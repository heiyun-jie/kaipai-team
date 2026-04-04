import argparse
from pathlib import Path

from ai_notification_http_bridge_inputs import (
    DEFAULT_AUTH_HEADER,
    DEFAULT_CALLBACK_PATH,
    DEFAULT_EXPECTED_PROVIDER_CODE,
    DEFAULT_SECRET_FILE,
)


DEFAULT_CALLBACK_BASE_URL = "http://101.43.57.62/api"


def render_content() -> str:
    return (
        "# Local AI notification HTTP bridge rollout inputs\n"
        f"AI_NOTIFICATION_HTTP_BRIDGE_EXPECTED_PROVIDER_CODE={DEFAULT_EXPECTED_PROVIDER_CODE}\n"
        "AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT=\n"
        f"AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_BASE_URL={DEFAULT_CALLBACK_BASE_URL}\n"
        f"AI_NOTIFICATION_HTTP_BRIDGE_CALLBACK_PATH={DEFAULT_CALLBACK_PATH}\n"
        f"AI_NOTIFICATION_HTTP_BRIDGE_AUTH_HEADER={DEFAULT_AUTH_HEADER}\n"
        "AI_NOTIFICATION_HTTP_BRIDGE_AUTH_TOKEN=\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize the local gitignored AI notification HTTP bridge secret file.")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    args = parser.parse_args()

    secret_file = Path(args.secret_file)
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    if not secret_file.exists():
        secret_file.write_text(render_content(), encoding="utf-8")
    print(secret_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
