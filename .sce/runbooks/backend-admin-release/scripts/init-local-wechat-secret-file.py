import argparse
import json
from pathlib import Path

from wechat_secret_inputs import DEFAULT_SECRET_FILE, validate_secret_value


ROOT = Path(__file__).resolve().parents[4]
PROJECT_CONFIG = ROOT / "kaipai-frontend" / "project.config.json"
PLACEHOLDER_SECRET = "replace-with-real-app-secret"


def read_project_appid() -> str:
    if not PROJECT_CONFIG.exists():
        return ""
    data = json.loads(PROJECT_CONFIG.read_text(encoding="utf-8-sig"))
    return str(data.get("appid") or "").strip()


def resolve_appid(explicit: str | None) -> str:
    app_id = (explicit or "").strip() or read_project_appid()
    issues = validate_secret_value("WECHAT_MINIAPP_APP_ID", app_id)
    if issues:
        raise RuntimeError(
            "cannot initialize local WeChat secret file because no valid appId is available; "
            f"issues={','.join(issues)}"
        )
    return app_id


def render_content(app_id: str, env_version: str) -> str:
    lines = [
        "# Local-only WeChat mini-program secrets for 00-29 sync pipeline",
        "# This file is gitignored. Fill the real appSecret before running the standard pipeline.",
        f"WECHAT_MINIAPP_APP_ID={app_id}",
        f"WECHAT_MINIAPP_APP_SECRET={PLACEHOLDER_SECRET}",
    ]
    if env_version:
        lines.append(f"WECHAT_MINIAPP_ENV_VERSION={env_version}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize the local gitignored WeChat secret file for the standard 00-29 pipeline.")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    parser.add_argument("--app-id")
    parser.add_argument("--env-version", default="release")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    secret_file = Path(args.secret_file).resolve()
    if secret_file.exists() and not args.force:
        raise RuntimeError(f"secret file already exists: {secret_file}")

    app_id = resolve_appid(args.app_id)
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    secret_file.write_text(render_content(app_id, args.env_version), encoding="utf-8")

    print(
        json.dumps(
            {
                "secret_file": str(secret_file),
                "app_id": app_id,
                "placeholder_secret_written": True,
                "next_step": "replace WECHAT_MINIAPP_APP_SECRET with the real secret, then run run-backend-wechat-config-sync-pipeline.py",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
