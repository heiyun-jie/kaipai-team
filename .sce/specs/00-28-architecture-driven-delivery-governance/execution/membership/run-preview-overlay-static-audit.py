import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SAMPLES_ROOT = SCRIPT_DIR / "samples"
FRONTEND_SRC_ROOT = SCRIPT_DIR.parents[4] / "kaipai-frontend" / "src"

SCANNED_SUFFIXES = {".ts", ".vue"}
SESSION_KEY_LITERAL = "kp:personalization-preview-overlay-session"

HELPER_ALLOWED_FILES = {
    "PersonalizationPreviewOverlay": {
        "types/personalization.ts",
        "utils/personalization.ts",
        "pkg-card/actor-card/index.vue",
        "pages/actor-profile/detail.vue",
        "pkg-card/invite/index.vue",
    },
    "readPersonalizationPreviewOverlaySession": {
        "utils/personalization.ts",
        "pkg-card/actor-card/index.vue",
        "pages/actor-profile/detail.vue",
        "pkg-card/invite/index.vue",
    },
    "writePersonalizationPreviewOverlaySession": {
        "utils/personalization.ts",
        "pkg-card/actor-card/index.vue",
    },
    "diffPersonalizationPreviewOverlay": {
        "utils/personalization.ts",
        "pkg-card/actor-card/index.vue",
    },
    "applyPersonalizationPreviewOverlay": {
        "utils/personalization.ts",
        "pkg-card/actor-card/index.vue",
        "pages/actor-profile/detail.vue",
        "pkg-card/invite/index.vue",
    },
}

QUERY_KEY_LITERALS = {
    "previewLayout",
    "previewPrimary",
    "previewAccent",
    "previewBackground",
}


@dataclass
class Finding:
    rule_id: str
    file: str
    line: int
    text: str


def iter_source_files() -> list[Path]:
    return sorted(
        [
            path
            for path in FRONTEND_SRC_ROOT.rglob("*")
            if path.is_file() and path.suffix in SCANNED_SUFFIXES
        ]
    )


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative_path(path: Path) -> str:
    return path.relative_to(FRONTEND_SRC_ROOT).as_posix()


def iter_matches(text: str, pattern: str):
    compiled = re.compile(pattern)
    for match in compiled.finditer(text):
        yield match


def line_number_at(text: str, start_index: int) -> int:
    return text.count("\n", 0, start_index) + 1


def build_touchpoint_inventory() -> dict[str, list[dict]]:
    inventory: dict[str, list[dict]] = {name: [] for name in HELPER_ALLOWED_FILES}
    for path in iter_source_files():
        file_text = read_file(path)
        rel_path = relative_path(path)
        for helper_name in HELPER_ALLOWED_FILES:
            for match in iter_matches(file_text, rf"\b{re.escape(helper_name)}\b"):
                inventory[helper_name].append(
                    {
                        "file": rel_path,
                        "line": line_number_at(file_text, match.start()),
                    }
                )
    return inventory


def audit_query_key_literals() -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_source_files():
        rel_path = relative_path(path)
        file_text = read_file(path)
        for literal in QUERY_KEY_LITERALS:
            for match in iter_matches(file_text, re.escape(literal)):
                line = line_number_at(file_text, match.start())
                line_text = file_text.splitlines()[line - 1].strip()
                findings.append(
                    Finding(
                        rule_id="overlay_query_key_leak",
                        file=rel_path,
                        line=line,
                        text=line_text,
                    )
                )
    return findings


def audit_session_storage_key_literal() -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_source_files():
        rel_path = relative_path(path)
        if rel_path == "utils/personalization.ts":
            continue
        file_text = read_file(path)
        for match in iter_matches(file_text, re.escape(SESSION_KEY_LITERAL)):
            line = line_number_at(file_text, match.start())
            line_text = file_text.splitlines()[line - 1].strip()
            findings.append(
                Finding(
                    rule_id="overlay_session_key_leak",
                    file=rel_path,
                    line=line,
                    text=line_text,
                )
            )
    return findings


def audit_helper_usage(inventory: dict[str, list[dict]]) -> list[Finding]:
    findings: list[Finding] = []
    for helper_name, matches in inventory.items():
        allowed_files = HELPER_ALLOWED_FILES[helper_name]
        for item in matches:
            if item["file"] not in allowed_files:
                file_text = read_file(FRONTEND_SRC_ROOT / item["file"])
                line_text = file_text.splitlines()[item["line"] - 1].strip()
                findings.append(
                    Finding(
                        rule_id=f"overlay_helper_out_of_bounds:{helper_name}",
                        file=item["file"],
                        line=item["line"],
                        text=line_text,
                    )
                )
    return findings


def group_inventory_by_file(inventory: dict[str, list[dict]]) -> dict[str, list[str]]:
    by_file: dict[str, list[str]] = {}
    for helper_name, items in inventory.items():
        for item in items:
            by_file.setdefault(item["file"], [])
            if helper_name not in by_file[item["file"]]:
                by_file[item["file"]].append(helper_name)
    return dict(sorted(by_file.items()))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_summary(path: Path, payload: dict) -> None:
    lines = [
        f"# Preview Overlay Static Audit {path.parent.name}",
        "",
        f"- Generated At: `{payload['generatedAt']}`",
        f"- Frontend Root: `{payload['frontendRoot']}`",
        f"- Passed: `{payload['passed']}`",
        f"- Total Findings: `{payload['findingCount']}`",
        "",
        "## Rules",
        "",
        f"- Query key literals `{sorted(QUERY_KEY_LITERALS)}` must not appear anywhere in frontend runtime code",
        f"- Session storage literal `{SESSION_KEY_LITERAL}` only allowed in `utils/personalization.ts`",
        "- Preview overlay helpers must stay within the approved file set",
        "",
        "## Touchpoints",
        "",
    ]

    for file_name, helpers in payload["touchpointsByFile"].items():
        lines.append(f"- `{file_name}` -> helpers=`{', '.join(helpers)}`")

    lines.extend(["", "## Findings", ""])
    if payload["findings"]:
        for item in payload["findings"]:
            lines.append(
                f"- `{item['ruleId']}` -> file=`{item['file']}` line=`{item['line']}` text=`{item['text']}`"
            )
    else:
        lines.append("- No findings")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `captures/preview-overlay-static-audit.json`",
            "- `summary.md`",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    label = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "preview-overlay-static-audit"

    sample_root = SAMPLES_ROOT / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{label}"
    captures_root = sample_root / "captures"
    captures_root.mkdir(parents=True, exist_ok=True)

    inventory = build_touchpoint_inventory()
    findings = [
        *audit_query_key_literals(),
        *audit_session_storage_key_literal(),
        *audit_helper_usage(inventory),
    ]
    findings_payload = [
        {
            "ruleId": item.rule_id,
            "file": item.file,
            "line": item.line,
            "text": item.text,
        }
        for item in sorted(findings, key=lambda current: (current.file, current.line, current.rule_id))
    ]
    payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "frontendRoot": str(FRONTEND_SRC_ROOT),
        "passed": not findings_payload,
        "findingCount": len(findings_payload),
        "findings": findings_payload,
        "touchpointsByFile": group_inventory_by_file(inventory),
        "touchpointInventory": inventory,
        "rules": {
            "queryKeyLiterals": sorted(QUERY_KEY_LITERALS),
            "sessionKeyLiteral": SESSION_KEY_LITERAL,
            "helperAllowedFiles": {key: sorted(value) for key, value in HELPER_ALLOWED_FILES.items()},
        },
    }

    write_json(captures_root / "preview-overlay-static-audit.json", payload)
    write_summary(sample_root / "summary.md", payload)
    print(json.dumps({"sampleRoot": str(sample_root), "passed": payload["passed"], "findingCount": payload["findingCount"]}, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
