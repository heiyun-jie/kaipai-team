import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CHAIN_SCRIPT = SCRIPT_DIR / "run-admin-template-rollback-mini-program-chain.py"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_source_sample(explicit_sample_id: str | None) -> Path:
    if explicit_sample_id:
        candidate = SAMPLES_ROOT / explicit_sample_id
        if not candidate.exists():
            raise RuntimeError(f"source sample not found: {explicit_sample_id}")
        return candidate

    default_candidate = SAMPLES_ROOT / "20260402-212713-dev-fortune-theme-lv5-unlock"
    if default_candidate.exists():
        return default_candidate

    raise RuntimeError("default source sample not found for no-fortune-theme rollback evidence")


def write_summary(sample_root: Path, source_sample: str, stdout_text: str) -> None:
    lines = [
        f"# Admin Template Rollback Mini Program No Fortune Theme {sample_root.name}",
        "",
        f"- Generated At: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Source Sample: `{source_sample}`",
        f"- Chain Script: `{CHAIN_SCRIPT.name}`",
        f"- Mode: `force-disable-fortune-theme + restore-original-fortune-theme`",
        "",
        "## Artifacts",
        "",
        "- `captures/no-fortune-theme-chain.stdout.log`",
        "- `captures/no-fortune-theme-chain.stderr.log`",
        "- `captures/admin-template-rollback-mini-program-results.json`",
        "- `captures/admin-template-rollback-mini-program-db.txt`",
        "- `captures/mini-program-screenshot-capture-before-rollback.json`",
        "- `captures/mini-program-screenshot-capture-after-rollback.json`",
        "- `captures/mini-program-screenshot-capture-after-restore.json`",
        "- `admin-template-rollback-mini-program-summary.md`",
        "",
        "## Chain Output",
        "",
        "```json",
        stdout_text.strip() or "{}",
        "```",
        "",
    ]
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    explicit_source_sample = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else None
    source_sample_dir = resolve_source_sample(explicit_source_sample)

    sample_root = SAMPLES_ROOT / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-dev-template-rollback-no-fortune-theme"
    ensure_dir(sample_root / "captures")
    ensure_dir(sample_root / "screenshots")

    stdout_log_path = sample_root / "captures" / "no-fortune-theme-chain.stdout.log"
    stderr_log_path = sample_root / "captures" / "no-fortune-theme-chain.stderr.log"
    command = [
        "python",
        str(CHAIN_SCRIPT),
        str(sample_root),
        "--force-disable-fortune-theme",
        "--restore-original-fortune-theme",
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
            "no-fortune-theme rollback chain failed: "
            f"returnCode={process.returncode}, stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        )

    write_summary(sample_root, source_sample_dir.name, stdout_text)
    print(
        json.dumps(
            {
                "sampleRoot": str(sample_root),
                "sourceSample": source_sample_dir.name,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
