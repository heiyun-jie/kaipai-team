import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from wechat_secret_inputs import DEFAULT_SECRET_FILE, parse_dotenv


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
DIAGNOSTICS_DIR = RUNBOOK_DIR / "records" / "diagnostics"

DEFAULT_LABEL = "local-wechat-config-inputs"
ENV_KEYS = ["WECHAT_MINIAPP_APP_ID", "WECHAT_MINIAPP_APP_SECRET"]
DOTENV_FILES = [
    ROOT / "kaipai-frontend" / ".env",
    ROOT / "kaipai-frontend" / ".env.example",
    ROOT / "kaipai-admin" / ".env.development",
]
PROJECT_CONFIG = ROOT / "kaipai-frontend" / "project.config.json"


@dataclass
class LocalInputContext:
    capture_id: str
    label: str
    output_dir: Path
    secret_file: Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or DEFAULT_LABEL


def mask_value(key: str, value: str | None) -> str:
    if not value:
        return "--"
    if "SECRET" in key.upper():
        if len(value) <= 4:
            return "[REDACTED]"
        return f"{value[:2]}***{value[-2:]}"
    return value


def read_project_appid() -> str | None:
    if not PROJECT_CONFIG.exists():
        return None
    data = json.loads(PROJECT_CONFIG.read_text(encoding="utf-8-sig"))
    return data.get("appid") or None


def resolve_inputs(env_values: dict[str, str | None], secret_values: dict[str, str]) -> tuple[dict[str, str | None], dict[str, str]]:
    resolved: dict[str, str | None] = {}
    sources: dict[str, str] = {}
    for key in ENV_KEYS:
        env_value = env_values.get(key)
        if env_value:
            resolved[key] = env_value
            sources[key] = "local-env"
            continue
        secret_value = secret_values.get(key)
        if secret_value:
            resolved[key] = secret_value
            sources[key] = "secret-file"
            continue
        resolved[key] = None
        sources[key] = "missing"
    return resolved, sources


def build_summary(context: LocalInputContext) -> dict[str, object]:
    env_values = {key: os.environ.get(key) for key in ENV_KEYS}
    dotenv_values = {str(path.relative_to(ROOT)): parse_dotenv(path) for path in DOTENV_FILES}
    secret_values = parse_dotenv(context.secret_file)
    project_appid = read_project_appid()
    resolved_inputs, resolved_sources = resolve_inputs(env_values, secret_values)

    dotenv_hits: dict[str, dict[str, str]] = {}
    for relative_path, values in dotenv_values.items():
        matched = {key: values.get(key, "") for key in ENV_KEYS if values.get(key)}
        if matched:
            dotenv_hits[relative_path] = matched

    release_ready = bool(resolved_inputs.get("WECHAT_MINIAPP_APP_ID") and resolved_inputs.get("WECHAT_MINIAPP_APP_SECRET"))
    secret_found_anywhere = bool(resolved_inputs.get("WECHAT_MINIAPP_APP_SECRET")) or any(values.get("WECHAT_MINIAPP_APP_SECRET") for values in dotenv_values.values())

    return {
        "captureId": context.capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "label": context.label,
        "projectConfig": {
            "path": str(PROJECT_CONFIG.relative_to(ROOT)),
            "appId": project_appid,
        },
        "localEnv": {
            key: {
                "present": bool(env_values.get(key)),
                "valuePreview": mask_value(key, env_values.get(key)),
            }
            for key in ENV_KEYS
        },
        "secretFile": {
            "path": str(context.secret_file.relative_to(ROOT)),
            "exists": context.secret_file.exists(),
            "values": {
                key: {
                    "present": bool(secret_values.get(key)),
                    "valuePreview": mask_value(key, secret_values.get(key)),
                }
                for key in ENV_KEYS
            },
        },
        "resolvedInputs": {
            key: {
                "present": bool(resolved_inputs.get(key)),
                "source": resolved_sources.get(key, "missing"),
                "valuePreview": mask_value(key, resolved_inputs.get(key)),
            }
            for key in ENV_KEYS
        },
        "dotenvFiles": {
            relative_path: {
                key: {
                    "present": bool(values.get(key)),
                    "valuePreview": mask_value(key, values.get(key)),
                }
                for key in ENV_KEYS
            }
            for relative_path, values in dotenv_values.items()
        },
        "dotenvHits": dotenv_hits,
        "releaseReady": release_ready,
        "secretFoundAnywhere": secret_found_anywhere,
    }


def render_markdown(summary: dict[str, object]) -> str:
    local_env = summary["localEnv"]  # type: ignore[index]
    secret_file = summary["secretFile"]  # type: ignore[index]
    resolved_inputs = summary["resolvedInputs"]  # type: ignore[index]
    dotenv_files = summary["dotenvFiles"]  # type: ignore[index]
    project_config = summary["projectConfig"]  # type: ignore[index]
    lines = [
        "# 本地微信配置输入检查",
        "",
        f"- Capture ID: `{summary['captureId']}`",
        f"- Label: `{summary['label']}`",
        f"- Project appId: `{project_config['appId'] or '--'}`",
        f"- Release Ready: `{'yes' if summary['releaseReady'] else 'no'}`",
        "",
        "## Local Env",
        "",
    ]
    for key, detail in local_env.items():  # type: ignore[union-attr]
        lines.append(f"- `{key}` present: `{'yes' if detail['present'] else 'no'}`")
        lines.append(f"- `{key}` preview: `{detail['valuePreview']}`")

    lines.extend(["", "## Secret File", "", f"- path: `{secret_file['path']}`", f"- exists: `{'yes' if secret_file['exists'] else 'no'}`"])
    for key, detail in secret_file["values"].items():
        lines.append(f"- `{key}` present: `{'yes' if detail['present'] else 'no'}`")
        lines.append(f"- `{key}` preview: `{detail['valuePreview']}`")

    lines.extend(["", "## Resolved Inputs", ""])
    for key, detail in resolved_inputs.items():
        lines.append(f"- `{key}` present: `{'yes' if detail['present'] else 'no'}`")
        lines.append(f"- `{key}` source: `{detail['source']}`")
        lines.append(f"- `{key}` preview: `{detail['valuePreview']}`")

    lines.extend(["", "## Dotenv Candidates", ""])
    for relative_path, values in dotenv_files.items():  # type: ignore[union-attr]
        lines.append(f"- `{relative_path}`")
        for key, detail in values.items():
            lines.append(f"  - `{key}` present: `{'yes' if detail['present'] else 'no'}`")
            lines.append(f"  - `{key}` preview: `{detail['valuePreview']}`")

    lines.extend(["", "## Conclusion", ""])
    if summary["releaseReady"]:
        lines.append("- current result: local machine already resolves both appId and appSecret, can proceed to standard compose/Nacos sync")
    else:
        lines.append("- current result: local machine still does not resolve a complete `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` input pair")
        if project_config["appId"]:
            lines.append("- extra fact: frontend project config already fixes the mini-program appId, but this is not enough to open the backend WeChat gate")
        lines.append("- next step: obtain the legal appSecret source first, then write it to the local secret file or local env and continue `00-29` sync flow")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect local WeChat config candidates before running standard remote sync steps.")
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    args = parser.parse_args()

    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    context = LocalInputContext(
        capture_id=capture_id,
        label=args.label,
        output_dir=DIAGNOSTICS_DIR / capture_id,
        secret_file=Path(args.secret_file),
    )
    ensure_dir(context.output_dir)
    summary = build_summary(context)
    write_text(context.output_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(context.output_dir / "summary.md", render_markdown(summary))
    print(json.dumps({"capture_id": context.capture_id, "output_dir": str(context.output_dir)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
