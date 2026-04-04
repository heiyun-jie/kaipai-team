import json
from pathlib import Path

from ai_notification_secret_inputs import DEFAULT_CALLBACK_HEADER, DEFAULT_SECRET_FILE


ROOT = Path(__file__).resolve().parents[4]


def main() -> int:
    secret_file = DEFAULT_SECRET_FILE
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    created = False
    if not secret_file.exists():
        secret_file.write_text(
            "\n".join(
                [
                    "# Local AI resume notification foundation inputs",
                    "AI_RESUME_NOTIFICATION_ENABLED=true",
                    "AI_RESUME_NOTIFICATION_PROVIDER_CODE=manual",
                    f"AI_RESUME_NOTIFICATION_CALLBACK_HEADER={DEFAULT_CALLBACK_HEADER}",
                    "AI_RESUME_NOTIFICATION_CALLBACK_TOKEN=replace-with-real-notification-callback-token",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        created = True

    print(
        json.dumps(
            {
                "secret_file": str(secret_file),
                "created": created,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
