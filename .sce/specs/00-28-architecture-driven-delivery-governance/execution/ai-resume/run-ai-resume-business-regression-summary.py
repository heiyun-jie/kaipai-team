import json
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_sample(sample_id: str) -> Path:
    candidate = SAMPLES_ROOT / sample_id
    if not candidate.exists():
        raise RuntimeError(f"sample not found: {sample_id}")
    return candidate


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_file(path: Path) -> Path:
    if not path.exists():
        raise RuntimeError(f"required file missing: {path}")
    return path


def find_check(payload: dict, name: str) -> dict | None:
    for item in ((payload.get("summary") or {}).get("checks") or []):
        if item.get("name") == name:
            return item
    return None


def require_pass(payload: dict, name: str) -> dict:
    item = find_check(payload, name)
    if item is None:
        raise RuntimeError(f"check not found: {name}")
    if not item.get("passed"):
        raise RuntimeError(f"check not passed: {name}")
    return item


def extract_page_source_sample(summary_text: str) -> str | None:
    marker = "- Source AI Sample: `"
    for line in summary_text.splitlines():
        if line.startswith(marker) and line.endswith("`"):
            return line[len(marker):-1]
    return None


def load_business_inputs(validation_sample_id: str, page_sample_id: str) -> dict:
    validation_dir = resolve_sample(validation_sample_id)
    page_dir = resolve_sample(page_sample_id)

    validation_results = load_json(require_file(validation_dir / "results.json"))
    page_manifest = load_json(require_file(page_dir / "captures" / "mini-program-screenshot-capture.json"))
    page_summary_text = require_file(page_dir / "summary.md").read_text(encoding="utf-8")

    source_sample = extract_page_source_sample(page_summary_text)
    if source_sample != validation_sample_id:
        raise RuntimeError(
            f"page evidence source sample mismatch: expected={validation_sample_id}, actual={source_sample}"
        )

    require_pass(validation_results, "polish-success")
    require_pass(validation_results, "profile-reflects-applied-patches")
    require_pass(validation_results, "history-recorded")
    require_pass(validation_results, "rollback-restores-fields")

    captures = page_manifest.get("captures") or []
    capture_names = [item.get("name") for item in captures]
    expected_capture_names = [
        "actor-card",
        "actor-profile-edit",
        "actor-profile-edit-ai-panel",
        "actor-profile-detail",
    ]
    if capture_names != expected_capture_names:
        raise RuntimeError(f"unexpected capture sequence: {capture_names}")
    if any((item.get("screenshotMethod") != "automator") for item in captures):
        raise RuntimeError("page evidence contains non-automator screenshot")

    visual_review = page_manifest.get("visualReview") or {}
    if bool(visual_review.get("visualDidNotRefresh")):
        raise RuntimeError("page evidence visualDidNotRefresh=true")

    return {
        "validationDir": validation_dir,
        "pageDir": page_dir,
        "validationResults": validation_results,
        "pageManifest": page_manifest,
        "sourceSample": source_sample,
        "captureNames": capture_names,
    }


def write_summary(sample_root: Path, sample_id: str, inputs: dict) -> None:
    validation_summary = inputs["validationResults"]["summary"]
    page_manifest = inputs["pageManifest"]
    visual_review = page_manifest.get("visualReview") or {}

    lines = [
        f"# AI Resume Business Regression Summary {sample_id}",
        "",
        f"- Generated At: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Validation Sample: `{inputs['validationDir'].name}`",
        f"- Mini Program Page Sample: `{inputs['pageDir'].name}`",
        "",
        "## Key IDs",
        "",
        f"- Actor User ID: `{validation_summary.get('actorUserId')}`",
        f"- Success Request ID: `{validation_summary.get('successRequestId')}`",
        f"- Draft ID: `{validation_summary.get('draftId')}`",
        f"- History ID: `{validation_summary.get('historyId')}`",
        "",
        "## API Regression",
        "",
    ]

    for check_name in [
        "polish-success",
        "profile-reflects-applied-patches",
        "history-recorded",
        "rollback-restores-fields",
    ]:
        item = require_pass(inputs["validationResults"], check_name)
        lines.append(f"- `{check_name}`: {item.get('detail')}")

    lines.extend([
        "",
        "## Page Regression",
        "",
        f"- Capture Names: `{', '.join(inputs['captureNames'])}`",
        f"- Unique Screenshot Hash Count: `{visual_review.get('uniqueScreenshotHashCount')}`",
        f"- Visual Did Not Refresh: `{visual_review.get('visualDidNotRefresh')}`",
        "",
        "## Artifacts",
        "",
        f"- Validation Summary: `{inputs['validationDir'].name}/summary.md`",
        f"- Validation Results: `{inputs['validationDir'].name}/results.json`",
        f"- Mini Program Summary: `{inputs['pageDir'].name}/summary.md`",
        f"- Mini Program Manifest: `{inputs['pageDir'].name}/captures/mini-program-screenshot-capture.json`",
        "- `results.json`",
    ])
    (sample_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("usage: run-ai-resume-business-regression-summary.py <validation-sample-id> <page-sample-id> [label]")

    validation_sample_id = sys.argv[1].strip()
    page_sample_id = sys.argv[2].strip()
    label = sys.argv[3].strip() if len(sys.argv) > 3 and sys.argv[3].strip() else "ai-business-regression-summary"

    inputs = load_business_inputs(validation_sample_id, page_sample_id)

    sample_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    sample_root = SAMPLES_ROOT / sample_id
    ensure_dir(sample_root)

    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "sampleId": sample_id,
        "sampleLabel": label,
        "validationSampleId": validation_sample_id,
        "pageSampleId": page_sample_id,
        "summary": {
            "actorUserId": (inputs["validationResults"].get("summary") or {}).get("actorUserId"),
            "successRequestId": (inputs["validationResults"].get("summary") or {}).get("successRequestId"),
            "draftId": (inputs["validationResults"].get("summary") or {}).get("draftId"),
            "historyId": (inputs["validationResults"].get("summary") or {}).get("historyId"),
            "captureNames": inputs["captureNames"],
            "visualReview": inputs["pageManifest"].get("visualReview") or {},
            "checks": [
                require_pass(inputs["validationResults"], "polish-success"),
                require_pass(inputs["validationResults"], "profile-reflects-applied-patches"),
                require_pass(inputs["validationResults"], "history-recorded"),
                require_pass(inputs["validationResults"], "rollback-restores-fields"),
            ],
        },
    }
    (sample_root / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(sample_root, sample_id, inputs)
    print(json.dumps({"sampleRoot": str(sample_root), "validationSampleId": validation_sample_id, "pageSampleId": page_sample_id}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
