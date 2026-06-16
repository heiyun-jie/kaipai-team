import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


ENDPOINT = "https://alidns.aliyuncs.com/"
VERSION = "2015-01-09"
DEFAULT_LINE = "default"


@dataclass(frozen=True)
class DesiredRecord:
    rr: str
    value: str
    record_type: str
    line: str
    ttl: int


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def percent_encode(value: Any) -> str:
    return quote(str(value), safe="~")


def require_secret(name: str, *fallback_names: str) -> str:
    for candidate in (name, *fallback_names):
        value = os.environ.get(candidate)
        if value:
            return value
    names = ", ".join((name, *fallback_names))
    raise RuntimeError(f"missing required environment variable: {names}")


def sign_params(access_key_secret: str, params: dict[str, Any]) -> str:
    canonicalized_query = "&".join(
        f"{percent_encode(key)}={percent_encode(params[key])}"
        for key in sorted(params.keys())
    )
    string_to_sign = "GET&%2F&" + percent_encode(canonicalized_query)
    digest = hmac.new(
        (access_key_secret + "&").encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def common_params(access_key_id: str, action: str) -> dict[str, Any]:
    return {
        "Action": action,
        "Version": VERSION,
        "Format": "JSON",
        "AccessKeyId": access_key_id,
        "SignatureMethod": "HMAC-SHA1",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
    }


def call_alidns(access_key_id: str, access_key_secret: str, action: str, params: dict[str, Any]) -> dict[str, Any]:
    request_params = common_params(access_key_id, action)
    request_params.update(params)
    signature = sign_params(access_key_secret, request_params)
    query = "&".join(
        f"{percent_encode(key)}={percent_encode(request_params[key])}"
        for key in sorted(request_params.keys())
    )
    url = ENDPOINT + "?" + query + "&Signature=" + percent_encode(signature)
    try:
        with urlopen(url, timeout=30) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Alidns HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Alidns request failed: {exc}") from exc

    data = json.loads(body)
    if "Code" in data and data.get("Code") not in ("", None):
        raise RuntimeError(f"Alidns API error {data.get('Code')}: {data.get('Message', '')}")
    return data


def describe_subdomain_records(
    access_key_id: str,
    access_key_secret: str,
    fqdn: str,
    record_type: str,
) -> list[dict[str, Any]]:
    data = call_alidns(
        access_key_id,
        access_key_secret,
        "DescribeSubDomainRecords",
        {
            "SubDomain": fqdn,
            "Type": record_type,
        },
    )
    records = data.get("DomainRecords", {}).get("Record", [])
    if isinstance(records, dict):
        return [records]
    return list(records or [])


def add_domain_record(
    access_key_id: str,
    access_key_secret: str,
    domain: str,
    record: DesiredRecord,
) -> dict[str, Any]:
    return call_alidns(
        access_key_id,
        access_key_secret,
        "AddDomainRecord",
        {
            "DomainName": domain,
            "RR": record.rr,
            "Type": record.record_type,
            "Value": record.value,
            "TTL": record.ttl,
            "Line": record.line,
        },
    )


def parse_record(value: str, record_type: str, line: str, ttl: int) -> DesiredRecord:
    if "=" not in value:
        raise argparse.ArgumentTypeError("record must be in rr=value format")
    rr, record_value = value.split("=", 1)
    rr = rr.strip()
    record_value = record_value.strip()
    if not rr or not record_value:
        raise argparse.ArgumentTypeError("record rr and value cannot be empty")
    return DesiredRecord(
        rr=rr,
        value=record_value,
        record_type=record_type.upper(),
        line=line,
        ttl=ttl,
    )


def sync_record(
    access_key_id: str,
    access_key_secret: str,
    domain: str,
    record: DesiredRecord,
    *,
    dry_run: bool,
) -> dict[str, Any]:
    fqdn = f"{record.rr}.{domain}" if record.rr != "@" else domain
    existing = describe_subdomain_records(access_key_id, access_key_secret, fqdn, record.record_type)
    exact = [item for item in existing if str(item.get("Value", "")) == record.value]
    if exact:
        record_id = exact[0].get("RecordId")
        log(f"noop {fqdn} {record.record_type} {record.value} recordId={record_id}")
        return {
            "fqdn": fqdn,
            "value": record.value,
            "recordType": record.record_type,
            "status": "noop",
            "recordId": record_id,
        }

    if existing:
        values = ", ".join(str(item.get("Value", "")) for item in existing)
        raise RuntimeError(
            f"refuse to modify existing {fqdn} {record.record_type} record(s) "
            f"with different value(s): {values}"
        )

    if dry_run:
        log(f"dry-run create {fqdn} {record.record_type} {record.value} ttl={record.ttl}")
        return {
            "fqdn": fqdn,
            "value": record.value,
            "recordType": record.record_type,
            "status": "dry-run-create",
        }

    response = add_domain_record(access_key_id, access_key_secret, domain, record)
    record_id = response.get("RecordId")
    log(f"created {fqdn} {record.record_type} {record.value} recordId={record_id}")
    return {
        "fqdn": fqdn,
        "value": record.value,
        "recordType": record.record_type,
        "status": "created",
        "recordId": record_id,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync Alibaba Cloud Alidns records without storing secrets.")
    parser.add_argument("--domain", default="kplyyk.com", help="Domain name, default: kplyyk.com")
    parser.add_argument("--record", action="append", required=True, help="Desired record, rr=value")
    parser.add_argument("--record-type", default="A", help="Record type, default: A")
    parser.add_argument("--record-line", default=DEFAULT_LINE, help="Record line, default: default")
    parser.add_argument("--ttl", type=int, default=600, help="Record TTL, default: 600")
    parser.add_argument("--dry-run", action="store_true", help="Only describe and report planned creates")
    parser.add_argument("--json", action="store_true", help="Print sanitized JSON result")
    args = parser.parse_args(argv)

    access_key_id = require_secret("ALIBABA_CLOUD_ACCESS_KEY_ID", "ALIYUN_ACCESS_KEY_ID", "ALICLOUD_ACCESS_KEY")
    access_key_secret = require_secret(
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
        "ALIYUN_ACCESS_KEY_SECRET",
        "ALICLOUD_SECRET_KEY",
    )
    desired = [parse_record(item, args.record_type, args.record_line, args.ttl) for item in args.record]
    results = [
        sync_record(access_key_id, access_key_secret, args.domain, record, dry_run=args.dry_run)
        for record in desired
    ]
    if args.json:
        print(json.dumps({"domain": args.domain, "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
