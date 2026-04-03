import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
CAPTURE_SCRIPT = SCRIPT_DIR / "capture-admin-recruit-screenshots.py"


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

    raise RuntimeError("no recruit sample with results.json found")


def load_source_summary(sample_dir: Path) -> dict:
    payload = json.loads((sample_dir / "results.json").read_text(encoding="utf-8"))
    summary = payload.get("summary") or {}
    actor_user_id = summary.get("actorUserId")
    project_id = summary.get("projectId")
    role_id = summary.get("roleId")
    apply_id = summary.get("applyId")
    sample_label = payload.get("sampleLabel")
    if not actor_user_id or not project_id or not role_id or not apply_id or not sample_label:
        raise RuntimeError(f"source sample missing ids or sampleLabel: {sample_dir}")
    return {
        "sampleId": payload.get("sampleId") or sample_dir.name,
        "sampleLabel": sample_label,
        "actorUserId": actor_user_id,
        "projectId": project_id,
        "roleId": role_id,
        "applyId": apply_id,
    }


def write_summary(sample_root: Path, source_summary: dict, manifest: dict) -> None:
    lines = [
        f"# Recruit Admin Page Evidence {sample_root.name}",
        "",
        f"- Generated At: `{manifest.get('generatedAt')}`",
        f"- Base URL: `{manifest.get('baseUrl')}`",
        f"- Proxy URL: `{manifest.get('proxyUrl')}`",
        f"- Local Admin URL: `{manifest.get('localAdminUrl')}`",
        f"- Source Recruit Sample: `{source_summary['sampleId']}`",
        "",
        "## Entity IDs",
        "",
        f"- Actor User ID: `{source_summary['actorUserId']}`",
        f"- Project ID: `{source_summary['projectId']}`",
        f"- Role ID: `{source_summary['roleId']}`",
        f"- Apply ID: `{source_summary['applyId']}`",
        f"- Sample Label: `{source_summary['sampleLabel']}`",
        "",
        "## Captures",
        "",
    ]

    for item in manifest.get("captures") or []:
        lines.append(
            f"- `{item['name']}` -> route=`{item['route']}` filters=`{json.dumps(item.get('filters') or {}, ensure_ascii=False)}` list=`{Path(item['listScreenshotPath']).name}` detail=`{Path(item['detailScreenshotPath']).name}` pageData=`{Path(item['pageDataPath']).name}` rows=`{item.get('rowCount')}`"
        )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `captures/admin-recruit-screenshot-capture.json`",
            "- `captures/admin-recruit-screenshot-capture.stdout.log`",
            "- `captures/admin-recruit-screenshot-capture.stderr.log`",
            "- `captures/admin-local-vite.log`",
            "- `captures/page-data-admin-recruit-projects.json`",
            "- `captures/page-data-admin-recruit-roles.json`",
            "- `captures/page-data-admin-recruit-applies.json`",
            "- `screenshots/admin-recruit-projects.png`",
            "- `screenshots/admin-recruit-projects-detail.png`",
            "- `screenshots/admin-recruit-roles.png`",
            "- `screenshots/admin-recruit-roles-detail.png`",
            "- `screenshots/admin-recruit-applies.png`",
            "- `screenshots/admin-recruit-applies-detail.png`",
            "",
        ]
    )
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    explicit_source_sample = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else None
    label = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "recruit-admin-page-evidence"

    source_sample_dir = resolve_source_sample(explicit_source_sample)
    source_summary = load_source_summary(source_sample_dir)

    sample_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)
    ensure_dir(sample_root / "captures")

    stdout_log_path = sample_root / "captures" / "admin-recruit-screenshot-capture.stdout.log"
    stderr_log_path = sample_root / "captures" / "admin-recruit-screenshot-capture.stderr.log"

    command = [
        "python",
        str(CAPTURE_SCRIPT),
        str(sample_root),
        str(source_summary["projectId"]),
        str(source_summary["roleId"]),
        str(source_summary["applyId"]),
        str(source_summary["actorUserId"]),
        str(source_summary["sampleLabel"]),
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
            "recruit admin capture failed: "
            f"returnCode={process.returncode}, stdoutLog={stdout_log_path}, stderrLog={stderr_log_path}"
        )

    manifest = json.loads((sample_root / "captures" / "admin-recruit-screenshot-capture.json").read_text(encoding="utf-8"))
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
