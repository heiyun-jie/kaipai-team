import argparse
import hashlib
import hmac
import http.client
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
DEFAULT_SECRET_FILE = ROOT / ".sce" / "config" / "local-secrets" / "cos-bucket.env"
DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_CONTAINER = "kaipai-backend"
DEFAULT_SOURCE_BUCKET = "kaipai-1412601014"
DEFAULT_TARGET_BUCKET = "kaipai-prod-1412601014"
DEFAULT_REGION = "ap-shanghai"


@dataclass
class ObjectItem:
    key: str
    size: int
    etag: str = ""
    last_modified: str = ""


@dataclass
class MigrationStats:
    listed: int = 0
    listed_bytes: int = 0
    copied: int = 0
    copied_bytes: int = 0
    skipped: int = 0
    skipped_bytes: int = 0
    verified: int = 0
    failed: int = 0
    pages: int = 0
    first_keys: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


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


def parse_env_lines(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip().strip("'").strip('"')
    return values


def read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return parse_env_lines(path.read_text(encoding="utf-8").splitlines())


def read_production_container_env(args: argparse.Namespace) -> dict[str, str]:
    ssh = resolve_executable("ssh")
    command = [
        ssh,
        "-i",
        str(Path(args.identity_file)),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{args.user}@{args.host}",
        (
            "sudo -n docker inspect "
            f"{args.container} "
            "--format '{{range .Config.Env}}{{println .}}{{end}}'"
        ),
    ]
    result = subprocess.run(
        command,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.stderr.strip():
        log("remote docker inspect emitted stderr; values are not printed")
    return parse_env_lines(result.stdout.splitlines())


def pick(values: dict[str, str], names: list[str]) -> tuple[str | None, str | None]:
    for name in names:
        value = values.get(name)
        if value:
            return name, value
    return None, None


def load_credentials(args: argparse.Namespace) -> tuple[str, str, str]:
    merged: dict[str, str] = {}
    merged.update(read_env_file(Path(args.secret_file)))
    for key in (
        "TENCENT_CLOUD_SECRET_ID",
        "TENCENT_CLOUD_SECRET_KEY",
        "COS_SECRET_ID",
        "COS_SECRET_KEY",
    ):
        if os.environ.get(key):
            merged[key] = os.environ[key]

    source = "local secret file or local environment"
    _, secret_id = pick(merged, ["TENCENT_CLOUD_SECRET_ID", "COS_SECRET_ID"])
    _, secret_key = pick(merged, ["TENCENT_CLOUD_SECRET_KEY", "COS_SECRET_KEY"])

    if (not secret_id or not secret_key) and args.from_production_env:
        prod_env = read_production_container_env(args)
        merged.update({key: value for key, value in prod_env.items() if value})
        source = "production container environment"
        _, secret_id = pick(merged, ["TENCENT_CLOUD_SECRET_ID", "COS_SECRET_ID"])
        _, secret_key = pick(merged, ["TENCENT_CLOUD_SECRET_KEY", "COS_SECRET_KEY"])

    if not secret_id or not secret_key:
        raise RuntimeError(
            "COS credentials are missing. Fill .sce/config/local-secrets/cos-bucket.env, "
            "export TENCENT_CLOUD_SECRET_ID/TENCENT_CLOUD_SECRET_KEY, or pass --from-production-env."
        )
    return secret_id, secret_key, source


def cos_quote(value: str, *, safe: str = "-_.~") -> str:
    return urllib.parse.quote(value, safe=safe)


def canonical_query(params: dict[str, str]) -> tuple[str, str]:
    if not params:
        return "", ""
    parts: list[str] = []
    names: list[str] = []
    for key in sorted(params):
        names.append(key.lower())
        parts.append(f"{cos_quote(key.lower())}={cos_quote(str(params[key]))}")
    return "&".join(parts), ";".join(names)


def canonical_headers(headers: dict[str, str]) -> tuple[str, str]:
    normalized: dict[str, str] = {}
    for key, value in headers.items():
        lowered = key.strip().lower()
        normalized[lowered] = " ".join(str(value).strip().split())
    parts: list[str] = []
    names: list[str] = []
    for key in sorted(normalized):
        names.append(key)
        parts.append(f"{cos_quote(key)}={cos_quote(normalized[key])}")
    return "&".join(parts), ";".join(names)


def sha1_hex(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def hmac_sha1_hex(key: bytes, value: str) -> str:
    return hmac.new(key, value.encode("utf-8"), hashlib.sha1).hexdigest()


class CosXmlClient:
    def __init__(self, secret_id: str, secret_key: str, timeout: int = 60):
        self.secret_id = secret_id
        self.secret_key = secret_key.encode("utf-8")
        self.timeout = timeout

    def host(self, bucket: str, region: str) -> str:
        return f"{bucket}.cos.{region}.myqcloud.com"

    def authorization(
        self,
        method: str,
        path: str,
        params: dict[str, str],
        headers: dict[str, str],
    ) -> str:
        start = int(time.time())
        end = start + 900
        key_time = f"{start};{end}"
        sign_time = key_time
        canonical_uri = urllib.parse.quote(path, safe="/-_.~")
        canonical_qs, query_list = canonical_query(params)
        canonical_header_string, header_list = canonical_headers(headers)
        http_string = "\n".join(
            [
                method.lower(),
                canonical_uri,
                canonical_qs,
                canonical_header_string,
                "",
            ]
        )
        string_to_sign = "\n".join(["sha1", sign_time, sha1_hex(http_string), ""])
        sign_key = hmac.new(self.secret_key, key_time.encode("utf-8"), hashlib.sha1).hexdigest()
        signature = hmac_sha1_hex(sign_key.encode("utf-8"), string_to_sign)
        return (
            "q-sign-algorithm=sha1"
            f"&q-ak={self.secret_id}"
            f"&q-sign-time={sign_time}"
            f"&q-key-time={key_time}"
            f"&q-header-list={header_list}"
            f"&q-url-param-list={query_list}"
            f"&q-signature={signature}"
        )

    def request(
        self,
        method: str,
        bucket: str,
        region: str,
        path: str = "/",
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        body: bytes | None = None,
    ) -> tuple[int, str, dict[str, str], bytes]:
        params = params or {}
        headers = dict(headers or {})
        host = self.host(bucket, region)
        headers["Host"] = host
        headers["Authorization"] = self.authorization(method, path, params, headers)
        query, _ = canonical_query(params)
        target = path if not query else f"{path}?{query}"
        connection = http.client.HTTPSConnection(host, timeout=self.timeout)
        try:
            connection.request(method.upper(), target, body=body, headers=headers)
            response = connection.getresponse()
            data = response.read()
            response_headers = {key.lower(): value for key, value in response.getheaders()}
            return response.status, response.reason, response_headers, data
        finally:
            connection.close()

    def head_bucket(self, bucket: str, region: str) -> tuple[int, str]:
        status, reason, _, _ = self.request("HEAD", bucket, region)
        return status, reason

    def put_object(self, bucket: str, region: str, key: str, body: bytes, content_type: str) -> tuple[int, str, bytes]:
        path = "/" + urllib.parse.quote(key, safe="/-_.~")
        headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        }
        status, reason, _, data = self.request("PUT", bucket, region, path=path, headers=headers, body=body)
        return status, reason, data

    def delete_object(self, bucket: str, region: str, key: str) -> tuple[int, str]:
        path = "/" + urllib.parse.quote(key, safe="/-_.~")
        status, reason, _, _ = self.request("DELETE", bucket, region, path=path)
        return status, reason

    def head_object(self, bucket: str, region: str, key: str) -> tuple[int, dict[str, str]]:
        path = "/" + urllib.parse.quote(key, safe="/-_.~")
        status, _, headers, _ = self.request("HEAD", bucket, region, path=path)
        return status, headers

    def list_objects(
        self,
        bucket: str,
        region: str,
        page_size: int,
        continuation_token: str | None,
        prefix: str | None,
    ) -> tuple[list[ObjectItem], bool, str | None]:
        params = {
            "list-type": "2",
            "max-keys": str(page_size),
        }
        if continuation_token:
            params["continuation-token"] = continuation_token
        if prefix:
            params["prefix"] = prefix
        status, reason, _, data = self.request("GET", bucket, region, params=params)
        if status != 200:
            raise RuntimeError(f"list source bucket failed: HTTP {status} {reason}: {cos_error_code(data)}")
        root = ET.fromstring(data)
        contents = root.findall(".//{*}Contents")
        objects: list[ObjectItem] = []
        for node in contents:
            key = text_of(node, "Key")
            size = int(text_of(node, "Size") or "0")
            objects.append(
                ObjectItem(
                    key=key,
                    size=size,
                    etag=(text_of(node, "ETag") or "").strip('"'),
                    last_modified=text_of(node, "LastModified"),
                )
            )
        is_truncated = (text_of(root, "IsTruncated") or "").lower() == "true"
        next_token = text_of(root, "NextContinuationToken")
        return objects, is_truncated, next_token

    def copy_object(
        self,
        source_bucket: str,
        source_region: str,
        target_bucket: str,
        target_region: str,
        key: str,
    ) -> tuple[int, str, bytes]:
        path = "/" + urllib.parse.quote(key, safe="/-_.~")
        encoded_key = urllib.parse.quote(key, safe="/-_.~")
        copy_source = f"{source_bucket}.cos.{source_region}.myqcloud.com/{encoded_key}"
        headers = {
            "x-cos-copy-source": copy_source,
            "Content-Length": "0",
        }
        status, reason, _, data = self.request(
            "PUT",
            target_bucket,
            target_region,
            path=path,
            headers=headers,
            body=b"",
        )
        return status, reason, data


def text_of(node: ET.Element, child_name: str) -> str:
    child = node.find(f"{{*}}{child_name}")
    return child.text or "" if child is not None else ""


def cos_error_code(data: bytes) -> str:
    if not data:
        return "empty-response"
    try:
        root = ET.fromstring(data)
        code = text_of(root, "Code")
        message = text_of(root, "Message")
        return f"{code} {message}".strip()
    except ET.ParseError:
        return data[:300].decode("utf-8", errors="replace")


def object_size_from_headers(headers: dict[str, str]) -> int | None:
    raw = headers.get("content-length")
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def validate_bucket(client: CosXmlClient, bucket: str, region: str, label: str) -> None:
    status, reason = client.head_bucket(bucket, region)
    if status != 200:
        raise RuntimeError(f"{label} bucket is not accessible: {bucket}/{region} -> HTTP {status} {reason}")
    log(f"{label} bucket accessible: {bucket} ({region})")


def validate_target_write(client: CosXmlClient, bucket: str, region: str) -> None:
    key = f"codex-migration-smoke/{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    body = b"kaipai cos migration smoke\n"
    status, reason, data = client.put_object(bucket, region, key, body, "text/plain")
    if status not in (200, 206):
        raise RuntimeError(f"target bucket write smoke failed: HTTP {status} {reason}: {cos_error_code(data)}")
    head_status, headers = client.head_object(bucket, region, key)
    if head_status != 200 or object_size_from_headers(headers) != len(body):
        raise RuntimeError(f"target bucket write smoke verification failed: HTTP {head_status}")
    delete_status, delete_reason = client.delete_object(bucket, region, key)
    if delete_status not in (200, 204):
        raise RuntimeError(f"target bucket smoke cleanup failed: HTTP {delete_status} {delete_reason}")
    log("target bucket write/delete smoke passed")


def record_error(stats: MigrationStats, message: str) -> None:
    stats.failed += 1
    if len(stats.errors) < 20:
        stats.errors.append(message)


def should_stop_for_limit(limit: int | None, stats: MigrationStats) -> bool:
    if limit is None or limit <= 0:
        return False
    return stats.listed >= limit


def migrate(args: argparse.Namespace, client: CosXmlClient) -> MigrationStats:
    stats = MigrationStats()
    token: str | None = None
    execute = args.execute
    while True:
        objects, truncated, next_token = client.list_objects(
            args.source_bucket,
            args.source_region,
            args.page_size,
            token,
            args.prefix,
        )
        stats.pages += 1
        for item in objects:
            if should_stop_for_limit(args.limit, stats):
                break
            stats.listed += 1
            stats.listed_bytes += item.size
            if len(stats.first_keys) < 10:
                stats.first_keys.append(item.key)
            if not execute:
                continue
            try:
                if args.skip_existing:
                    head_status, headers = client.head_object(args.target_bucket, args.target_region, item.key)
                    target_size = object_size_from_headers(headers) if head_status == 200 else None
                    if head_status == 200 and target_size == item.size:
                        stats.skipped += 1
                        stats.skipped_bytes += item.size
                        stats.verified += 1
                        continue
                status, reason, data = client.copy_object(
                    args.source_bucket,
                    args.source_region,
                    args.target_bucket,
                    args.target_region,
                    item.key,
                )
                if status != 200:
                    record_error(stats, f"{item.key}: copy failed HTTP {status} {reason}: {cos_error_code(data)}")
                    continue
                head_status, headers = client.head_object(args.target_bucket, args.target_region, item.key)
                target_size = object_size_from_headers(headers) if head_status == 200 else None
                if head_status != 200 or target_size != item.size:
                    record_error(stats, f"{item.key}: verify failed HTTP {head_status}, size={target_size}, expected={item.size}")
                    continue
                stats.copied += 1
                stats.copied_bytes += item.size
                stats.verified += 1
            except Exception as exc:
                record_error(stats, f"{item.key}: {exc}")
            if stats.listed % args.progress_every == 0:
                log(
                    "progress: "
                    f"listed={stats.listed}, copied={stats.copied}, "
                    f"skipped={stats.skipped}, failed={stats.failed}"
                )
        if should_stop_for_limit(args.limit, stats):
            break
        if not truncated:
            break
        token = next_token
    return stats


def format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    number = float(value)
    for unit in units:
        if number < 1024 or unit == units[-1]:
            return f"{number:.2f}{unit}"
        number /= 1024
    return f"{value}B"


def write_record(args: argparse.Namespace, stats: MigrationStats, credential_source: str, started_at: str, finished_at: str) -> Path:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    mode = "execute" if args.execute else "dry-run"
    record_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-cos-bucket-object-migration-{mode}"
    path = RECORDS_DIR / f"{record_id}.md"
    lines = [
        f"# COS bucket object migration {mode}",
        "",
        f"- startedAt: `{started_at}`",
        f"- finishedAt: `{finished_at}`",
        f"- sourceBucket: `{args.source_bucket}`",
        f"- targetBucket: `{args.target_bucket}`",
        f"- sourceRegion: `{args.source_region}`",
        f"- targetRegion: `{args.target_region}`",
        f"- prefix: `{args.prefix or ''}`",
        f"- limit: `{args.limit or ''}`",
        f"- credentialSource: `{credential_source}`",
        f"- secretsPrinted: `false`",
        "",
        "## Summary",
        "",
        f"- pages: `{stats.pages}`",
        f"- listed: `{stats.listed}`",
        f"- listedBytes: `{stats.listed_bytes}` ({format_bytes(stats.listed_bytes)})",
        f"- copied: `{stats.copied}`",
        f"- copiedBytes: `{stats.copied_bytes}` ({format_bytes(stats.copied_bytes)})",
        f"- skipped: `{stats.skipped}`",
        f"- skippedBytes: `{stats.skipped_bytes}` ({format_bytes(stats.skipped_bytes)})",
        f"- verified: `{stats.verified}`",
        f"- failed: `{stats.failed}`",
        "",
        "## First Keys",
        "",
    ]
    if stats.first_keys:
        lines.extend(f"- `{key}`" for key in stats.first_keys)
    else:
        lines.append("- none")
    lines.extend(["", "## Errors", ""])
    if stats.errors:
        lines.extend(f"- `{error}`" for error in stats.errors)
    else:
        lines.append("- none")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy Tencent COS objects from an old bucket to a new bucket without deleting source objects.",
    )
    parser.add_argument("--source-bucket", default=DEFAULT_SOURCE_BUCKET)
    parser.add_argument("--target-bucket", default=DEFAULT_TARGET_BUCKET)
    parser.add_argument("--region", default=DEFAULT_REGION, help="Region used for both source and target unless overridden.")
    parser.add_argument("--source-region")
    parser.add_argument("--target-region")
    parser.add_argument("--prefix")
    parser.add_argument("--limit", type=positive_int)
    parser.add_argument("--page-size", type=positive_int, default=1000)
    parser.add_argument("--progress-every", type=positive_int, default=100)
    parser.add_argument("--execute", action="store_true", help="Actually copy objects. Omit for dry-run.")
    parser.add_argument("--overwrite", action="store_true", help="Copy even when target object exists with the same size.")
    parser.add_argument("--no-target-smoke", action="store_true", help="Skip target write/delete smoke before execute mode.")
    parser.add_argument("--secret-file", default=str(DEFAULT_SECRET_FILE))
    parser.add_argument("--from-production-env", action="store_true", help="Read COS credentials from the production backend container if local inputs are missing.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.source_region = args.source_region or args.region
    args.target_region = args.target_region or args.region
    args.skip_existing = not args.overwrite
    started_at = datetime.now().astimezone().isoformat()
    mode = "execute" if args.execute else "dry-run"

    log(f"starting COS bucket object migration ({mode})")
    log(f"source={args.source_bucket}/{args.source_region}, target={args.target_bucket}/{args.target_region}")
    if not args.execute:
        log("dry-run mode: no target objects will be written")

    secret_id, secret_key, credential_source = load_credentials(args)
    log(f"credentials loaded from {credential_source}; secret values are hidden")
    client = CosXmlClient(secret_id, secret_key)

    validate_bucket(client, args.source_bucket, args.source_region, "source")
    validate_bucket(client, args.target_bucket, args.target_region, "target")
    if args.execute and not args.no_target_smoke:
        validate_target_write(client, args.target_bucket, args.target_region)

    stats = migrate(args, client)
    finished_at = datetime.now().astimezone().isoformat()
    record_path = write_record(args, stats, credential_source, started_at, finished_at)
    log(
        "migration summary: "
        f"listed={stats.listed} ({format_bytes(stats.listed_bytes)}), "
        f"copied={stats.copied}, skipped={stats.skipped}, "
        f"verified={stats.verified}, failed={stats.failed}"
    )
    log(f"record saved: {record_path}")
    if stats.failed:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"command failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
