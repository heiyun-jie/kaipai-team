import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


WS_ENDPOINT = "ws://127.0.0.1:9421"
DEFAULT_BASE_URL = "http://101.43.57.62/api"
SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-mini-program-screenshots.js"


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
        if (candidate / "closure-context.json").exists():
            return candidate

    raise RuntimeError("no verify closure sample with closure-context.json found")


def load_source_summary(sample_dir: Path) -> dict:
    payload = json.loads((sample_dir / "closure-context.json").read_text(encoding="utf-8"))
    context = payload.get("context") or {}
    phone = context.get("phone")
    user_id = context.get("userId")
    verification_id = context.get("verificationId")
    retry_verification_id = context.get("retryVerificationId")
    if not phone or not user_id or not verification_id or not retry_verification_id:
        raise RuntimeError(f"source sample missing phone/userId/verification ids: {sample_dir}")

    base_url = str(context.get("baseUrl") or DEFAULT_BASE_URL).strip().rstrip("/")
    if not base_url.endswith("/api"):
        base_url = f"{base_url}/api"

    return {
        "sampleId": sample_dir.name,
        "baseUrl": base_url,
        "environment": context.get("environment") or "unknown",
        "phone": str(phone),
        "userId": str(user_id),
        "verificationId": str(verification_id),
        "retryVerificationId": str(retry_verification_id),
    }


def write_summary(sample_root: Path, source_summary: dict, manifest: dict) -> None:
    lines = [
        f"# Verify Mini Program Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- WS Endpoint: `{manifest.get('wsEndpoint')}`",
        f"- Source Verify Sample: `{source_summary['sampleId']}`",
        "",
        "## Entity IDs",
        "",
        f"- Actor User ID: `{source_summary['userId']}`",
        f"- First Verification ID: `{source_summary['verificationId']}`",
        f"- Retry Verification ID: `{source_summary['retryVerificationId']}`",
        "",
        "## Captures",
        "",
    ]

    for item in manifest.get("captures") or []:
        lines.append(
            f"- `{item['name']}` -> path=`{item['actualPath']}` query=`{json.dumps(item.get('actualQuery') or {}, ensure_ascii=False)}` screenshot=`{Path(item['screenshotPath']).name}` method=`{item.get('screenshotMethod')}` pageData=`{Path(item['pageDataPath']).name}`"
        )

    lines.extend(
        [
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
            "- `captures/page-data-verify-page.json`",
            "- `screenshots/verify-page.png`",
            "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    explicit_source_sample = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else None
    label = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "verify-mini-program-page-evidence"

    source_sample_dir = resolve_source_sample(explicit_source_sample)
    source_summary = load_source_summary(source_sample_dir)

    sample_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)
    ensure_dir(sample_root / "captures")

    stdout_log_path = sample_root / "captures" / "mini-program-screenshot-capture.stdout.log"
    stderr_log_path = sample_root / "captures" / "mini-program-screenshot-capture.stderr.log"

    command = [
        "node",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        WS_ENDPOINT,
        source_summary["baseUrl"],
        source_summary["phone"],
        source_summary["userId"],
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
    stdout_text, stderr_text = process.communicate(timeout=420)
    stdout_log_path.write_text(stdout_text or "", encoding="utf-8")
    stderr_log_path.write_text(stderr_text or "", encoding="utf-8")

    if process.returncode != 0:
        raise RuntimeError(
            "verify mini program capture failed: "
            f"returnCode={process.returncode}, stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        )

    manifest = json.loads((sample_root / "captures" / "mini-program-screenshot-capture.json").read_text(encoding="utf-8"))
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
