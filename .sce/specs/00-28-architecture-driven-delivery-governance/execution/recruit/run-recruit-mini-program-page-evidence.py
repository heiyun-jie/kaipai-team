import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


WS_ENDPOINT = "ws://127.0.0.1:9421"
BASE_URL = "http://101.43.57.62/api"
USER_PHONE = "13800138000"
SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-mini-program-screenshots.js"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def list_sample_dirs() -> list[Path]:
    if not SAMPLES_ROOT.exists():
        return []
    return sorted([item for item in SAMPLES_ROOT.iterdir() if item.is_dir()], key=lambda item: item.stat().st_mtime, reverse=True)


def resolve_source_sample(explicit_sample_id: str | None) -> Path:
    if explicit_sample_id:
        candidate = SAMPLES_ROOT / explicit_sample_id
        if not candidate.exists():
            raise RuntimeError(f"source sample not found: {explicit_sample_id}")
        return candidate

    for candidate in list_sample_dirs():
        if (candidate / "results.json").exists():
            return candidate

    raise RuntimeError("no recruit sample with results.json found")


def load_source_summary(sample_dir: Path) -> dict:
    results_path = sample_dir / "results.json"
    if not results_path.exists():
        raise RuntimeError(f"source sample missing results.json: {sample_dir}")
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    summary = payload.get("summary") or {}
    actor_user_id = summary.get("actorUserId")
    role_id = summary.get("roleId")
    apply_id = summary.get("applyId")
    project_id = summary.get("projectId")
    if not actor_user_id or not role_id or not apply_id:
        raise RuntimeError(f"source sample missing actor/role/apply ids: {sample_dir}")
    return {
        "sampleId": payload.get("sampleId") or sample_dir.name,
        "actorUserId": actor_user_id,
        "projectId": project_id,
        "roleId": role_id,
        "applyId": apply_id,
    }


def write_summary(sample_root: Path, source_summary: dict, manifest: dict) -> None:
    captures = manifest.get("captures") or []
    lines = [
        f"# Recruit Mini Program Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- WS Endpoint: `{manifest.get('wsEndpoint')}`",
        f"- Source Recruit Sample: `{source_summary['sampleId']}`",
        "",
        "## Entity IDs",
        "",
        f"- Actor User ID: `{source_summary['actorUserId']}`",
        f"- Project ID: `{source_summary.get('projectId')}`",
        f"- Role ID: `{source_summary['roleId']}`",
        f"- Apply ID: `{source_summary['applyId']}`",
        "",
        "## Captures",
        "",
    ]
    for item in captures:
        screenshot_method = item.get("screenshotMethod") or "unknown"
        page_data_file = Path(item.get("pageDataPath") or "").name or "n/a"
        lines.append(
            f"- `{item['name']}` -> path=`{item['actualPath']}` query=`{json.dumps(item.get('actualQuery') or {}, ensure_ascii=False)}` screenshot=`{Path(item['screenshotPath']).name}` method=`{screenshot_method}` pageData=`{page_data_file}`"
        )
    lines.extend([
        "",
        "## Visual Review",
        "",
        f"- Unique Screenshot Hash Count: `{(manifest.get('visualReview') or {}).get('uniqueScreenshotHashCount')}`",
        f"- Unique Actual Path Count: `{(manifest.get('visualReview') or {}).get('uniqueActualPathCount')}`",
        f"- Visual Did Not Refresh: `{(manifest.get('visualReview') or {}).get('visualDidNotRefresh')}`",
        "",
        "## Artifacts",
        "",
        "- `captures/mini-program-screenshot-capture.json`",
        "- `captures/mini-program-capture-progress.log`",
        "- `captures/mini-program-screenshot-capture.stdout.log`",
        "- `captures/mini-program-screenshot-capture.stderr.log`",
        "- `captures/page-data-*.json`",
        "- `screenshots/crew-home-projects.png`",
        "- `screenshots/crew-apply-manage.png`",
        "- `screenshots/actor-home-archive.png`",
        "- `screenshots/actor-role-detail.png`",
        "- `screenshots/actor-apply-confirm.png`",
        "- `screenshots/actor-my-applies.png`",
        "- `screenshots/actor-apply-detail.png`",
        "",
    ])
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    explicit_source_sample = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else None
    label = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "recruit-mini-program-page-evidence"

    source_sample_dir = resolve_source_sample(explicit_source_sample)
    source_summary = load_source_summary(source_sample_dir)

    now = datetime.now()
    sample_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)
    capture_root = sample_root / "captures"
    ensure_dir(capture_root)
    stdout_log_path = capture_root / "mini-program-screenshot-capture.stdout.log"
    stderr_log_path = capture_root / "mini-program-screenshot-capture.stderr.log"

    command = [
        "node",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        WS_ENDPOINT,
        BASE_URL,
        USER_PHONE,
        str(source_summary["actorUserId"]),
        str(source_summary["roleId"]),
        str(source_summary["applyId"]),
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
        raise RuntimeError(
            "recruit mini program capture timed out: "
            f"stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        ) from exc

    stdout_log_path.write_text(stdout_text or "", encoding="utf-8")
    stderr_log_path.write_text(stderr_text or "", encoding="utf-8")

    if process.returncode != 0:
        raise RuntimeError(
            "recruit mini program capture failed: "
            f"returnCode={process.returncode}, stderrLog={stderr_log_path}, stdoutLog={stdout_log_path}"
        )

    manifest_path = sample_root / "captures" / "mini-program-screenshot-capture.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
