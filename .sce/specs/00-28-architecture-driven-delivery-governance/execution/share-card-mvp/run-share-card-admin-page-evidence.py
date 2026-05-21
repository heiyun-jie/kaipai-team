import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-admin-share-card-governance-screenshots.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture the share-card admin page evidence bundle.",
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
    default_label = "share-card-admin-page-evidence"
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
        if (candidate / "sample-metadata.json").exists():
            return candidate, "auto_latest_sample_metadata"

    raise RuntimeError("no share-card validation sample with sample-metadata.json found")


def build_source_sample_selection_display(selection_mode: str) -> str:
    if selection_mode == "explicit_arg":
        return "显式指定 source sample"
    if selection_mode == "auto_latest_sample_metadata":
        return "自动命中最新 sample-metadata 样本"
    return "未识别 source sample 选择方式"


def build_source_sample_selection_note(selection_mode: str) -> str:
    if selection_mode == "explicit_arg":
        return "本轮通过命令行第一个参数显式指定了 source sample。"
    if selection_mode == "auto_latest_sample_metadata":
        return "本轮未显式传 source sample，脚本已自动选择最新且包含 `sample-metadata.json` 的样本。"
    return "当前未得到可识别的 source sample 选择说明。"


def print_cli_result(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def write_result_json(sample_root: Path, payload: dict) -> Path:
    result_path = sample_root / "admin-page-evidence-result.json"
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result_path


def load_source_summary(sample_dir: Path) -> dict:
    payload = json.loads((sample_dir / "sample-metadata.json").read_text(encoding="utf-8"))
    owner_user_id = payload.get("ownerUserId")
    viewer_user_id = payload.get("viewerUserId")
    share_card_id = payload.get("shareCardId")
    request_id = payload.get("requestId")
    if not owner_user_id or not viewer_user_id or not share_card_id or not request_id:
        raise RuntimeError(f"source sample missing owner/viewer/request/shareCard ids: {sample_dir}")
    return {
        "sampleId": payload.get("sampleId") or sample_dir.name,
        "ownerUserId": str(owner_user_id),
        "viewerUserId": str(viewer_user_id),
        "shareCardId": str(share_card_id),
        "requestId": str(request_id),
    }


def write_summary(sample_root: Path, source_summary: dict, source_sample_selection_mode: str, manifest: dict) -> None:
    lines = [
        f"# Share Card Admin Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- Proxy URL: `{manifest.get('proxyUrl')}`",
        f"- Local Admin URL: `{manifest.get('localAdminUrl')}`",
        f"- Source Share Card Sample: `{source_summary['sampleId']}`",
        f"- Source Share Card Sample Selection: `{source_sample_selection_mode}`",
        f"- Source Share Card Sample Selection Display: `{build_source_sample_selection_display(source_sample_selection_mode)}`",
        f"- Source Share Card Sample Selection Note: {build_source_sample_selection_note(source_sample_selection_mode)}",
        "",
        "## Entity IDs",
        "",
        f"- Owner User ID: `{source_summary['ownerUserId']}`",
        f"- Viewer User ID: `{source_summary['viewerUserId']}`",
        f"- Share Card ID: `{source_summary['shareCardId']}`",
        f"- Contact Request ID: `{source_summary['requestId']}`",
        "",
        "## Captures",
        "",
    ]

    for item in manifest.get("captures") or []:
        if item["name"] == "admin-share-card-default-general-card":
            lines.append(
                f"- `{item['name']}` -> route=`{item['route']}` screenshot=`{Path(item['screenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}`"
            )
            continue
        if item.get("actionScreenshotPath"):
            lines.append(
                f"- `{item['name']}` -> route=`{item['route']}` action=`{Path(item['actionScreenshotPath']).name}` list=`{Path(item['listScreenshotPath']).name}` detail=`{Path(item['detailScreenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}`"
            )
            continue
        lines.append(
            f"- `{item['name']}` -> route=`{item['route']}` list=`{Path(item['listScreenshotPath']).name}` detail=`{Path(item['detailScreenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}`"
        )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `admin-page-evidence-result.json`",
            "- `captures/admin-share-card-screenshot-capture.json`",
            "- `captures/admin-share-card-screenshot-capture.stdout.log`",
            "- `captures/admin-share-card-screenshot-capture.stderr.log`",
            "- `captures/admin-local-vite.log`",
            "- `captures/page-data-admin-share-card-contact-requests.json`",
            "- `captures/page-data-admin-share-card-share-cards.json`",
            "- `captures/page-data-admin-share-card-default-general-card.json`",
            "- `screenshots/admin-share-card-contact-requests.png`",
            "- `screenshots/admin-share-card-contact-requests-detail.png`",
            "- `screenshots/admin-share-card-share-cards-repair-legacy.png`",
            "- `screenshots/admin-share-card-share-cards.png`",
            "- `screenshots/admin-share-card-share-cards-detail.png`",
            "- `screenshots/admin-share-card-default-general-card.png`",
            "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_cli_result_payload(sample_root: Path,
                             source_summary: dict,
                             source_sample_selection_mode: str,
                             status: str,
                             captures: list[str] | None = None,
                             failure_kind: str | None = None,
                             return_code: int | None = None,
                             stdout_log_path: Path | None = None,
                             stderr_log_path: Path | None = None) -> dict:
    payload = {
        "sampleRoot": str(sample_root),
        "summaryPath": str(sample_root / "summary.md"),
        "resultPath": str(sample_root / "admin-page-evidence-result.json"),
        "sourceSample": source_summary["sampleId"],
        "sourceSampleSelectionMode": source_sample_selection_mode,
        "sourceSampleSelectionDisplay": build_source_sample_selection_display(source_sample_selection_mode),
        "sourceSampleSelectionNote": build_source_sample_selection_note(source_sample_selection_mode),
        "status": status,
    }
    if captures is not None:
        payload["captures"] = captures
        payload["captureManifestPath"] = str(sample_root / "captures" / "admin-share-card-screenshot-capture.json")
    else:
        payload["captures"] = []
        payload["captureManifestPath"] = ""
    if failure_kind:
        payload["failureKind"] = failure_kind
    if return_code is not None:
        payload["returnCode"] = return_code
    if stdout_log_path:
        payload["stdoutLog"] = str(stdout_log_path)
    else:
        payload["stdoutLog"] = ""
    if stderr_log_path:
        payload["stderrLog"] = str(stderr_log_path)
    else:
        payload["stderrLog"] = ""
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

    stdout_log_path = sample_root / "captures" / "admin-share-card-screenshot-capture.stdout.log"
    stderr_log_path = sample_root / "captures" / "admin-share-card-screenshot-capture.stderr.log"

    command = [
        "python",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        source_summary["requestId"],
        source_summary["shareCardId"],
        source_summary["viewerUserId"],
        source_summary["ownerUserId"],
    ]
    process = subprocess.Popen(
        command,
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout_text, stderr_text = process.communicate(timeout=420)
    stdout_log_path.write_text(stdout_text or "", encoding="utf-8")
    stderr_log_path.write_text(stderr_text or "", encoding="utf-8")

    if process.returncode != 0:
        cli_payload = build_cli_result_payload(
            sample_root=sample_root,
            source_summary=source_summary,
            source_sample_selection_mode=source_sample_selection_mode,
            status="failed",
            failure_kind="capture_failed",
            return_code=process.returncode,
            stdout_log_path=stdout_log_path,
            stderr_log_path=stderr_log_path,
        )
        write_result_json(sample_root, cli_payload)
        print_cli_result(cli_payload)
        raise RuntimeError(
            "share-card admin capture failed: "
            f"returnCode={process.returncode}, stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        )

    manifest = json.loads((sample_root / "captures" / "admin-share-card-screenshot-capture.json").read_text(encoding="utf-8"))
    write_summary(sample_root, source_summary, source_sample_selection_mode, manifest)

    cli_payload = build_cli_result_payload(
        sample_root=sample_root,
        source_summary=source_summary,
        source_sample_selection_mode=source_sample_selection_mode,
        status="success",
        captures=[item["name"] for item in manifest.get("captures") or []],
        stdout_log_path=stdout_log_path,
        stderr_log_path=stderr_log_path,
    )
    write_result_json(sample_root, cli_payload)
    print_cli_result(cli_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
