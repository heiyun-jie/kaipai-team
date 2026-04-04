import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-admin-verify-screenshots.py"


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
    user_id = context.get("userId")
    verification_id = context.get("verificationId")
    retry_verification_id = context.get("retryVerificationId")
    real_name = context.get("realName")
    if not user_id or not verification_id or not retry_verification_id or not real_name:
        raise RuntimeError(f"source sample missing userId/verification ids/realName: {sample_dir}")
    return {
        "sampleId": sample_dir.name,
        "userId": str(user_id),
        "verificationId": str(verification_id),
        "retryVerificationId": str(retry_verification_id),
        "realName": str(real_name),
    }


def write_summary(sample_root: Path, source_summary: dict, manifest: dict) -> None:
    lines = [
        f"# Verify Admin Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- Proxy URL: `{manifest.get('proxyUrl')}`",
        f"- Local Admin URL: `{manifest.get('localAdminUrl')}`",
        f"- Source Verify Sample: `{source_summary['sampleId']}`",
        "",
        "## Entity IDs",
        "",
        f"- Actor User ID: `{source_summary['userId']}`",
        f"- First Verification ID: `{source_summary['verificationId']}`",
        f"- Retry Verification ID: `{source_summary['retryVerificationId']}`",
        f"- Real Name: `{source_summary['realName']}`",
        "",
        "## Captures",
        "",
    ]

    for item in manifest.get("captures") or []:
        if item.get("detailScreenshotPath"):
            lines.append(
                f"- `{item['name']}` -> route=`{item['route']}` list=`{Path(item['listScreenshotPath']).name}` detail=`{Path(item['detailScreenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}` rows=`{item.get('rowCount')}`"
            )
            continue
        lines.append(
            f"- `{item['name']}` -> route=`{item['route']}` screenshot=`{Path(item['listScreenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}` rows=`{item.get('rowCount')}`"
        )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `captures/admin-verify-screenshot-capture.json`",
            "- `captures/admin-verify-screenshot-capture.stdout.log`",
            "- `captures/admin-verify-screenshot-capture.stderr.log`",
            "- `captures/admin-local-vite.log`",
            "- `captures/page-data-admin-verify-pending-empty.json`",
            "- `captures/page-data-admin-verify-history.json`",
            "- `screenshots/admin-verify-pending-empty.png`",
            "- `screenshots/admin-verify-history.png`",
            "- `screenshots/admin-verify-history-detail.png`",
            "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    explicit_source_sample = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else None
    label = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "verify-admin-page-evidence"

    source_sample_dir = resolve_source_sample(explicit_source_sample)
    source_summary = load_source_summary(source_sample_dir)

    sample_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)
    ensure_dir(sample_root / "captures")

    stdout_log_path = sample_root / "captures" / "admin-verify-screenshot-capture.stdout.log"
    stderr_log_path = sample_root / "captures" / "admin-verify-screenshot-capture.stderr.log"

    command = [
        "python",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        source_summary["userId"],
        source_summary["realName"],
        source_summary["retryVerificationId"],
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
            "verify admin capture failed: "
            f"returnCode={process.returncode}, stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        )

    manifest = json.loads((sample_root / "captures" / "admin-verify-screenshot-capture.json").read_text(encoding="utf-8"))
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
