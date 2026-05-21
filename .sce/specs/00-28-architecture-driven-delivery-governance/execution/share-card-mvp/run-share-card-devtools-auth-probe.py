import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[4]
FRONTEND_ROOT = WORKSPACE_ROOT / "kaipai-frontend"
DIST_PROJECT_ROOT = FRONTEND_ROOT / "dist" / "dev" / "mp-weixin"
SAMPLES_ROOT = SCRIPT_DIR / "samples"
DEVTOOLS_CLI = Path(r"D:\AP\微信web开发者工具\cli.bat")
DEFAULT_PORT = 9421


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the share-card DevTools auth probe and write a sample bundle.",
    )
    parser.add_argument(
        "label",
        nargs="?",
        default="share-card-devtools-auth-probe",
        help="Optional sample label suffix.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_appid() -> tuple[str, str]:
    candidates = [
        DIST_PROJECT_ROOT / "project.config.json",
        FRONTEND_ROOT / "project.config.json",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        return str(payload.get("appid") or "").strip(), str(candidate)
    return "", ""


def run_cli_auto(port: int) -> dict:
    command_text = f"{DEVTOOLS_CLI} auto --project {DIST_PROJECT_ROOT} --auto-port {port}"
    if not DEVTOOLS_CLI.exists():
        return {
            "commandText": command_text,
            "available": False,
            "returnCode": None,
            "stdout": "",
            "stderr": "DevTools CLI not found",
        }

    process = subprocess.run(
        ["cmd", "/c", str(DEVTOOLS_CLI), "auto", "--project", str(DIST_PROJECT_ROOT), "--auto-port", str(port)],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "commandText": command_text,
        "available": True,
        "returnCode": process.returncode,
        "stdout": process.stdout or "",
        "stderr": process.stderr or "",
    }


def run_port_check(port: int) -> str:
    process = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"if (Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue) {{ 'LISTENING' }} else {{ 'NO_LISTENER' }}",
        ],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (process.stdout or process.stderr or "").strip() or "UNKNOWN"


def classify_probe(cli_result: dict, port_check_result: str) -> str:
    combined = "\n".join([(cli_result.get("stdout") or ""), (cli_result.get("stderr") or "")])
    if "登录用户不是该小程序的开发者" in combined:
        return "devtools_auth_gate"
    if port_check_result == "LISTENING":
        return "automation_ready"
    if port_check_result == "NO_LISTENER":
        return "port_not_listening"
    return "unknown"


def build_summary_lines(sample_root: Path,
                        generated_at: str,
                        appid: str,
                        project_config_path: str,
                        port: int,
                        cli_result: dict,
                        port_check_result: str,
                        probe_result: str) -> list[str]:
    lines = [
        f"# Share Card DevTools Auth Probe {sample_root.name}",
        "",
        f"- Generated At: `{generated_at}`",
        f"- Project Root: `{DIST_PROJECT_ROOT}`",
        f"- Project Config: `{project_config_path or '--'}`",
        f"- AppID: `{appid or '--'}`",
        f"- Auto Port: `{port}`",
        f"- Probe Result: `{probe_result}`",
        "",
        "## CLI Replay",
        "",
        f"- Command: `{cli_result['commandText']}`",
        f"- CLI Available: `{cli_result['available']}`",
        f"- Return Code: `{cli_result['returnCode']}`",
        "- stdout log: `captures/devtools-cli-auto.stdout.log`",
        "- stderr log: `captures/devtools-cli-auto.stderr.log`",
        "",
        "## Port Check",
        "",
        f"- Result: `{port_check_result}`",
        "- port check file: `captures/port-check.txt`",
        "",
        "## Conclusion",
        "",
    ]

    if probe_result == "automation_ready":
        lines.append("- 当前 DevTools automation 端口已恢复，可继续重跑 share-card mini-program page evidence。")
    elif probe_result == "devtools_auth_gate":
        lines.append("- 当前阻塞是 DevTools 开发者授权，不在 page evidence 脚本或页面逻辑。")
    elif probe_result == "port_not_listening":
        lines.append("- 当前 9421 端口未监听，需先恢复 DevTools automation，再决定是否重跑 page evidence。")
    else:
        lines.append("- 当前探针未得到明确结论，请检查 CLI replay 与端口检查结果。")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `captures/devtools-cli-auto.stdout.log`",
            "- `captures/devtools-cli-auto.stderr.log`",
            "- `captures/port-check.txt`",
            "- `probe-result.json`",
            "",
        ]
    )
    return lines


def build_probe_payload(sample_root: Path,
                        generated_at: str,
                        appid: str,
                        project_config_path: str,
                        port: int,
                        cli_result: dict,
                        port_check_result: str,
                        probe_result: str) -> dict:
    summary_path = sample_root / "summary.md"
    result_path = sample_root / "probe-result.json"
    return {
        "generatedAt": generated_at,
        "sampleRoot": str(sample_root),
        "sampleId": sample_root.name,
        "summaryPath": str(summary_path),
        "probeSummaryPath": str(summary_path),
        "resultPath": str(result_path),
        "projectRoot": str(DIST_PROJECT_ROOT),
        "projectConfigPath": project_config_path,
        "appid": appid,
        "port": port,
        "probeResult": probe_result,
        "portCheckResult": port_check_result,
        "cliReplay": {
            "commandText": cli_result["commandText"],
            "available": cli_result["available"],
            "returnCode": cli_result["returnCode"],
        },
    }


def main() -> int:
    args = parse_args()
    label = args.label.strip() if args.label and args.label.strip() else "share-card-devtools-auth-probe"
    port = DEFAULT_PORT

    now = datetime.now()
    generated_at = now.isoformat(timespec="seconds")
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    captures_root = sample_root / "captures"
    ensure_dir(captures_root)

    appid, project_config_path = load_appid()
    cli_result = run_cli_auto(port)
    port_check_result = run_port_check(port)
    probe_result = classify_probe(cli_result, port_check_result)

    (captures_root / "devtools-cli-auto.stdout.log").write_text(cli_result["stdout"], encoding="utf-8")
    (captures_root / "devtools-cli-auto.stderr.log").write_text(cli_result["stderr"], encoding="utf-8")
    (captures_root / "port-check.txt").write_text(port_check_result + "\n", encoding="utf-8")

    summary_lines = build_summary_lines(
        sample_root=sample_root,
        generated_at=generated_at,
        appid=appid,
        project_config_path=project_config_path,
        port=port,
        cli_result=cli_result,
        port_check_result=port_check_result,
        probe_result=probe_result,
    )
    (sample_root / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    probe_payload = build_probe_payload(
        sample_root=sample_root,
        generated_at=generated_at,
        appid=appid,
        project_config_path=project_config_path,
        port=port,
        cli_result=cli_result,
        port_check_result=port_check_result,
        probe_result=probe_result,
    )

    (sample_root / "probe-result.json").write_text(
        json.dumps(
            probe_payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            probe_payload,
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
