import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
DIAGNOSTICS_DIR = RUNBOOK_DIR / "records" / "diagnostics"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_MYSQL_DATABASE = "kaipai_dev"
DEFAULT_MYSQL_CONTAINER = "kaipai-mysql"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"

PAGE_ONLY_FILTER_SQL = """
FROM actor_ai_profile_card_task t
JOIN actor_ai_profile_card_page p
  ON p.task_id = t.task_id
WHERE t.deleted = 0
  AND p.deleted = 0
  AND t.status = 'success'
  AND t.share_card_id IS NOT NULL
  AND TRIM(COALESCE(t.generated_image_url, '')) = ''
  AND p.status = 'success'
  AND p.page_type = 'cover'
  AND p.page_no = 1
  AND TRIM(COALESCE(p.generated_image_url, '')) <> ''
  AND COALESCE(LOWER(t.provider_code), '') <> 'mock'
  AND (
    p.share_card_id IS NULL
    OR p.share_card_id = t.share_card_id
  )
  AND (
    TRIM(COALESCE(t.source_image_url, '')) = ''
    OR SUBSTRING_INDEX(TRIM(p.generated_image_url), '?', 1)
        <> SUBSTRING_INDEX(TRIM(t.source_image_url), '?', 1)
  )
""".strip()

SAMPLE_COLUMNS_SQL = """
  t.task_id,
  t.user_id,
  t.share_card_id AS task_share_card_id,
  p.share_card_id AS page_share_card_id,
  t.status AS task_status,
  p.status AS page_status,
  t.source_image_url,
  p.generated_image_url AS cover_generated_image_url,
  t.create_time
""".strip()

SAMPLE_HEADER = [
    "task_id",
    "user_id",
    "task_share_card_id",
    "page_share_card_id",
    "task_status",
    "page_status",
    "source_image_url",
    "cover_generated_image_url",
    "create_time",
]


@dataclass
class InventoryContext:
    capture_id: str
    operator: str
    host: str
    user: str
    identity_file: Path
    mysql_database: str
    mysql_container: str
    sample_limit: int
    output_dir: Path
    template_only: bool


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def resolve_executable(name: str) -> str:
    if os.name == "nt":
        resolved = shutil.which(f"{name}.exe") or shutil.which(f"{name}.cmd") or shutil.which(name)
    else:
        resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required executable not found: {name}")
    return resolved


def run_process(command: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    return subprocess.run(
        command,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ssh_base(context: InventoryContext) -> list[str]:
    ssh = resolve_executable("ssh")
    return [
        ssh,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{context.user}@{context.host}",
    ]


def scp_base(context: InventoryContext) -> list[str]:
    scp = resolve_executable("scp")
    return [
        scp,
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(context: InventoryContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: InventoryContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: InventoryContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "ai-profile-card-page-only-inventory"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def assert_read_only_sql(sql: str) -> None:
    normalized = re.sub(r"\s+", " ", sql.upper())
    for keyword in ["INSERT", "UPDATE", "DELETE", "REPLACE", "ALTER", "DROP", "CREATE", "TRUNCATE", "CALL", "LOAD"]:
        if re.search(rf"\b{keyword}\b", normalized):
            raise RuntimeError(f"inventory SQL must remain read-only; found keyword: {keyword}")


def build_count_sql() -> str:
    return f"""
SELECT COUNT(*) AS page_only_cover_count
{PAGE_ONLY_FILTER_SQL};
""".strip()


def build_sample_sql(sample_limit: int) -> str:
    return f"""
SELECT
{SAMPLE_COLUMNS_SQL}
{PAGE_ONLY_FILTER_SQL}
ORDER BY t.create_time DESC
LIMIT {sample_limit};
""".strip()


def build_inventory_sql(sample_limit: int) -> str:
    header = "\\t".join(SAMPLE_HEADER)
    return f"""
SELECT CONCAT('PAGE_ONLY_COVER_COUNT=', COUNT(*)) AS inventory_marker
{PAGE_ONLY_FILTER_SQL};

SELECT 'SAMPLE_TSV={header}' AS inventory_marker
UNION ALL
SELECT CONCAT(
  'SAMPLE_TSV=',
  CONCAT_WS(
    '\\t',
    COALESCE(CAST(sample.task_id AS CHAR), ''),
    COALESCE(CAST(sample.user_id AS CHAR), ''),
    COALESCE(CAST(sample.task_share_card_id AS CHAR), ''),
    COALESCE(CAST(sample.page_share_card_id AS CHAR), ''),
    COALESCE(sample.task_status, ''),
    COALESCE(sample.page_status, ''),
    COALESCE(sample.source_image_url, ''),
    COALESCE(sample.cover_generated_image_url, ''),
    COALESCE(DATE_FORMAT(sample.create_time, '%Y-%m-%d %H:%i:%s'), '')
  )
) AS inventory_marker
FROM (
  SELECT
{indent_sql(SAMPLE_COLUMNS_SQL, 4)}
  {PAGE_ONLY_FILTER_SQL}
  ORDER BY t.create_time DESC
  LIMIT {sample_limit}
) sample;
""".strip()


def indent_sql(sql: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in sql.splitlines())


def extract_section(output: str, field: str) -> str | None:
    begin = f"__{field}_BEGIN__"
    end = f"__{field}_END__"
    start = output.find(begin)
    stop = output.find(end)
    if start == -1 or stop == -1 or stop < start:
        return None
    content_start = start + len(begin)
    return output[content_start:stop].strip("\r\n")


def parse_helper_output(output: str) -> dict[str, str]:
    required_fields = [
        "REMOTE_DATE",
        "MYSQL_MODE",
        "MYSQL_DATABASE",
        "MYSQL_CONTAINER",
        "MYSQL_RESULT",
        "FINAL_STATUS",
        "FAIL_REASON",
    ]
    summary: dict[str, str] = {}
    for field in required_fields:
        section = extract_section(output, field)
        if section is None:
            raise RuntimeError(f"missing helper output section: {field}")
        summary[field] = section
    return summary


def clean_marker_value(value: str) -> str:
    return value.strip().strip("|").strip()


def parse_inventory_result(raw_mysql_output: str) -> tuple[int, list[str]]:
    count: int | None = None
    sample_lines: list[str] = []
    for line in raw_mysql_output.splitlines():
        if "PAGE_ONLY_COVER_COUNT=" in line:
            value = clean_marker_value(line.split("PAGE_ONLY_COVER_COUNT=", 1)[1])
            count = int(value)
        if "SAMPLE_TSV=" in line:
            value = clean_marker_value(line.split("SAMPLE_TSV=", 1)[1])
            sample_lines.append(value)
    if count is None:
        raise RuntimeError("PAGE_ONLY_COVER_COUNT marker not found in mysql output")
    if not sample_lines:
        sample_lines.append("\t".join(SAMPLE_HEADER))
    return count, sample_lines


def upload_and_run_inventory_sql(context: InventoryContext, inventory_sql: str) -> dict[str, str]:
    assert_read_only_sql(inventory_sql)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
        handle.write(inventory_sql)
        handle.write("\n")
        local_sql_path = Path(handle.name)
    try:
        remote_dir = f"/home/{context.user}/backend-diagnostics/{context.capture_id}"
        remote_sql_path = f"{remote_dir}/ai-profile-card-page-only-inventory.sql"
        run_ssh(context, f"mkdir -p {shlex.quote(remote_dir)}")
        run_process(scp_base(context) + [str(local_sql_path), f"{context.user}@{context.host}:{remote_sql_path}"])
        helper_command = (
            f"sudo -n {REMOTE_HELPER_PATH} "
            f"--mysql-validation "
            f"--mysql-script-path {shlex.quote(remote_sql_path)} "
            f"--mysql-database {shlex.quote(context.mysql_database)} "
            f"--mysql-container {shlex.quote(context.mysql_container)}"
        )
        write_text(context.output_dir / "remote-helper-command.txt", helper_command + "\n")
        result = run_ssh(context, helper_command)
        if result.stderr and result.stderr.strip():
            log(f"remote stderr> {result.stderr.strip()}")
        summary = parse_helper_output(result.stdout)
        if summary["FINAL_STATUS"] != "passed":
            raise RuntimeError(f"remote mysql validation failed: {summary['FAIL_REASON']}")
        return summary
    finally:
        try:
            local_sql_path.unlink(missing_ok=True)
        except UnboundLocalError:
            pass


def write_readme(context: InventoryContext, metadata: dict[str, Any]) -> None:
    status = metadata["status"]
    count = metadata.get("pageOnlyCoverCount")
    sample_rows = metadata.get("sampleRows")
    review = metadata.get("review", {})
    content = f"""# AI Profile Card Page-Only Inventory Evidence

## 1. Scope

- Spec: `00-171-current-phase-ai-profile-card-single-cover-theme-flow`
- Capture ID: `{context.capture_id}`
- Status: `{status}`
- Operator: `{context.operator}`
- Host: `{context.host}`
- MySQL database: `{context.mysql_database}`
- MySQL container: `{context.mysql_container}`
- Approval session: `{metadata.get('approvalSession', 'pending')}`

## 2. Result

- `page_only_cover_count`: `{count if count is not None else 'not-executed'}`
- Sample rows: `{sample_rows if sample_rows is not None else 'not-executed'}`
- Completion evidence status: `{metadata.get('completionEvidenceStatus', 'pending-human-review')}`

## 3. Human Review

- Reviewed by: `{review.get('reviewedBy', 'pending')}`
- Sample rows reviewed: `{review.get('sampleRowsReviewed', 'no')}`
- Review conclusion: `{review.get('reviewConclusion', 'pending')}`
- Fallback removal approved: `{review.get('fallbackRemovalApproved', 'no')}`

Fill these fields in a follow-up review note or update this record after target-environment execution. `status=executed` only means the read-only inventory query ran; it is not a completion approval.

## 4. Completion Gate

This record can support closing the Phase 5 page-only data item only if it was executed against the target environment and either:

- `page_only_cover_count = 0`, or
- a reviewed backfill/re-host operation has run and a post-run inventory count is `0`.

Do not remove the frontend legacy `pages` fallback from this record alone when the count is non-zero or when this is a template-only record.
"""
    write_text(context.output_dir / "README.md", content)


def write_initial_files(context: InventoryContext, count_sql: str, sample_sql: str, inventory_sql: str) -> None:
    ensure_dir(context.output_dir)
    write_text(context.output_dir / "query-count.sql", count_sql + "\n")
    write_text(context.output_dir / "query-sample.sql", sample_sql + "\n")
    write_text(context.output_dir / "query-inventory.sql", inventory_sql + "\n")


def write_summary(context: InventoryContext, metadata: dict[str, Any]) -> None:
    write_text(context.output_dir / "summary.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    write_readme(context, metadata)


def collect(context: InventoryContext) -> dict[str, Any]:
    count_sql = build_count_sql()
    sample_sql = build_sample_sql(context.sample_limit)
    inventory_sql = build_inventory_sql(context.sample_limit)
    assert_read_only_sql(inventory_sql)
    write_initial_files(context, count_sql, sample_sql, inventory_sql)

    metadata: dict[str, Any] = {
        "captureId": context.capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "status": "template-only" if context.template_only else "pending",
        "operator": context.operator,
        "host": context.host,
        "user": context.user,
        "mysqlDatabase": context.mysql_database,
        "mysqlContainer": context.mysql_container,
        "sampleLimit": context.sample_limit,
        "pageOnlyCoverCount": None,
        "sampleRows": None,
        "approvalSession": "pending",
        "completionEvidenceStatus": "pending-human-review",
        "review": {
            "reviewedBy": "pending",
            "sampleRowsReviewed": "no",
            "reviewConclusion": "pending",
            "fallbackRemovalApproved": "no",
        },
        "files": {
            "countQuery": "query-count.sql",
            "sampleQuery": "query-sample.sql",
            "inventoryQuery": "query-inventory.sql",
            "remoteHelperCommand": None if context.template_only else "remote-helper-command.txt",
            "rawMysqlOutput": None if context.template_only else "raw-mysql-output.txt",
            "countResult": None if context.template_only else "result-count.txt",
            "sampleTsv": None if context.template_only else "sample.tsv",
            "summary": "summary.json",
            "readme": "README.md",
        },
        "completionGate": (
            "target-environment evidence is required before marking Phase 5 page-only data inventory complete"
        ),
    }

    if context.template_only:
        write_summary(context, metadata)
        return metadata

    require_key_auth(context)
    require_helper(context)
    helper_summary = upload_and_run_inventory_sql(context, inventory_sql)
    raw_mysql_output = helper_summary["MYSQL_RESULT"]
    page_only_count, sample_lines = parse_inventory_result(raw_mysql_output)

    write_text(context.output_dir / "raw-mysql-output.txt", raw_mysql_output + "\n")
    write_text(context.output_dir / "result-count.txt", f"{page_only_count}\n")
    write_text(context.output_dir / "sample.tsv", "\n".join(sample_lines) + "\n")

    metadata.update(
        {
            "status": "executed",
            "helperFinalStatus": helper_summary["FINAL_STATUS"],
            "remoteDate": helper_summary["REMOTE_DATE"],
            "mysqlMode": helper_summary["MYSQL_MODE"],
            "pageOnlyCoverCount": page_only_count,
            "sampleRows": max(0, len(sample_lines) - 1),
        }
    )
    write_summary(context, metadata)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read legacy AI profile-card page-only inventory through the standard backend release helper.",
    )
    parser.add_argument("--label", default="ai-profile-card-page-only-inventory")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--mysql-database", default=DEFAULT_MYSQL_DATABASE)
    parser.add_argument("--mysql-container", default=DEFAULT_MYSQL_CONTAINER)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="write the evidence directory and SQL files without connecting to the target environment",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_limit < 1 or args.sample_limit > 500:
        raise RuntimeError("--sample-limit must be between 1 and 500")
    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    context = InventoryContext(
        capture_id=capture_id,
        operator=args.operator,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        mysql_database=args.mysql_database,
        mysql_container=args.mysql_container,
        sample_limit=args.sample_limit,
        output_dir=DIAGNOSTICS_DIR / capture_id,
        template_only=args.template_only,
    )
    metadata = collect(context)
    log(f"ai profile-card page-only inventory record saved: {context.output_dir}")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
