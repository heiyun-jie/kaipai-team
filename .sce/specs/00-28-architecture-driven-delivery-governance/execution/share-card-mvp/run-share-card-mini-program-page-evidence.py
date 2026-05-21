import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


WS_ENDPOINT = "ws://127.0.0.1:9421"
DEFAULT_BASE_URL = "http://101.43.57.62/api"
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[4]
FRONTEND_ROOT = WORKSPACE_ROOT / "kaipai-frontend"
DIST_PROJECT_ROOT = FRONTEND_ROOT / "dist" / "dev" / "mp-weixin"
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-mini-program-screenshots.js"
PROBE_SCRIPT = SCRIPT_DIR / "run-share-card-devtools-auth-probe.py"
DEVTOOLS_CLI = Path(r"D:\AP\微信web开发者工具\cli.bat")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture the share-card mini-program page evidence or a blocker sample bundle.",
    )
    parser.add_argument(
        "source_sample",
        nargs="?",
        default=None,
        help="Optional explicit source sample id. Omit it to auto-select the latest source sample; in PowerShell, a single unknown positional value is treated as the label.",
    )
    parser.add_argument(
        "label",
        nargs="?",
        default=None,
        help="Optional sample label suffix.",
    )
    return parser.parse_args()


def normalize_cli_source_and_label(source_sample_arg: str | None, label_arg: str | None) -> tuple[str | None, str]:
    default_label = "share-card-mini-program-page-evidence"
    source_sample = source_sample_arg.strip() if source_sample_arg and source_sample_arg.strip() else None
    label = label_arg.strip() if label_arg and label_arg.strip() else ""
    if label:
        return source_sample, label
    if not source_sample:
        return None, default_label
    if (SAMPLES_ROOT / source_sample).exists():
        return source_sample, default_label
    return None, source_sample


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def first_non_empty_text(*values: object) -> str:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def derive_probe_sample_root(probe_launch: dict) -> str:
    sample_root_text = first_non_empty_text(probe_launch.get("sampleRoot"))
    if sample_root_text:
        return sample_root_text

    for key in ("probeSummaryPath", "summaryPath", "resultPath"):
        candidate_text = first_non_empty_text(probe_launch.get(key))
        if not candidate_text:
            continue
        return str(Path(candidate_text).parent)
    return ""


def list_sample_dirs() -> list[Path]:
    if not SAMPLES_ROOT.exists():
        return []
    return sorted(
        [item for item in SAMPLES_ROOT.iterdir() if item.is_dir()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )


def resolve_source_sample(explicit_sample_id: str | None) -> tuple[Path, str]:
    if explicit_sample_id:
        candidate = SAMPLES_ROOT / explicit_sample_id
        if not candidate.exists():
            raise RuntimeError(f"source sample not found: {explicit_sample_id}")
        return candidate, "explicit_arg"

    for candidate in list_sample_dirs():
        if (candidate / "closure-context.json").exists():
            return candidate, "auto_latest_closure_context"

    raise RuntimeError("no share-card sample with closure-context.json found")


def build_source_sample_selection_display(selection_mode: str) -> str:
    if selection_mode == "explicit_arg":
        return "显式指定 source sample"
    if selection_mode == "auto_latest_closure_context":
        return "自动命中最新 closure-context 样本"
    return "未识别 source sample 选择方式"


def build_source_sample_selection_note(selection_mode: str) -> str:
    if selection_mode == "explicit_arg":
        return "本轮通过命令行第一个参数显式指定了 source sample。"
    if selection_mode == "auto_latest_closure_context":
        return "本轮未显式传 source sample，脚本已自动选择最新且包含 `closure-context.json` 的样本。"
    return "当前未得到可识别的 source sample 选择说明。"


def print_cli_result(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def write_result_json(sample_root: Path, payload: dict) -> Path:
    result_path = sample_root / "page-evidence-result.json"
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result_path


def load_source_summary(sample_dir: Path) -> dict:
    payload = json.loads((sample_dir / "closure-context.json").read_text(encoding="utf-8"))
    context = payload.get("context") or {}
    owner_phone = context.get("ownerPhone")
    owner_user_id = context.get("ownerUserId")
    viewer_phone = context.get("viewerPhone")
    viewer_user_id = context.get("viewerUserId")
    share_card_id = context.get("shareCardId")
    request_id = context.get("requestId")
    if not owner_phone or not owner_user_id or not viewer_phone or not viewer_user_id or not share_card_id:
        raise RuntimeError(f"source sample missing owner/viewer/shareCardId: {sample_dir}")

    base_url = str(context.get("baseUrl") or DEFAULT_BASE_URL).strip().rstrip("/")
    if not base_url.endswith("/api"):
        base_url = f"{base_url}/api"

    return {
        "sampleId": sample_dir.name,
        "baseUrl": base_url,
        "environment": context.get("environment") or "unknown",
        "ownerPhone": str(owner_phone),
        "ownerUserId": str(owner_user_id),
        "viewerPhone": str(viewer_phone),
        "viewerUserId": str(viewer_user_id),
        "shareCardId": str(share_card_id),
        "requestId": str(request_id or ""),
        "sceneKey": str(context.get("sceneKey") or "general"),
    }


def load_project_appid() -> dict:
    candidates = [
        DIST_PROJECT_ROOT / "project.config.json",
        FRONTEND_ROOT / "project.config.json",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive fallback
            return {
                "projectConfigPath": str(candidate),
                "appid": "",
                "loadError": str(exc),
            }
        return {
            "projectConfigPath": str(candidate),
            "appid": str(payload.get("appid") or "").strip(),
            "loadError": "",
        }
    return {
        "projectConfigPath": "",
        "appid": "",
        "loadError": "project.config.json not found",
    }


def detect_failure_kind(stdout_text: str, stderr_text: str) -> str:
    combined = "\n".join([stdout_text or "", stderr_text or ""])
    if "登录用户不是该小程序的开发者" in combined:
        return "devtools_auth_gate"
    if f"Failed connecting to {WS_ENDPOINT}" in combined:
        return "ws_endpoint_unavailable"
    if "timeout" in combined.lower():
        return "capture_timeout"
    return "capture_failed"


def replay_devtools_cli_auto() -> dict:
    command_text = f"{DEVTOOLS_CLI} auto --project {DIST_PROJECT_ROOT} --auto-port 9421"
    if not DEVTOOLS_CLI.exists():
        return {
            "commandText": command_text,
            "available": False,
            "returnCode": None,
            "stdout": "",
            "stderr": "DevTools CLI not found",
        }

    process = subprocess.run(
        ["cmd", "/c", str(DEVTOOLS_CLI), "auto", "--project", str(DIST_PROJECT_ROOT), "--auto-port", "9421"],
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


def run_port_check() -> str:
    process = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-NetTCPConnection -LocalPort 9421 -ErrorAction SilentlyContinue) { 'LISTENING' } else { 'NO_LISTENER' }",
        ],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = (process.stdout or process.stderr or "").strip()
    return output or "UNKNOWN"


def run_devtools_auth_probe(label: str) -> dict:
    command = [sys.executable, str(PROBE_SCRIPT), label]
    command_text = " ".join(command)
    result = {
        "commandText": command_text,
        "available": PROBE_SCRIPT.exists(),
        "returnCode": None,
        "stdout": "",
        "stderr": "",
        "sampleRoot": "",
        "sampleId": "",
        "summaryPath": "",
        "probeSummaryPath": "",
        "resultPath": "",
        "probeResult": "probe_script_missing",
        "portCheckResult": "UNKNOWN",
        "cliReplay": {
            "commandText": "",
            "available": None,
            "returnCode": None,
            "stdout": "",
            "stderr": "",
        },
    }
    if not PROBE_SCRIPT.exists():
        result["stderr"] = "DevTools auth probe script not found"
        return result

    try:
        process = subprocess.run(
            command,
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=240,
        )
    except subprocess.TimeoutExpired as exc:
        result["stderr"] = f"DevTools auth probe timed out: {exc}"
        result["probeResult"] = "probe_timeout"
        return result

    result.update(
        {
            "returnCode": process.returncode,
            "stdout": process.stdout or "",
            "stderr": process.stderr or "",
            "probeResult": "probe_failed",
        }
    )
    if process.returncode != 0:
        return result

    stdout_text = (process.stdout or "").strip()
    if not stdout_text:
        result["probeResult"] = "probe_output_missing"
        return result

    try:
        probe_launch = json.loads(stdout_text)
    except json.JSONDecodeError as exc:
        result["probeResult"] = "probe_output_invalid"
        result["stderr"] = ((result["stderr"] + "\n") if result["stderr"] else "") + f"[probe-stdout-json-decode] {exc}"
        return result

    sample_root_text = derive_probe_sample_root(probe_launch)
    if not sample_root_text:
        result["probeResult"] = "probe_sample_missing"
        return result

    sample_root = Path(sample_root_text)
    result["sampleRoot"] = first_non_empty_text(probe_launch.get("sampleRoot"), str(sample_root))
    result["sampleId"] = first_non_empty_text(probe_launch.get("sampleId"), sample_root.name)
    result["summaryPath"] = first_non_empty_text(
        probe_launch.get("summaryPath"),
        probe_launch.get("probeSummaryPath"),
        sample_root / "summary.md",
    )
    result["probeSummaryPath"] = first_non_empty_text(
        probe_launch.get("probeSummaryPath"),
        probe_launch.get("summaryPath"),
        result["summaryPath"],
    )
    result["resultPath"] = first_non_empty_text(probe_launch.get("resultPath"), sample_root / "probe-result.json")

    probe_result_path = Path(result["resultPath"])
    if not probe_result_path.exists():
        fallback_probe_result_path = sample_root / "probe-result.json"
        if fallback_probe_result_path.exists():
            probe_result_path = fallback_probe_result_path
            result["resultPath"] = str(fallback_probe_result_path)
        else:
            result["probeResult"] = "probe_result_missing"
            return result

    try:
        probe_payload = json.loads(probe_result_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result["probeResult"] = "probe_result_invalid"
        result["stderr"] = ((result["stderr"] + "\n") if result["stderr"] else "") + f"[probe-result-json-decode] {exc}"
        return result

    result["sampleRoot"] = first_non_empty_text(probe_payload.get("sampleRoot"), result["sampleRoot"])
    result["sampleId"] = first_non_empty_text(probe_payload.get("sampleId"), result["sampleId"])
    result["summaryPath"] = first_non_empty_text(
        probe_payload.get("summaryPath"),
        probe_payload.get("probeSummaryPath"),
        result["summaryPath"],
    )
    result["probeSummaryPath"] = first_non_empty_text(
        probe_payload.get("probeSummaryPath"),
        probe_payload.get("summaryPath"),
        result["probeSummaryPath"],
    )
    result["resultPath"] = first_non_empty_text(probe_payload.get("resultPath"), result["resultPath"])

    sample_root = Path(result["sampleRoot"]) if result["sampleRoot"] else sample_root
    cli_stdout_path = sample_root / "captures" / "devtools-cli-auto.stdout.log"
    cli_stderr_path = sample_root / "captures" / "devtools-cli-auto.stderr.log"
    probe_cli_replay = probe_payload.get("cliReplay") or {}
    result.update(
        {
            "probeResult": str(probe_payload.get("probeResult") or "unknown"),
            "portCheckResult": str(probe_payload.get("portCheckResult") or "UNKNOWN"),
            "cliReplay": {
                "commandText": str(probe_cli_replay.get("commandText") or ""),
                "available": probe_cli_replay.get("available"),
                "returnCode": probe_cli_replay.get("returnCode"),
                "stdout": read_text_if_exists(cli_stdout_path),
                "stderr": read_text_if_exists(cli_stderr_path),
            },
        }
    )
    return result


def classify_preflight_failure_kind(preflight_probe: dict) -> str:
    probe_result = str(preflight_probe.get("probeResult") or "")
    port_check_result = str(preflight_probe.get("portCheckResult") or "")
    if probe_result == "devtools_auth_gate":
        return "preflight_devtools_auth_gate"
    if probe_result == "port_not_listening" or port_check_result == "NO_LISTENER":
        return "preflight_port_not_listening"
    if probe_result == "automation_ready":
        return "automation_ready"
    return "preflight_probe_failed"


def build_skipped_capture_log(preflight_probe: dict) -> str:
    lines = [
        "[skipped] share-card mini program screenshot capture did not start because the DevTools preflight probe blocked execution.",
        f"probeSample={preflight_probe.get('sampleId') or '--'}",
        f"probeSummary={preflight_probe.get('probeSummaryPath') or '--'}",
        f"probeResultPath={preflight_probe.get('resultPath') or '--'}",
        f"probeResult={preflight_probe.get('probeResult') or '--'}",
        f"portCheck={preflight_probe.get('portCheckResult') or '--'}",
    ]
    return "\n".join(lines) + "\n"


def write_blocked_summary(sample_root: Path,
                          source_summary: dict,
                          source_sample_selection_mode: str,
                          failure_kind: str,
                          stdout_log_path: Path,
                          stderr_log_path: Path,
                          blocker_capture_path: Path,
                          port_check_path: Path,
                          preflight_probe: dict | None = None) -> None:
    lines = [
        f"# Share Card Mini Program Page Evidence {sample_root.name}",
        "",
        "- Status: `blocked`",
        f"- Generated At: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Source Share Card Sample: `{source_summary['sampleId']}`",
        f"- Source Share Card Sample Selection: `{source_sample_selection_mode}`",
        f"- Source Share Card Sample Selection Display: `{build_source_sample_selection_display(source_sample_selection_mode)}`",
        f"- Source Share Card Sample Selection Note: {build_source_sample_selection_note(source_sample_selection_mode)}",
        f"- Base URL: `{source_summary['baseUrl']}`",
        f"- WS Endpoint: `{WS_ENDPOINT}`",
        f"- Failure Kind: `{failure_kind}`",
        "",
        "## Source Context",
        "",
        f"- Owner Phone: `{source_summary['ownerPhone']}`",
        f"- Owner User ID: `{source_summary['ownerUserId']}`",
        f"- Viewer Phone: `{source_summary['viewerPhone']}`",
        f"- Viewer User ID: `{source_summary['viewerUserId']}`",
        f"- Share Card ID: `{source_summary['shareCardId']}`",
        f"- Contact Request ID: `{source_summary['requestId']}`",
        f"- Scene: `{source_summary['sceneKey']}`",
        "",
        "## Blocker",
        "",
    ]
    if preflight_probe:
        lines.extend(
            [
                "- 本轮在 DevTools preflight 阶段即判定阻塞，未启动页面截图。",
                f"- 预检探针摘要: `{preflight_probe.get('probeSummaryPath') or '--'}`",
                f"- 预检结果文件: `{preflight_probe.get('resultPath') or '--'}`",
                f"- 预检结果: `{preflight_probe.get('probeResult') or '--'}`",
                f"- 预检端口检查: `{preflight_probe.get('portCheckResult') or '--'}`",
            ]
        )
    else:
        lines.append("- 本轮 page evidence 未进入页面截图阶段，阻塞发生在 DevTools / automator 建连前。")

    lines.extend(
        [
        f"- 原始 stdout: `{stdout_log_path.relative_to(sample_root)}`",
        f"- 原始 stderr: `{stderr_log_path.relative_to(sample_root)}`",
        f"- 标准 blocker 记录: `{blocker_capture_path.relative_to(sample_root)}`",
        f"- 端口检查: `{port_check_path.relative_to(sample_root)}`",
        "",
        "## Output Files",
        "",
        "- `page-evidence-result.json`",
        "- `captures/mini-program-screenshot-capture.stdout.log`",
        "- `captures/mini-program-screenshot-capture.stderr.log`",
        "- `captures/devtools-auth-blocker.txt`",
        "- `captures/devtools-cli-auto.stdout.log`",
        "- `captures/devtools-cli-auto.stderr.log`",
        "- `captures/port-check.txt`",
        "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_devtools_blocker_capture(sample_root: Path,
                                   source_summary: dict,
                                   failure_kind: str,
                                   stdout_text: str,
                                   stderr_text: str,
                                   cli_replay: dict,
                                   port_check_result: str,
                                   preflight_probe: dict | None = None) -> Path:
    captures_root = sample_root / "captures"
    cli_stdout_path = captures_root / "devtools-cli-auto.stdout.log"
    cli_stderr_path = captures_root / "devtools-cli-auto.stderr.log"
    port_check_path = captures_root / "port-check.txt"
    blocker_path = captures_root / "devtools-auth-blocker.txt"

    cli_stdout_path.write_text(cli_replay.get("stdout") or "", encoding="utf-8")
    cli_stderr_path.write_text(cli_replay.get("stderr") or "", encoding="utf-8")
    port_check_path.write_text((port_check_result or "UNKNOWN") + "\n", encoding="utf-8")

    project_appid = load_project_appid()
    lines = [
        "Share Card DevTools Blocker Capture",
        f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "1. Source sample context",
        f"- Source sample: `{source_summary['sampleId']}`",
        f"- Owner phone: `{source_summary['ownerPhone']}`",
        f"- Viewer phone: `{source_summary['viewerPhone']}`",
        f"- Share card id: `{source_summary['shareCardId']}`",
        f"- Scene: `{source_summary['sceneKey']}`",
        "",
        "2. Target appid",
        f"- Project config: `{project_appid.get('projectConfigPath') or 'N/A'}`",
        f"- appid: `{project_appid.get('appid') or 'UNKNOWN'}`",
    ]
    if project_appid.get("loadError"):
        lines.append(f"- load error: `{project_appid['loadError']}`")

    if preflight_probe:
        lines.extend(
            [
                "",
                "3. Preflight probe",
                f"- Probe sample: `{preflight_probe.get('sampleId') or '--'}`",
                f"- Probe summary: `{preflight_probe.get('probeSummaryPath') or '--'}`",
                f"- Probe result file: `{preflight_probe.get('resultPath') or '--'}`",
                f"- Probe result: `{preflight_probe.get('probeResult') or '--'}`",
                f"- Port check result: `{preflight_probe.get('portCheckResult') or '--'}`",
                "",
                "4. Capture stage",
                f"- Failure kind: `{failure_kind}`",
                "- Screenshot capture was skipped before capture-mini-program-screenshots.js started.",
            ]
        )
        if stderr_text.strip():
            lines.append("- skip note:")
            for line in stderr_text.strip().splitlines()[:6]:
                lines.append(f"  - `{line}`")
        cli_section = "5. DevTools CLI replay"
        port_section = "6. Port check"
        conclusion_section = "7. Conclusion"
    else:
        lines.extend(
            [
                "",
                "3. Initial capture failure",
                f"- Failure kind: `{failure_kind}`",
                f"- WS endpoint: `{WS_ENDPOINT}`",
                "- stderr excerpt:",
            ]
        )
        for line in (stderr_text or "").strip().splitlines()[:8]:
            lines.append(f"  - `{line}`")
        if stdout_text.strip():
            lines.append("- stdout excerpt:")
            for line in stdout_text.strip().splitlines()[:6]:
                lines.append(f"  - `{line}`")
        cli_section = "4. DevTools CLI replay"
        port_section = "5. Port check"
        conclusion_section = "6. Conclusion"

    lines.extend(
        [
            "",
            cli_section,
            f"- Command: `{cli_replay.get('commandText')}`",
            f"- CLI available: `{cli_replay.get('available')}`",
            f"- Return code: `{cli_replay.get('returnCode')}`",
            f"- stdout log: `{cli_stdout_path.name}`",
            f"- stderr log: `{cli_stderr_path.name}`",
        ]
    )

    cli_combined = "\n".join([(cli_replay.get("stdout") or "").strip(), (cli_replay.get("stderr") or "").strip()]).strip()
    if cli_combined:
        lines.append("- replay excerpt:")
        for line in cli_combined.splitlines()[:10]:
            lines.append(f"  - `{line}`")

    lines.extend(
        [
            "",
            port_section,
            "- Command: `if (Get-NetTCPConnection -LocalPort 9421 -ErrorAction SilentlyContinue) { 'LISTENING' } else { 'NO_LISTENER' }`",
            f"- Result: `{port_check_result}`",
            "",
            conclusion_section,
        ]
    )

    if "登录用户不是该小程序的开发者" in cli_combined:
        lines.append("- Current blocker is DevTools developer authorization for the target appid, not page logic.")
    elif failure_kind in {"ws_endpoint_unavailable", "preflight_port_not_listening"}:
        lines.append("- Current blocker is that the DevTools automation endpoint is unavailable before capture begins.")
    else:
        lines.append("- Current blocker is in the DevTools / automator stage; inspect the replay logs before rerun.")

    lines.append("- This sample did not produce spec-valid mini-program screenshots.")
    blocker_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return blocker_path


def write_summary(sample_root: Path, source_summary: dict, source_sample_selection_mode: str, manifest: dict) -> None:
    lines = [
        f"# Share Card Mini Program Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- WS Endpoint: `{manifest.get('wsEndpoint')}`",
        f"- Source Share Card Sample: `{source_summary['sampleId']}`",
        f"- Source Share Card Sample Selection: `{source_sample_selection_mode}`",
        f"- Source Share Card Sample Selection Display: `{build_source_sample_selection_display(source_sample_selection_mode)}`",
        f"- Source Share Card Sample Selection Note: {build_source_sample_selection_note(source_sample_selection_mode)}",
        "",
        "## Source Context",
        "",
        f"- Owner Phone: `{source_summary['ownerPhone']}`",
        f"- Owner User ID: `{source_summary['ownerUserId']}`",
        f"- Viewer Phone: `{source_summary['viewerPhone']}`",
        f"- Viewer User ID: `{source_summary['viewerUserId']}`",
        f"- Share Card ID: `{source_summary['shareCardId']}`",
        f"- Contact Request ID: `{source_summary['requestId']}`",
        f"- Scene: `{source_summary['sceneKey']}`",
        "",
        "## Captures",
        "",
    ]

    for item in manifest.get("captures") or []:
        lines.append(
            f"- `{item['name']}` -> session=`{item.get('sessionName')}` path=`{item['actualPath']}` query=`{json.dumps(item.get('actualQuery') or {}, ensure_ascii=False)}` screenshot=`{Path(item['screenshotPath']).name}` method=`{item.get('screenshotMethod')}` pageData=`{Path(item['pageDataPath']).name}`"
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- 本轮固定 owner 首页 / 我的名片 / 卡片编辑 / 个人中心，以及 owner 小程序卡片 / 海报分享终态、viewer 从分享路径再次进入的小程序卡片 / 海报页、公开名片 / 查看历史。",
            "- 页面证据直接复用成功远端样本的真实 owner/viewer/shareCardId，不再重新造业务数据。",
            "",
            "## Visual Review",
            "",
            f"- Unique Screenshot Hash Count: `{(manifest.get('visualReview') or {}).get('uniqueScreenshotHashCount')}`",
            f"- Unique Actual Path Count: `{(manifest.get('visualReview') or {}).get('uniqueActualPathCount')}`",
            f"- Visual Did Not Refresh: `{(manifest.get('visualReview') or {}).get('visualDidNotRefresh')}`",
            "",
            "## Artifacts",
            "",
            "- `page-evidence-result.json`",
            "- `captures/mini-program-screenshot-capture.json`",
            "- `captures/mini-program-capture-progress.log`",
            "- `captures/mini-program-screenshot-capture.stdout.log`",
            "- `captures/mini-program-screenshot-capture.stderr.log`",
            "- `captures/page-data-*.json`",
            "- `screenshots/owner-home-share-cards.png`",
            "- `screenshots/owner-card-list.png`",
            "- `screenshots/owner-card-editor-general.png`",
            "- `screenshots/owner-share-action-mini-program.png`",
            "- `screenshots/owner-share-action-poster.png`",
            "- `screenshots/viewer-shared-reentry-mini-program.png`",
            "- `screenshots/viewer-shared-reentry-poster.png`",
            "- `screenshots/viewer-public-card-detail.png`",
            "- `screenshots/viewer-history.png`",
            "- `screenshots/owner-mine.png`",
            "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_cli_result_payload(sample_root: Path,
                             source_summary: dict,
                             source_sample_selection_mode: str,
                             status: str,
                             failure_kind: str | None = None,
                             blocker_capture_path: Path | None = None,
                             preflight_probe: dict | None = None,
                             captures: list[str] | None = None) -> dict:
    payload = {
        "sampleRoot": str(sample_root),
        "summaryPath": str(sample_root / "summary.md"),
        "resultPath": str(sample_root / "page-evidence-result.json"),
        "sourceSample": source_summary["sampleId"],
        "sourceSampleSelectionMode": source_sample_selection_mode,
        "sourceSampleSelectionDisplay": build_source_sample_selection_display(source_sample_selection_mode),
        "sourceSampleSelectionNote": build_source_sample_selection_note(source_sample_selection_mode),
        "status": status,
    }
    if failure_kind:
        payload["failureKind"] = failure_kind
    if blocker_capture_path:
        payload["blockerCapture"] = str(blocker_capture_path)
    else:
        payload["blockerCapture"] = ""
    if preflight_probe:
        payload["preflightProbeSample"] = preflight_probe.get("sampleId")
        payload["preflightProbeResult"] = preflight_probe.get("probeResult")
        payload["preflightPortCheck"] = preflight_probe.get("portCheckResult")
        payload["preflightProbeSummaryPath"] = preflight_probe.get("probeSummaryPath")
        payload["preflightProbeResultPath"] = preflight_probe.get("resultPath")
    else:
        payload["preflightProbeSample"] = None
        payload["preflightProbeResult"] = None
        payload["preflightPortCheck"] = None
        payload["preflightProbeSummaryPath"] = None
        payload["preflightProbeResultPath"] = None
    if captures is not None:
        payload["captures"] = captures
        payload["captureManifestPath"] = str(sample_root / "captures" / "mini-program-screenshot-capture.json")
    else:
        payload["captures"] = []
        payload["captureManifestPath"] = ""
    return payload


def main() -> int:
    args = parse_args()
    explicit_source_sample, label = normalize_cli_source_and_label(args.source_sample, args.label)

    source_sample_dir, source_sample_selection_mode = resolve_source_sample(explicit_source_sample)
    source_summary = load_source_summary(source_sample_dir)

    sample_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)
    ensure_dir(sample_root / "captures")

    stdout_log_path = sample_root / "captures" / "mini-program-screenshot-capture.stdout.log"
    stderr_log_path = sample_root / "captures" / "mini-program-screenshot-capture.stderr.log"

    preflight_probe = run_devtools_auth_probe(f"{label}-preflight")
    if preflight_probe.get("probeResult") != "automation_ready" or preflight_probe.get("portCheckResult") != "LISTENING":
        skip_log_text = build_skipped_capture_log(preflight_probe)
        stdout_log_path.write_text(skip_log_text, encoding="utf-8")
        stderr_log_path.write_text(skip_log_text, encoding="utf-8")
        failure_kind = classify_preflight_failure_kind(preflight_probe)
        cli_replay = preflight_probe.get("cliReplay") or {}
        blocker_capture_path = write_devtools_blocker_capture(
            sample_root,
            source_summary,
            failure_kind,
            skip_log_text,
            skip_log_text,
            cli_replay,
            str(preflight_probe.get("portCheckResult") or "UNKNOWN"),
            preflight_probe=preflight_probe,
        )
        write_blocked_summary(
            sample_root,
            source_summary,
            source_sample_selection_mode,
            failure_kind,
            stdout_log_path,
            stderr_log_path,
            blocker_capture_path,
            sample_root / "captures" / "port-check.txt",
            preflight_probe=preflight_probe,
        )
        cli_payload = build_cli_result_payload(
            sample_root=sample_root,
            source_summary=source_summary,
            source_sample_selection_mode=source_sample_selection_mode,
            status="blocked",
            failure_kind=failure_kind,
            blocker_capture_path=blocker_capture_path,
            preflight_probe=preflight_probe,
        )
        write_result_json(sample_root, cli_payload)
        print_cli_result(cli_payload)
        raise RuntimeError(
            "share-card mini program capture skipped by DevTools preflight: "
            f"probeResult={preflight_probe.get('probeResult')}, "
            f"portCheck={preflight_probe.get('portCheckResult')}, "
            f"probeSample={preflight_probe.get('sampleRoot')}, "
            f"pageEvidenceSample={sample_root}"
        )

    command = [
        "node",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        WS_ENDPOINT,
        source_summary["baseUrl"],
        source_summary["ownerPhone"],
        source_summary["viewerPhone"],
        source_summary["ownerUserId"],
        source_summary["viewerUserId"],
        source_summary["shareCardId"],
        source_summary["requestId"],
        source_summary["sampleId"],
        "mini-program-screenshot-capture.json",
    ]
    process = subprocess.Popen(
        command,
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout_text, stderr_text = process.communicate(timeout=420)
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout_text, stderr_text = process.communicate()
        stdout_log_path.write_text(stdout_text or "", encoding="utf-8")
        stderr_log_path.write_text((stderr_text or "") + f"\n[timeout] {exc}\n", encoding="utf-8")
        failure_kind = detect_failure_kind(stdout_text, (stderr_text or "") + f"\n[timeout] {exc}\n")
        cli_replay = replay_devtools_cli_auto()
        port_check_result = run_port_check()
        blocker_capture_path = write_devtools_blocker_capture(
            sample_root,
            source_summary,
            failure_kind,
            stdout_text,
            (stderr_text or "") + f"\n[timeout] {exc}\n",
            cli_replay,
            port_check_result,
        )
        write_blocked_summary(
            sample_root,
            source_summary,
            source_sample_selection_mode,
            failure_kind,
            stdout_log_path,
            stderr_log_path,
            blocker_capture_path,
            sample_root / "captures" / "port-check.txt",
            preflight_probe=None,
        )
        cli_payload = build_cli_result_payload(
            sample_root=sample_root,
            source_summary=source_summary,
            source_sample_selection_mode=source_sample_selection_mode,
            status="blocked",
            failure_kind=failure_kind,
            blocker_capture_path=blocker_capture_path,
        )
        write_result_json(sample_root, cli_payload)
        print_cli_result(cli_payload)
        raise RuntimeError(
            "share-card mini program capture timed out: "
            f"stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        ) from exc

    stdout_log_path.write_text(stdout_text or "", encoding="utf-8")
    stderr_log_path.write_text(stderr_text or "", encoding="utf-8")

    if process.returncode != 0:
        failure_kind = detect_failure_kind(stdout_text, stderr_text)
        cli_replay = replay_devtools_cli_auto()
        port_check_result = run_port_check()
        blocker_capture_path = write_devtools_blocker_capture(
            sample_root,
            source_summary,
            failure_kind,
            stdout_text,
            stderr_text,
            cli_replay,
            port_check_result,
        )
        write_blocked_summary(
            sample_root,
            source_summary,
            source_sample_selection_mode,
            failure_kind,
            stdout_log_path,
            stderr_log_path,
            blocker_capture_path,
            sample_root / "captures" / "port-check.txt",
            preflight_probe=None,
        )
        cli_payload = build_cli_result_payload(
            sample_root=sample_root,
            source_summary=source_summary,
            source_sample_selection_mode=source_sample_selection_mode,
            status="blocked",
            failure_kind=failure_kind,
            blocker_capture_path=blocker_capture_path,
        )
        write_result_json(sample_root, cli_payload)
        print_cli_result(cli_payload)
        raise RuntimeError(
            "share-card mini program capture failed: "
            f"returnCode={process.returncode}, stderrLog={stderr_log_path}, stdoutLog={stdout_log_path}"
        )

    manifest = json.loads((sample_root / "captures" / "mini-program-screenshot-capture.json").read_text(encoding="utf-8"))
    write_summary(sample_root, source_summary, source_sample_selection_mode, manifest)

    cli_payload = build_cli_result_payload(
        sample_root=sample_root,
        source_summary=source_summary,
        source_sample_selection_mode=source_sample_selection_mode,
        status="success",
        captures=[item["name"] for item in manifest.get("captures") or []],
    )
    write_result_json(sample_root, cli_payload)
    print_cli_result(cli_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
