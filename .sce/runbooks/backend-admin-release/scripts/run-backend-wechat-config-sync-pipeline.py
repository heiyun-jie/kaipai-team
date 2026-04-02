import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
SCRIPTS_DIR = RUNBOOK_DIR / "scripts"
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "wechat-miniapp.env"
ENV_KEYS = ["WECHAT_MINIAPP_APP_ID", "WECHAT_MINIAPP_APP_SECRET"]


def parse_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def resolve_input_values(secret_file: Path) -> dict[str, str]:
    secret_values = parse_dotenv(secret_file)
    resolved: dict[str, str] = {}
    for key in ENV_KEYS:
        value = os.environ.get(key) or secret_values.get(key) or ""
        if value:
            resolved[key] = value
    return resolved


def run_python_script(script: Path, args: list[str], *, extra_env: dict[str, str] | None = None) -> dict[str, object]:
    command = [sys.executable, str(script), *args]
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        command,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    output = result.stdout.strip()
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"failed to parse JSON output from {script.name}: {output}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_record(
    *,
    release_id: str,
    operator: str,
    dry_run: bool,
    local_capture_path: Path,
    local_summary: dict[str, object],
    remote_capture_path: Path | None,
    remote_summary: dict[str, object] | None,
    compose_result: dict[str, object] | None,
    nacos_result: dict[str, object] | None,
    final_status: str,
    stop_reason: str,
) -> Path:
    record_path = RECORDS_DIR / f"{release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    lines = [
        "# 后端微信配置来源同步总控记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 配置批次号：`{release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 操作人：`{operator}`",
        f"- 范围：`backend-wechat-config-sync-pipeline`",
        f"- dry-run：`{'是' if dry_run else '否'}`",
        f"- 最终状态：`{final_status}`",
        f"- 中止/结束原因：`{stop_reason}`",
        "",
        "## 2. 固定执行顺序",
        "",
        "1. `read-local-wechat-config-inputs.py`",
        "2. `read-backend-wechat-config-precheck.py`",
        "3. `run-backend-compose-env-sync.py`",
        "4. `run-backend-nacos-config-sync.py`",
        "",
        "## 3. 本地输入检查",
        "",
        f"- 诊断目录：`{local_capture_path}`",
        f"- releaseReady：`{'是' if local_summary.get('releaseReady') else '否'}`",
        f"- project appId：`{((local_summary.get('projectConfig') or {}).get('appId') or '--')}`",
    ]

    if not local_summary.get("releaseReady"):
        lines.append("- 结论：当前本地没有成组 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，总控在第 1 步中止")

    if remote_capture_path and remote_summary:
        gate = remote_summary.get("gate") or {}
        lines.extend(
            [
                "",
                "## 4. 远端门禁预检查",
                "",
                f"- 诊断目录：`{remote_capture_path}`",
                f"- gate status：`{gate.get('status', '--')}`",
                f"- failing checks：`{', '.join(gate.get('failingChecks', [])) or '--'}`",
            ]
        )

    if compose_result:
        lines.extend(
            [
                "",
                "## 5. Compose 来源同步",
                "",
                f"- 记录路径：`{compose_result.get('record_path', '--')}`",
                f"- dry-run：`{'是' if compose_result.get('dry_run') else '否'}`",
            ]
        )

    if nacos_result:
        lines.extend(
            [
                "",
                "## 6. Nacos 配置同步",
                "",
                f"- 记录路径：`{nacos_result.get('record_path', '--')}`",
                f"- dry-run：`{'是' if nacos_result.get('dry_run') else '否'}`",
            ]
        )

    lines.extend(
        [
            "",
            "## 7. 下一步",
            "",
            "- 若总控已在本地输入检查中止，先取得合法 `appSecret` 输入，再重新执行本总控脚本",
            "- 若 compose / Nacos 已同步完成，后续仍必须执行标准 `backend-only` 发布 / 重建",
            "- 后续重建完成后，再重新执行 `read-backend-wechat-config-precheck.py` 验证运行时门禁",
        ]
    )

    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the fixed pipeline for backend WeChat config source sync: local input -> remote gate -> compose sync -> nacos sync.",
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
    parser.add_argument("--nacos-data-id", default="kaipai-backend-dev.yml")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    args = parser.parse_args()

    release_id = f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-backend-wechat-config-pipeline-{args.label}"
    local_label = f"{args.label}-local-input"
    remote_label = f"{args.label}-remote-gate"
    secret_file = Path(args.secret_file)

    base_forward_args: list[str] = []
    if args.host:
        base_forward_args.extend(["--host", args.host])
    if args.user:
        base_forward_args.extend(["--user", args.user])
    if args.identity_file:
        base_forward_args.extend(["--identity-file", args.identity_file])

    local_result = run_python_script(
        SCRIPTS_DIR / "read-local-wechat-config-inputs.py",
        ["--label", local_label, "--secret-file", str(secret_file)],
    )
    local_capture_path = Path(str(local_result["output_dir"]))
    local_summary = read_json(local_capture_path / "summary.json")
    resolved_inputs = resolve_input_values(secret_file)

    if not local_summary.get("releaseReady"):
        record_path = write_record(
            release_id=release_id,
            operator=args.operator,
            dry_run=args.dry_run,
            local_capture_path=local_capture_path,
            local_summary=local_summary,
            remote_capture_path=None,
            remote_summary=None,
            compose_result=None,
            nacos_result=None,
            final_status="blocked",
            stop_reason="local_input_missing",
        )
        print(
            json.dumps(
                {
                    "release_id": release_id,
                    "status": "blocked",
                    "stop_reason": "local_input_missing",
                    "local_input_capture": str(local_capture_path),
                    "record_path": str(record_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    extra_env = {key: value for key, value in resolved_inputs.items() if value}
    remote_args = ["--label", remote_label, "--no-fail-on-missing", *base_forward_args]
    if args.nacos_server_addr:
        remote_args.extend(["--nacos-server-addr", args.nacos_server_addr])
    if args.nacos_group:
        remote_args.extend(["--nacos-group", args.nacos_group])
    if args.nacos_namespace:
        remote_args.extend(["--nacos-namespace", args.nacos_namespace])
    remote_result = run_python_script(
        SCRIPTS_DIR / "read-backend-wechat-config-precheck.py",
        remote_args,
    )
    remote_capture_path = Path(str(remote_result["output_dir"]))
    remote_summary = read_json(remote_capture_path / "summary.json")

    compose_args = ["--label", args.label, "--operator", args.operator, "--from-local-env", "WECHAT_MINIAPP_APP_ID", "--from-local-env", "WECHAT_MINIAPP_APP_SECRET", *base_forward_args]
    nacos_args = ["--label", args.label, "--operator", args.operator, "--nacos-data-id", args.nacos_data_id, "--from-local-env", "WECHAT_MINIAPP_APP_ID", "--from-local-env", "WECHAT_MINIAPP_APP_SECRET", *base_forward_args]
    if args.nacos_server_addr:
        nacos_args.extend(["--nacos-server-addr", args.nacos_server_addr])
    if args.nacos_group:
        nacos_args.extend(["--nacos-group", args.nacos_group])
    if args.nacos_namespace:
        nacos_args.extend(["--nacos-namespace", args.nacos_namespace])
    if args.dry_run:
        compose_args.append("--dry-run")
        nacos_args.append("--dry-run")

    compose_result = run_python_script(SCRIPTS_DIR / "run-backend-compose-env-sync.py", compose_args, extra_env=extra_env)
    nacos_result = run_python_script(SCRIPTS_DIR / "run-backend-nacos-config-sync.py", nacos_args, extra_env=extra_env)

    record_path = write_record(
        release_id=release_id,
        operator=args.operator,
        dry_run=args.dry_run,
        local_capture_path=local_capture_path,
        local_summary=local_summary,
        remote_capture_path=remote_capture_path,
        remote_summary=remote_summary,
        compose_result=compose_result,
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
                "remote_gate_capture": str(remote_capture_path),
                "compose_record_path": compose_result.get("record_path"),
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
