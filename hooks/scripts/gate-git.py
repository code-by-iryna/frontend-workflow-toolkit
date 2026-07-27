#!/usr/bin/env python3
"""
Human Gate для Bash-команд.

Це PreToolUse hook на matcher "Bash". Він перевіряє команду, яку Claude
хоче виконати, і якщо вона виходить за межі "лабораторії" (тобто
торкається git commit / git push / merge / створення PR) —
примусово повертає permissionDecision "ask", навіть якщо відповідний skill
(git-workflow) вже мав текстову інструкцію ніколи такого не робити.

Це другий, технічний шар захисту на додачу до текстового — hook
не залежить від того, чи Claude "згадає" прочитати інструкцію skill'а.
Все інше (npm, git status, git diff, git log, cat, ls тощо) віддається
у звичайний permission flow через "defer", щоб не заважати Auto Mode.

ВАЖЛИВО про формат виводу: PreToolUse читає ВИКЛЮЧНО
`hookSpecificOutput.permissionDecision` зі значеннями
allow / deny / ask / defer. Поле верхнього рівня "decision" для цієї події
не використовується, а значень "ask_user" чи "approve" не існує — такий
вивід тихо ігнорується, і hook відпрацьовує вхолосту (саме це й було до
версії 0.6.1: гейт ніколи фактично не блокував).

Для гілки пропуску свідомо використано "defer", а НЕ "allow": "allow" дав
би безумовне автосхвалення кожній bash-команді в обхід системи дозволів.
"""
import json
import re
import sys

BLOCKED_PATTERNS = [
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgh\s+pr\s+create\b",
    r"\bgh\s+pr\s+merge\b",
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    command = str(payload.get("tool_input", {}).get("command", ""))

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command):
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "ask",
                            "permissionDecisionReason": (
                                "Human Gate: команда виходить за межі 'лабораторії' "
                                f"(git commit/push/merge/PR) — '{command.strip()}'. "
                                "Потрібне явне підтвердження перед виконанням."
                            ),
                        }
                    }
                )
            )
            return

    # Не наша зона відповідальності — віддаємо рішення звичайному
    # permission flow. Саме "defer", а не "allow" (див. docstring).
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "defer",
                }
            }
        )
    )


if __name__ == "__main__":
    main()
