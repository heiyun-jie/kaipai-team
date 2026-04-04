import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from ai_notification_secret_inputs import DEFAULT_SECRET_FILE, DEFAULT_SECRET_ENV_KEYS, resolve_secret_values


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
SCRIPTS_DIR = RUNBOOK_DIR / "scripts"
DEFAULT_NACOS_DATA_ID = "kaipai-backend-dev.yml"
DEFAULT_GREP = "kaipai\\.ai\\.resume\\.notification|AI_RESUME_NOTIFICATION"
NACOS_KEY_MAP = {
    "AI_RESUME_NOTIFICATION_ENABLED": "kaipai.ai.resume.notification.enabled",
    "AI_RESUME_NOTIFICATION_PROVIDER_CODE": "kaipai.ai.resume.notification.provider-code",
    "AI_RESUME_NOTIFICATION_CALLBACK_HEADER": "kaipai.ai.resume.notification.callback-header",
    "AI_RESUME_NOTIFICATION_CALLBACK_TOKEN": "kaipai.ai.resume.notification.callback-token",
}


def run_python_script(
    script: Path,
    args: list[str],
    *,
    extra_env: dict[str, str] | None = None,
    allowed_exit_codes: set[int] | None = None,
) -> tuple[int, dict[str, object]]:
    command = [sys.executable, str(script), *args]
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        command,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    output = result.stdout.strip()
    candidate: str | None = None
    match = re.search(r"(\{[\s\S]*\})\s*$", output)
    if match:
        candidate = match.group(1)
    try:
        parsed = json.loads(candidate) if candidate else None
    except json.JSONDecodeError as exc:
        parsed = None
    if parsed is None:
        capture_match = re.search(r"capture saved:\s*(.+)$", output, re.M)
        if capture_match:
            parsed = {"output_dir": capture_match.group(1).strip()}
    if parsed is None:
        raise RuntimeError(f"failed to parse script output from {script.name}: {output}")
    accepted_codes = allowed_exit_codes or {0}
    if result.returncode not in accepted_codes:
        raise RuntimeError(f"{script.name} exited with {result.returncode}: {output}")
    return result.returncode, parsed


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig").strip()


def normalize_remote_ai_summary(presence_summary: str, filtered_configs: str) -> list[str]:
    normalized: list[str] = []
    if filtered_configs.strip() == "### kaipai-backend-dev.yml\n[no matching lines]":
        normalized.append("kaipai-backend-dev.yml: no AI notification keys matched current grep")
    for raw_line in presence_summary.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "missing app-id" in line or "missing app-secret" in line:
            continue
        normalized.append(line)
    return normalized


def write_record(
    *,
    release_id: str,
    operator: str,
    dry_run: bool,
    local_capture_path: Path,
    local_summary: dict[str, object],
    remote_capture_path: Path,
    nacos_result: dict[str, object] | None,
    final_status: str,
    stop_reason: str,
) -> Path:
    record_path = RECORDS_DIR / f"{release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    lines = [
        "# 后端 AI 通知配置来源同步总控记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 配置批次号：`{release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 操作人：`{operator}`",
        f"- 范围：`backend-ai-notification-config-sync-pipeline`",
        f"- dry-run：`{'是' if dry_run else '否'}`",
        f"- 最终状态：`{final_status}`",
        f"- 中止/结束原因：`{stop_reason}`",
        "",
        "## 2. 固定执行顺序",
        "",
        "1. `read-local-ai-notification-config-inputs.py`",
        "2. `read-backend-nacos-config.py`",
        "3. `run-backend-nacos-config-sync.py`",
        "",
        "## 3. 本地输入检查",
        "",
        f"- 诊断目录：`{local_capture_path}`",
        f"- releaseReady：`{'是' if local_summary.get('releaseReady') else '否'}`",
    ]
    validation = local_summary.get("validation")
    if isinstance(validation, dict):
        for key in DEFAULT_SECRET_ENV_KEYS:
            issues = validation.get(key) or []
            lines.append(f"- `{key}`：`{', '.join(issues) if issues else 'passed'}`")
    if not local_summary.get("releaseReady"):
        lines.append("- 结论：当前本地 AI 通知配置输入未就绪，总控在第 1 步中止")
        lines.append(f"- 建议动作：先把真实 callback token 写入 `{DEFAULT_SECRET_FILE}`，再重新执行本总控")

    lines.extend(
        [
            "",
            "## 4. 远端 Nacos 预检查",
            "",
            f"- 诊断目录：`{remote_capture_path}`",
            "- 目的：同步前固定目标 dataId 当前原文与目标键存在性，不再手工进控制台比对",
        ]
    )
    remote_presence_summary = read_text_if_exists(remote_capture_path / "nacos-config-presence-summary.txt")
    remote_filtered_configs = read_text_if_exists(remote_capture_path / "nacos-filtered-configs.txt")
    normalized_remote_summary = normalize_remote_ai_summary(remote_presence_summary, remote_filtered_configs)
    if normalized_remote_summary:
        lines.extend(["- 预检查摘要："])
        for line in normalized_remote_summary:
            lines.append(f"  {line}")
    if remote_filtered_configs:
        filtered_status = remote_filtered_configs if remote_filtered_configs != "### kaipai-backend-dev.yml\n[no matching lines]" else "[no matching lines]"
        lines.append(f"- 过滤回读：`{filtered_status}`")

    if nacos_result:
        lines.extend(
            [
                "",
                "## 5. Nacos 配置同步",
                "",
                f"- 记录路径：`{nacos_result.get('record_path', '--')}`",
                f"- dry-run：`{'是' if nacos_result.get('dry_run') else '否'}`",
            ]
        )

    lines.extend(
        [
            "",
            "## 6. 下一步",
            "",
            "- 若当前仍是 `local_input_not_ready`，先修正本地 secret 文件，再重新执行本总控",
            "- Nacos 同步完成后，仍必须执行标准 `backend-only` 发布 / 重建",
            "- 重建后再执行 `run-ai-resume-notification-foundation-validation.py`，产出真实 dispatch / callback 样本",
        ]
    )

    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the fixed pipeline for backend AI notification config sync: local input -> remote nacos precheck -> nacos sync."
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--operator", default="codex")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--host")
    parser.add_argument("--user")
    parser.add_argument("--identity-file")
    parser.add_argument("--nacos-server-addr")
    parser.add_argument("--nacos-group")
    parser.add_argument("--nacos-namespace")
    parser.add_argument("--nacos-data-id", default=DEFAULT_NACOS_DATA_ID)
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    args = parser.parse_args()

    release_id = f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-backend-ai-notification-config-pipeline-{args.label}"
    secret_file = Path(args.secret_file)
    base_forward_args: list[str] = []
    if args.host:
        base_forward_args.extend(["--host", args.host])
    if args.user:
        base_forward_args.extend(["--user", args.user])
    if args.identity_file:
        base_forward_args.extend(["--identity-file", args.identity_file])

    _, local_result = run_python_script(
        SCRIPTS_DIR / "read-local-ai-notification-config-inputs.py",
        ["--label", f"{args.label}-local-input", "--secret-file", str(secret_file)],
        allowed_exit_codes={0, 2},
    )
    local_capture_path = Path(str(local_result["output_dir"]))
    local_summary = read_json(local_capture_path / "summary.json")
    resolved_inputs = resolve_secret_values(secret_file, list(DEFAULT_SECRET_ENV_KEYS))

    remote_args = [
        "--label",
        f"{args.label}-remote-nacos",
        "--grep",
        DEFAULT_GREP,
        "--nacos-data-id",
        args.nacos_data_id,
        *base_forward_args,
    ]
    if args.nacos_server_addr:
        remote_args.extend(["--nacos-server-addr", args.nacos_server_addr])
    if args.nacos_group:
        remote_args.extend(["--nacos-group", args.nacos_group])
    if args.nacos_namespace:
        remote_args.extend(["--nacos-namespace", args.nacos_namespace])
    _, remote_result = run_python_script(SCRIPTS_DIR / "read-backend-nacos-config.py", remote_args)
    remote_capture_path = Path(str(remote_result["output_dir"]))

    if not local_summary.get("releaseReady"):
        record_path = write_record(
            release_id=release_id,
            operator=args.operator,
            dry_run=args.dry_run,
            local_capture_path=local_capture_path,
            local_summary=local_summary,
            remote_capture_path=remote_capture_path,
            nacos_result=None,
            final_status="blocked",
            stop_reason="local_input_not_ready",
        )
        print(
            json.dumps(
                {
                    "release_id": release_id,
                    "status": "blocked",
                    "stop_reason": "local_input_not_ready",
                    "local_input_capture": str(local_capture_path),
                    "remote_nacos_capture": str(remote_capture_path),
                    "record_path": str(record_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    extra_env = {key: value for key, value in resolved_inputs.items() if value}
    nacos_args = [
        "--label",
        args.label,
        "--operator",
        args.operator,
        "--nacos-data-id",
        args.nacos_data_id,
        "--grep",
        DEFAULT_GREP,
        *base_forward_args,
    ]
    if args.nacos_server_addr:
        nacos_args.extend(["--nacos-server-addr", args.nacos_server_addr])
    if args.nacos_group:
        nacos_args.extend(["--nacos-group", args.nacos_group])
    if args.nacos_namespace:
        nacos_args.extend(["--nacos-namespace", args.nacos_namespace])
    for env_key, nacos_key in NACOS_KEY_MAP.items():
        nacos_args.extend(["--set", f"{nacos_key}={resolved_inputs[env_key]}"])
    if args.dry_run:
        nacos_args.append("--dry-run")

    _, nacos_result = run_python_script(
        SCRIPTS_DIR / "run-backend-nacos-config-sync.py",
        nacos_args,
        extra_env=extra_env,
    )
    record_path = write_record(
        release_id=release_id,
        operator=args.operator,
        dry_run=args.dry_run,
        local_capture_path=local_capture_path,
        local_summary=local_summary,
        remote_capture_path=remote_capture_path,
        nacos_result=nacos_result,
        final_status="completed",
        stop_reason="pipeline_finished",
    )
    print(
        json.dumps(
            {
                "release_id": release_id,
                "status": "completed",
                "local_input_capture": str(local_capture_path),
                "remote_nacos_capture": str(remote_capture_path),
                "nacos_record_path": nacos_result.get("record_path"),
                "record_path": str(record_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
