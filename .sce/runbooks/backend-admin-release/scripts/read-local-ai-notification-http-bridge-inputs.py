import argparse
import json
from datetime import datetime
from pathlib import Path

from ai_notification_http_bridge_inputs import (
    DEFAULT_SECRET_ENV_KEYS,
    DEFAULT_SECRET_FILE,
    build_derived_runtime_values,
    parse_dotenv,
    resolve_secret_values,
    validate_required_secret_values,
)


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
DIAGNOSTICS_DIR = RUNBOOK_DIR / "records" / "diagnostics"


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "local-ai-notification-http-bridge-inputs"


def redact(key: str, value: str | None) -> str:
    if not value:
        return ""
    return "[REDACTED]" if key.endswith("TOKEN") else value


def main() -> int:
    parser = argparse.ArgumentParser(description="Read local AI notification HTTP bridge inputs and validate readiness.")
    parser.add_argument("--label", default="local-ai-notification-http-bridge-inputs")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    args = parser.parse_args()

    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    output_dir = DIAGNOSTICS_DIR / capture_id
    output_dir.mkdir(parents=True, exist_ok=True)

    secret_file = Path(args.secret_file)
    dotenv_values = parse_dotenv(secret_file)
    resolved = resolve_secret_values(secret_file, list(DEFAULT_SECRET_ENV_KEYS))
    validation = validate_required_secret_values(resolved)
    derived = build_derived_runtime_values(resolved)
    release_ready = all(not issues for issues in validation.values()) and bool(derived.get("AI_RESUME_NOTIFICATION_CALLBACK_URL"))

    summary = {
        "captureId": capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "secretFile": str(secret_file),
        "secretFileExists": secret_file.exists(),
        "resolvedValues": {key: redact(key, resolved.get(key)) for key in DEFAULT_SECRET_ENV_KEYS},
        "dotenvValues": {key: redact(key, dotenv_values.get(key)) for key in DEFAULT_SECRET_ENV_KEYS},
        "derivedRuntimeValues": {key: redact(key, derived.get(key)) for key in sorted(derived)},
        "validation": validation,
        "releaseReady": release_ready,
    }

    lines = [
        "# 本地 AI 通知 HTTP Bridge 输入检查",
        "",
        f"- Capture ID: `{capture_id}`",
        f"- Secret File: `{secret_file}`",
        f"- Exists: `{'yes' if secret_file.exists() else 'no'}`",
        f"- Release Ready: `{'yes' if release_ready else 'no'}`",
        "",
        "## Resolved Inputs",
        "",
    ]
    for key in DEFAULT_SECRET_ENV_KEYS:
        lines.append(f"- `{key}`: `{redact(key, resolved.get(key)) or '--'}`")
    lines.extend(["", "## Derived Runtime Values", ""])
    for key in sorted(derived):
        lines.append(f"- `{key}`: `{redact(key, derived.get(key)) or '--'}`")
    lines.extend(["", "## Validation", ""])
    for key in DEFAULT_SECRET_ENV_KEYS:
        issues = validation.get(key) or []
        lines.append(f"- `{key}`: `{', '.join(issues) if issues else 'passed'}`")
    if not release_ready:
        lines.extend(
            [
                "",
                "## Conclusion",
                "",
                "- 当前没有可用的 bridge endpoint / callback base url 输入，不能把 `provider-code=http` 推进到目标环境验证",
            ]
        )

    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "capture_id": capture_id,
                "output_dir": str(output_dir),
                "releaseReady": release_ready,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if release_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
