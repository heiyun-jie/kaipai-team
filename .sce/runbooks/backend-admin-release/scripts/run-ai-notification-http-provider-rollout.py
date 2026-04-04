import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from ai_notification_http_bridge_inputs import (
    DEFAULT_SECRET_ENV_KEYS as DEFAULT_BRIDGE_KEYS,
    DEFAULT_SECRET_FILE as DEFAULT_BRIDGE_SECRET_FILE,
    build_derived_runtime_values,
    resolve_secret_values as resolve_bridge_secret_values,
)
from ai_notification_secret_inputs import (
    DEFAULT_SECRET_ENV_KEYS as DEFAULT_AI_NOTIFICATION_KEYS,
    DEFAULT_SECRET_FILE as DEFAULT_AI_NOTIFICATION_SECRET_FILE,
    resolve_secret_values as resolve_ai_notification_secret_values,
)


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
SCRIPTS_DIR = RUNBOOK_DIR / "scripts"
AI_EXECUTION_DIR = ROOT / ".sce" / "specs" / "00-28-architecture-driven-delivery-governance" / "execution" / "ai-resume"
AI_SAMPLE_ROOT = AI_EXECUTION_DIR / "samples"


def run_python_script(
    script: Path,
    args: list[str],
    *,
    extra_env: dict[str, str] | None = None,
    allowed_exit_codes: set[int] | None = None,
) -> tuple[int, dict[str, object], str]:
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
    parsed = extract_last_json_object(output)
    if parsed is None:
        raise RuntimeError(f"failed to parse script output from {script.name}: {output}")
    accepted_codes = allowed_exit_codes or {0}
    if result.returncode not in accepted_codes:
        raise RuntimeError(f"{script.name} exited with {result.returncode}: {output}")
    return result.returncode, parsed, output


def extract_last_json_object(output: str) -> dict[str, object] | None:
    for start in [match.start() for match in re.finditer(r"\{", output)][::-1]:
        candidate = output[start:].strip()
        decoder = json.JSONDecoder()
        try:
            parsed, end = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            trailing = candidate[end:].strip()
            if not trailing or trailing.startswith("["):
                return parsed
    return None


def run_command(
    command: list[str],
    *,
    extra_env: dict[str, str] | None = None,
    allowed_exit_codes: set[int] | None = None,
) -> tuple[int, str]:
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
    accepted_codes = allowed_exit_codes or {0}
    if result.returncode not in accepted_codes:
        raise RuntimeError(f"command exited with {result.returncode}: {' '.join(command)}\n{result.stdout}")
    return result.returncode, result.stdout.strip()


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig").strip()


def find_latest_sample_dir(label: str, started_at: datetime) -> Path | None:
    if not AI_SAMPLE_ROOT.exists():
        return None
    suffix = f"-{label}"
    candidates = [
        path
        for path in AI_SAMPLE_ROOT.iterdir()
        if path.is_dir() and path.name.endswith(suffix) and datetime.fromtimestamp(path.stat().st_mtime) >= started_at
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0]


def write_record(
    *,
    release_id: str,
    operator: str,
    dry_run: bool,
    bridge_capture_path: Path,
    bridge_summary: dict[str, object],
    ai_pipeline_result: dict[str, object] | None,
    backend_release_result: dict[str, object] | None,
    validation_exit_code: int | None,
    validation_sample_path: Path | None,
    final_status: str,
    stop_reason: str,
) -> Path:
    record_path = RECORDS_DIR / f"{release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    lines = [
        "# AI 通知 HTTP Provider 总控记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 操作人：`{operator}`",
        f"- 范围：`provider=http rollout`",
        f"- dry-run：`{'是' if dry_run else '否'}`",
        f"- 最终状态：`{final_status}`",
        f"- 中止/结束原因：`{stop_reason}`",
        "",
        "## 2. 固定执行顺序",
        "",
        "1. `read-local-ai-notification-http-bridge-inputs.py`",
        "2. `run-backend-ai-notification-config-sync-pipeline.py`",
        "3. `run-backend-only-release.py`",
        "4. `run-ai-resume-notification-foundation-validation.py`",
        "",
        "## 3. Bridge 输入门禁",
        "",
        f"- 诊断目录：`{bridge_capture_path}`",
        f"- releaseReady：`{'是' if bridge_summary.get('releaseReady') else '否'}`",
    ]

    derived = bridge_summary.get("derivedRuntimeValues")
    if isinstance(derived, dict):
        for key in sorted(derived):
            lines.append(f"- `{key}`：`{derived.get(key) or '--'}`")

    if not bridge_summary.get("releaseReady"):
        lines.extend(
            [
                "- 结论：当前没有真实 bridge endpoint/回调地址输入，本轮按标准 blocked 收口，不继续写 Nacos 或重建后端",
                "",
                "## 4. 下一步",
                "",
                "- 先通过 `init-local-ai-notification-http-bridge-secret-file.py` 初始化本地 gitignored 输入文件",
                "- 再把真实 `AI_NOTIFICATION_HTTP_BRIDGE_PUBLIC_ENDPOINT` 写入 `.sce/config/local-secrets/ai-notification-http-bridge.env`",
                "- 然后重新执行本总控脚本",
            ]
        )
        record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return record_path

    lines.extend(["", "## 4. AI 通知配置总控", ""])
    if ai_pipeline_result:
        lines.append(f"- 记录路径：`{ai_pipeline_result.get('record_path') or '--'}`")
        lines.append(f"- 本地输入诊断：`{ai_pipeline_result.get('local_input_capture') or '--'}`")
        lines.append(f"- 远端 Nacos 预检查：`{ai_pipeline_result.get('remote_nacos_capture') or '--'}`")
        if ai_pipeline_result.get("nacos_record_path"):
            lines.append(f"- Nacos 同步记录：`{ai_pipeline_result.get('nacos_record_path')}`")

    lines.extend(["", "## 5. backend-only", ""])
    if dry_run:
        lines.append("- dry-run 本轮不执行 `backend-only` 与通知样本验证，只固化 bridge 输入和 Nacos 总控路径")
    elif backend_release_result:
        lines.append(f"- 发布记录：`{backend_release_result.get('record_path') or '--'}`")
        lines.append(f"- 本地 jar SHA256：`{backend_release_result.get('local_jar_sha') or '--'}`")
        lines.append(f"- `/api/v3/api-docs`：`{backend_release_result.get('public_docs_status')}`")
        lines.append(f"- `/api/admin/auth/login`：`{backend_release_result.get('public_login_status')}`")

    lines.extend(["", "## 6. 真实通知样本", ""])
    if dry_run:
        lines.append("- dry-run 未执行 `run-ai-resume-notification-foundation-validation.py`")
    else:
        lines.append(f"- 验证脚本退出码：`{validation_exit_code}`")
        lines.append(f"- 样本目录：`{validation_sample_path or '--'}`")

    lines.extend(["", "## 7. 下一步", ""])
    if dry_run:
        lines.append("- 确认 bridge endpoint 已实际可访问后，去掉 `--dry-run` 重新执行本总控")
    elif validation_exit_code == 0:
        lines.append("- 当前已完成 `provider=http` 的标准总控与真实样本验证；后续只需补真实 vendor/bridge 变更时复用同一路径")
    else:
        lines.append("- 若样本失败，先阅读对应 sample `summary.md` 和发布记录，再决定是桥接服务问题、Nacos 漂移还是运行时数据问题")

    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the fixed provider=http rollout pipeline: bridge input -> ai notification config sync -> backend-only -> validation."
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--operator", default="codex")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--host")
    parser.add_argument("--user")
    parser.add_argument("--identity-file")
    parser.add_argument("--java-home")
    parser.add_argument("--ai-secret-file", default=str(DEFAULT_AI_NOTIFICATION_SECRET_FILE))
    parser.add_argument("--bridge-secret-file", default=str(DEFAULT_BRIDGE_SECRET_FILE))
    parser.add_argument(
        "--overlay-path",
        action="append",
        default=[],
        help="server-relative file/dir passed through to run-backend-only-release.py when kaipaile-server worktree is dirty; repeatable",
    )
    args = parser.parse_args()

    release_id = f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-backend-ai-notification-http-provider-rollout-{args.label}"
    ai_secret_file = Path(args.ai_secret_file)
    bridge_secret_file = Path(args.bridge_secret_file)

    base_forward_args: list[str] = []
    if args.host:
        base_forward_args.extend(["--host", args.host])
    if args.user:
        base_forward_args.extend(["--user", args.user])
    if args.identity_file:
        base_forward_args.extend(["--identity-file", args.identity_file])

    _, bridge_result, _ = run_python_script(
        SCRIPTS_DIR / "read-local-ai-notification-http-bridge-inputs.py",
        ["--label", f"{args.label}-bridge-input", "--secret-file", str(bridge_secret_file)],
        allowed_exit_codes={0, 2},
    )
    bridge_capture_path = Path(str(bridge_result["output_dir"]))
    bridge_summary = read_json(bridge_capture_path / "summary.json")
    if not bridge_summary.get("releaseReady"):
        record_path = write_record(
            release_id=release_id,
            operator=args.operator,
            dry_run=args.dry_run,
            bridge_capture_path=bridge_capture_path,
            bridge_summary=bridge_summary,
            ai_pipeline_result=None,
            backend_release_result=None,
            validation_exit_code=None,
            validation_sample_path=None,
            final_status="blocked",
            stop_reason="bridge_input_not_ready",
        )
        print(
            json.dumps(
                {
                    "release_id": release_id,
                    "status": "blocked",
                    "stop_reason": "bridge_input_not_ready",
                    "bridge_input_capture": str(bridge_capture_path),
                    "record_path": str(record_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    ai_values = resolve_ai_notification_secret_values(ai_secret_file, list(DEFAULT_AI_NOTIFICATION_KEYS))
    bridge_values = resolve_bridge_secret_values(bridge_secret_file, list(DEFAULT_BRIDGE_KEYS))
    rollout_env = {}
    rollout_env.update({key: value for key, value in ai_values.items() if value})
    rollout_env.update({key: value for key, value in bridge_values.items() if value})
    rollout_env.update(build_derived_runtime_values(bridge_values))
    rollout_env["AI_RESUME_NOTIFICATION_PROVIDER_CODE"] = "http"
    rollout_env["AI_NOTIFICATION_PROVIDER_CODE"] = "http"
    if ai_values.get("AI_RESUME_NOTIFICATION_CALLBACK_HEADER"):
        rollout_env["AI_NOTIFICATION_CALLBACK_HEADER"] = ai_values["AI_RESUME_NOTIFICATION_CALLBACK_HEADER"]
    if ai_values.get("AI_RESUME_NOTIFICATION_CALLBACK_TOKEN"):
        rollout_env["AI_NOTIFICATION_CALLBACK_TOKEN"] = ai_values["AI_RESUME_NOTIFICATION_CALLBACK_TOKEN"]

    _, ai_pipeline_result, _ = run_python_script(
        SCRIPTS_DIR / "run-backend-ai-notification-config-sync-pipeline.py",
        [
            "--label",
            args.label,
            "--operator",
            args.operator,
            "--secret-file",
            str(ai_secret_file),
            *base_forward_args,
            *(["--dry-run"] if args.dry_run else []),
        ],
        extra_env=rollout_env,
        allowed_exit_codes={0, 2},
    )
    if ai_pipeline_result.get("status") == "blocked":
        record_path = write_record(
            release_id=release_id,
            operator=args.operator,
            dry_run=args.dry_run,
            bridge_capture_path=bridge_capture_path,
            bridge_summary=bridge_summary,
            ai_pipeline_result=ai_pipeline_result,
            backend_release_result=None,
            validation_exit_code=None,
            validation_sample_path=None,
            final_status="blocked",
            stop_reason=str(ai_pipeline_result.get("stop_reason") or "ai_notification_config_blocked"),
        )
        print(
            json.dumps(
                {
                    "release_id": release_id,
                    "status": "blocked",
                    "stop_reason": ai_pipeline_result.get("stop_reason"),
                    "bridge_input_capture": str(bridge_capture_path),
                    "record_path": str(record_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    if args.dry_run:
        record_path = write_record(
            release_id=release_id,
            operator=args.operator,
            dry_run=True,
            bridge_capture_path=bridge_capture_path,
            bridge_summary=bridge_summary,
            ai_pipeline_result=ai_pipeline_result,
            backend_release_result=None,
            validation_exit_code=None,
            validation_sample_path=None,
            final_status="dry-run-completed",
            stop_reason="dry_run_finished",
        )
        print(
            json.dumps(
                {
                    "release_id": release_id,
                    "status": "dry-run-completed",
                    "bridge_input_capture": str(bridge_capture_path),
                    "record_path": str(record_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    _, backend_release_result, _ = run_python_script(
        SCRIPTS_DIR / "run-backend-only-release.py",
        [
            "--label",
            args.label,
            "--operator",
            args.operator,
            *base_forward_args,
            *(["--java-home", args.java_home] if args.java_home else []),
            *sum([["--overlay-path", item] for item in args.overlay_path], []),
        ],
        extra_env=rollout_env,
    )

    validation_started_at = datetime.now()
    validation_exit_code, _ = run_command(
        [sys.executable, str(AI_EXECUTION_DIR / "run-ai-resume-notification-foundation-validation.py"), args.label],
        extra_env=rollout_env,
        allowed_exit_codes={0, 1},
    )
    validation_sample_path = find_latest_sample_dir(args.label, validation_started_at)

    final_status = "completed" if validation_exit_code == 0 else "validation_failed"
    record_path = write_record(
        release_id=release_id,
        operator=args.operator,
        dry_run=False,
        bridge_capture_path=bridge_capture_path,
        bridge_summary=bridge_summary,
        ai_pipeline_result=ai_pipeline_result,
        backend_release_result=backend_release_result,
        validation_exit_code=validation_exit_code,
        validation_sample_path=validation_sample_path,
        final_status=final_status,
        stop_reason="pipeline_finished" if validation_exit_code == 0 else "validation_failed",
    )
    print(
        json.dumps(
            {
                "release_id": release_id,
                "status": final_status,
                "bridge_input_capture": str(bridge_capture_path),
                "backend_release_record": backend_release_result.get("record_path"),
                "validation_sample_path": str(validation_sample_path) if validation_sample_path else None,
                "record_path": str(record_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if validation_exit_code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
