#!/usr/bin/env python3
"""
Human Gate для Linear.

PreToolUse hook на matcher "mcp__linear__save_issue". Кожен виклик цього
інструменту (створення нового issue АБО оновлення статусу існуючого)
примусово переводиться в permissionDecision "ask" — незалежно від того, чи
skill linear-task-manager вже показав Markdown-версію issue в чаті.

Це навмисно завжди "ask" без додаткової логіки: сам факт виклику
save_issue означає запис у зовнішній трекер, а це завжди критична точка
за визначенням Human Gate.

ВАЖЛИВО про формат виводу: PreToolUse читає ВИКЛЮЧНО
`hookSpecificOutput.permissionDecision` зі значеннями
allow / deny / ask / defer. Значення "ask_user" не існує — до версії 0.6.1
цей hook віддавав саме його, тому вивід тихо ігнорувався і гейт фактично
не спрацьовував.
"""
import json
import sys


def main() -> None:
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        pass

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": (
                        "Human Gate: Linear:save_issue створює або змінює запис у "
                        "зовнішньому трекері. Потрібне явне 'так' перед виконанням."
                    ),
                }
            }
        )
    )


if __name__ == "__main__":
    main()
