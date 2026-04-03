import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-admin-ai-governance-screenshots.py"


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


def resolve_source_sample(explicit_sample_id: str | None) -> Path:
    if explicit_sample_id:
        candidate = SAMPLES_ROOT / explicit_sample_id
        if not candidate.exists():
            raise RuntimeError(f"source sample not found: {explicit_sample_id}")
        return candidate

    for candidate in list_sample_dirs():
        if (candidate / "results.json").exists():
            return candidate

    raise RuntimeError("no ai-resume validation sample with results.json found")


def load_source_summary(sample_dir: Path) -> dict:
    payload = json.loads((sample_dir / "results.json").read_text(encoding="utf-8"))
    summary = payload.get("summary") or {}
    actor_user_id = summary.get("actorUserId")
    history_id = summary.get("historyId")
    failure_id = summary.get("failureId")
    failure_request_id = summary.get("failureRequestId")
    if not actor_user_id or not history_id or not failure_id or not failure_request_id:
        raise RuntimeError(f"source sample missing actor/history/failure ids: {sample_dir}")
    return {
        "sampleId": payload.get("sampleId") or sample_dir.name,
        "sampleLabel": payload.get("sampleLabel") or sample_dir.name,
        "actorUserId": actor_user_id,
        "historyId": history_id,
        "failureId": failure_id,
        "failureRequestId": failure_request_id,
    }


def write_summary(sample_root: Path, source_summary: dict, manifest: dict) -> None:
    lines = [
        f"# AI Resume Admin Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- Proxy URL: `{manifest.get('proxyUrl')}`",
        f"- Local Admin URL: `{manifest.get('localAdminUrl')}`",
        f"- Source AI Sample: `{source_summary['sampleId']}`",
        "",
        "## Entity IDs",
        "",
        f"- Actor User ID: `{source_summary['actorUserId']}`",
        f"- History ID: `{source_summary['historyId']}`",
        f"- Failure ID: `{source_summary['failureId']}`",
        f"- Failure Request ID: `{source_summary['failureRequestId']}`",
        "",
        "## Captures",
        "",
    ]

    for item in manifest.get("captures") or []:
        if item["name"] == "admin-ai-governance-overview":
            lines.append(
                f"- `{item['name']}` -> route=`{item['route']}` screenshot=`{Path(item['screenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}`"
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
            "- `captures/admin-ai-governance-screenshot-capture.json`",
            "- `captures/admin-ai-governance-screenshot-capture.stdout.log`",
            "- `captures/admin-ai-governance-screenshot-capture.stderr.log`",
            "- `captures/admin-local-vite.log`",
            "- `captures/page-data-admin-ai-governance-overview.json`",
            "- `captures/page-data-admin-ai-governance-history-detail.json`",
            "- `captures/page-data-admin-ai-governance-failure-detail.json`",
            "- `screenshots/admin-ai-governance-overview.png`",
            "- `screenshots/admin-ai-governance-history-list.png`",
            "- `screenshots/admin-ai-governance-history-detail.png`",
            "- `screenshots/admin-ai-governance-failure-list.png`",
            "- `screenshots/admin-ai-governance-failure-detail.png`",
            "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    explicit_source_sample = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else None
    label = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "ai-admin-page-evidence"

    source_sample_dir = resolve_source_sample(explicit_source_sample)
    source_summary = load_source_summary(source_sample_dir)

    sample_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)
    ensure_dir(sample_root / "captures")

    stdout_log_path = sample_root / "captures" / "admin-ai-governance-screenshot-capture.stdout.log"
    stderr_log_path = sample_root / "captures" / "admin-ai-governance-screenshot-capture.stderr.log"

    command = [
        "python",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        str(source_summary["historyId"]),
        str(source_summary["failureId"]),
        str(source_summary["failureRequestId"]),
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
        raise RuntimeError(
            "ai admin capture failed: "
            f"returnCode={process.returncode}, stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        )

    manifest = json.loads((sample_root / "captures" / "admin-ai-governance-screenshot-capture.json").read_text(encoding="utf-8"))
    write_summary(sample_root, source_summary, manifest)

    print(
        json.dumps(
            {
                "sampleRoot": str(sample_root),
                "sourceSample": source_summary["sampleId"],
                "captures": [item["name"] for item in manifest.get("captures") or []],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
