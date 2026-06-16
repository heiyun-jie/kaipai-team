import argparse
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_EXPECTED_IP = "101.43.57.62"
DEFAULT_DOMAIN = "kplyyk.com"
DEFAULT_TEST_API_HOST = "test-api.kplyyk.com"
DEFAULT_TEST_ADMIN_HOST = "test.kplyyk.com"
DEFAULT_NACOS_SERVER_ADDR = "127.0.0.1:8848"
DEFAULT_NACOS_GROUP = "DEFAULT_GROUP"
DEFAULT_NACOS_NAMESPACE = ""
DEFAULT_TEST_DATA_ID = "kaipai-backend-test.yml"
DEFAULT_PROD_DATA_ID = "kaipai-backend-prod.yml"
DEFAULT_TEST_DATABASE = "kaipai_test"
DEFAULT_PROD_DATABASE = "kaipai_prod"
DEFAULT_MYSQL_CONTAINER = "kaipai-mysql"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
CORE_TABLES = [
    "user",
    "actor_profile",
    "admin_user",
    "admin_role",
    "card_scene_template",
    "identity_verification",
]


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


def run_process(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_sectioned_output(output: str, fields: list[str]) -> dict[str, str]:
    sections: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        match = re.search(rf"{re.escape(begin)}\s*(.*?)\s*{re.escape(end)}", output, re.S)
        if not match:
            raise RuntimeError(f"missing helper output section: {field}")
        sections[field] = match.group(1).strip()
    return sections


def summarize_nacos_config(raw_config: str, expected_database: str) -> dict[str, Any]:
    lower = raw_config.lower()
    required_fragments = ["spring", "datasource", "redis"]
    missing_fragments = [fragment for fragment in required_fragments if fragment not in lower]
    return {
        "readable": bool(raw_config.strip()),
        "containsExpectedDatabase": expected_database in raw_config,
        "missingFragments": missing_fragments,
    }


def preflight_exit_code(gates: dict[str, dict[str, Any]]) -> int:
    return 0 if all(bool(gate.get("passed")) for gate in gates.values()) else 1


def parse_table_count_result(mysql_result: str, expected_count: int) -> dict[str, Any]:
    match = re.search(r"TABLE_COUNT=(\d+)", mysql_result)
    found_count = int(match.group(1)) if match else 0
    return {
        "schemaReady": found_count == expected_count,
        "foundTableCount": found_count,
        "expectedTableCount": expected_count,
    }


def check_dns(hostnames: list[str], expected_ip: str) -> dict[str, Any]:
    records = []
    for hostname in hostnames:
        try:
            results = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
            addresses = sorted({item[4][0] for item in results})
            passed = expected_ip in addresses
            records.append(
                {
                    "hostname": hostname,
                    "resolved": bool(addresses),
                    "addresses": addresses,
                    "expectedIp": expected_ip,
                    "passed": passed,
                }
            )
        except socket.gaierror as exc:
            records.append(
                {
                    "hostname": hostname,
                    "resolved": False,
                    "addresses": [],
                    "expectedIp": expected_ip,
                    "passed": False,
                    "reason": str(exc),
                }
            )
    return {
        "passed": all(item["passed"] for item in records),
        "records": records,
    }


def ssh_base(user: str, host: str, identity_file: Path) -> list[str]:
    return [
        resolve_executable("ssh"),
        "-i",
        str(identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{user}@{host}",
    ]


def scp_base(identity_file: Path) -> list[str]:
    return [
        resolve_executable("scp"),
        "-i",
        str(identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(user: str, host: str, identity_file: Path, remote_command: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(user, host, identity_file) + [remote_command], check=check)


def check_remote_access(user: str, host: str, identity_file: Path) -> dict[str, Any]:
    if not identity_file.exists():
        return {
            "passed": False,
            "keyAuth": False,
            "helper": False,
            "reason": f"identity file not found: {identity_file}",
        }
    key = run_ssh(user, host, identity_file, "printf 'key-auth-ok'", check=False)
    key_ok = key.returncode == 0 and key.stdout.strip() == "key-auth-ok"
    helper_ok = False
    reason = ""
    if key_ok:
        helper = run_ssh(user, host, identity_file, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck", check=False)
        helper_ok = helper.returncode == 0 and helper.stdout.strip() == "helper-ok"
        if not helper_ok:
            reason = "release helper healthcheck failed"
    else:
        reason = "ssh key auth failed"
    return {
        "passed": key_ok and helper_ok,
        "keyAuth": key_ok,
        "helper": helper_ok,
        "reason": reason,
    }


def export_nacos_config(
    user: str,
    host: str,
    identity_file: Path,
    *,
    server_addr: str,
    group: str,
    namespace: str,
    data_id: str,
) -> str:
    command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--nacos-config-export "
        f"--nacos-server-addr {shlex.quote(server_addr)} "
        f"--nacos-group {shlex.quote(group)} "
        f"--nacos-namespace {shlex.quote(namespace)} "
        f"--nacos-data-id {shlex.quote(data_id)}"
    )
    result = run_ssh(user, host, identity_file, command)
    sections = parse_sectioned_output(
        result.stdout,
        ["NACOS_RAW_CONFIG", "FINAL_STATUS", "FAIL_REASON"],
    )
    if sections["FINAL_STATUS"] != "passed":
        raise RuntimeError(sections["FAIL_REASON"] or "nacos export failed")
    return sections["NACOS_RAW_CONFIG"]


def check_nacos(
    user: str,
    host: str,
    identity_file: Path,
    *,
    server_addr: str,
    group: str,
    namespace: str,
    targets: dict[str, dict[str, str]],
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name, target in targets.items():
        try:
            raw = export_nacos_config(
                user,
                host,
                identity_file,
                server_addr=server_addr,
                group=group,
                namespace=namespace,
                data_id=target["dataId"],
            )
            summary = summarize_nacos_config(raw, target["database"])
            passed = (
                summary["readable"]
                and summary["containsExpectedDatabase"]
                and not summary["missingFragments"]
            )
            results[name] = {
                "dataId": target["dataId"],
                "expectedDatabase": target["database"],
                "passed": passed,
                **summary,
            }
        except Exception as exc:
            results[name] = {
                "dataId": target["dataId"],
                "expectedDatabase": target["database"],
                "passed": False,
                "readable": False,
                "containsExpectedDatabase": False,
                "missingFragments": ["spring", "datasource", "redis"],
                "reason": str(exc),
            }
    return {
        "passed": all(item["passed"] for item in results.values()),
        "targets": results,
    }


def upload_temp_sql(
    user: str,
    host: str,
    identity_file: Path,
    *,
    release_id: str,
    sql: str,
) -> str:
    remote_dir = f"/home/{user}/backend-schema-uploads/{release_id}"
    run_ssh(user, host, identity_file, f"mkdir -p {shlex.quote(remote_dir)}")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
        handle.write(sql)
        local_sql_path = Path(handle.name)
    try:
        remote_path = f"{remote_dir}/dual-env-db-existence.sql"
        run_process(
            scp_base(identity_file)
            + [str(local_sql_path), f"{user}@{host}:{remote_path}"]
        )
        return remote_path
    finally:
        local_sql_path.unlink(missing_ok=True)


def check_database(
    user: str,
    host: str,
    identity_file: Path,
    *,
    mysql_container: str,
    databases: list[str],
) -> dict[str, Any]:
    release_id = f"dual-env-preflight-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    table_literals = ", ".join(f"'{table}'" for table in CORE_TABLES)
    sql = (
        "SELECT CONCAT('DATABASE_OK=', DATABASE()) AS result;\n"
        "SELECT CONCAT('TABLE_COUNT=', COUNT(*)) AS result\n"
        "FROM information_schema.tables\n"
        "WHERE table_schema = DATABASE()\n"
        f"  AND table_name IN ({table_literals});\n"
    )
    remote_path = upload_temp_sql(user, host, identity_file, release_id=release_id, sql=sql)
    results: dict[str, Any] = {}
    try:
        for database in databases:
            command = (
                f"sudo -n {REMOTE_HELPER_PATH} "
                f"--mysql-validation "
                f"--mysql-script-path {shlex.quote(remote_path)} "
                f"--mysql-database {shlex.quote(database)} "
                f"--mysql-container {shlex.quote(mysql_container)}"
            )
            result = run_ssh(user, host, identity_file, command, check=False)
            if result.returncode == 0:
                try:
                    sections = parse_sectioned_output(
                        result.stdout,
                        ["MYSQL_RESULT", "FINAL_STATUS", "FAIL_REASON"],
                    )
                    exists = sections["FINAL_STATUS"] == "passed" and f"DATABASE_OK={database}" in sections["MYSQL_RESULT"]
                    schema_summary = parse_table_count_result(sections["MYSQL_RESULT"], len(CORE_TABLES))
                    passed = exists and schema_summary["schemaReady"]
                    reason = "" if passed else sections["FAIL_REASON"]
                except Exception as exc:
                    passed = False
                    exists = False
                    schema_summary = parse_table_count_result("", len(CORE_TABLES))
                    reason = str(exc)
            else:
                passed = False
                exists = False
                schema_summary = parse_table_count_result("", len(CORE_TABLES))
                reason = "mysql validation failed"
            results[database] = {
                "passed": passed,
                "exists": exists,
                **schema_summary,
                "requiredTables": CORE_TABLES,
                "reason": reason,
            }
    finally:
        remote_dir = f"/home/{user}/backend-schema-uploads/{release_id}"
        run_ssh(user, host, identity_file, f"rm -rf {shlex.quote(remote_dir)}", check=False)
    return {
        "passed": all(item["passed"] for item in results.values()),
        "databases": results,
    }


def build_targets(args: argparse.Namespace) -> dict[str, dict[str, str]]:
    return {
        "test": {
            "dataId": args.test_data_id,
            "database": args.test_database,
        },
        "prod": {
            "dataId": args.prod_data_id,
            "database": args.prod_database,
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sanitized same-host dual-environment preflight gates.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--expected-ip", default=DEFAULT_EXPECTED_IP)
    parser.add_argument("--test-api-host", default=DEFAULT_TEST_API_HOST)
    parser.add_argument("--test-admin-host", default=DEFAULT_TEST_ADMIN_HOST)
    parser.add_argument("--nacos-server-addr", default=DEFAULT_NACOS_SERVER_ADDR)
    parser.add_argument("--nacos-group", default=DEFAULT_NACOS_GROUP)
    parser.add_argument("--nacos-namespace", default=DEFAULT_NACOS_NAMESPACE)
    parser.add_argument("--test-data-id", default=DEFAULT_TEST_DATA_ID)
    parser.add_argument("--prod-data-id", default=DEFAULT_PROD_DATA_ID)
    parser.add_argument("--test-database", default=DEFAULT_TEST_DATABASE)
    parser.add_argument("--prod-database", default=DEFAULT_PROD_DATABASE)
    parser.add_argument("--mysql-container", default=DEFAULT_MYSQL_CONTAINER)
    parser.add_argument("--skip-remote", action="store_true", help="Only run local DNS gates.")
    parser.add_argument("--allow-fail", action="store_true", help="Always exit 0 after printing sanitized result.")
    return parser.parse_args(argv)


def run_preflight(args: argparse.Namespace) -> dict[str, Any]:
    gates: dict[str, dict[str, Any]] = {
        "dns": check_dns([args.test_api_host, args.test_admin_host], args.expected_ip),
    }
    if not args.skip_remote:
        identity_file = Path(args.identity_file)
        remote = check_remote_access(args.user, args.host, identity_file)
        gates["remoteAccess"] = remote
        if remote["passed"]:
            gates["nacos"] = check_nacos(
                args.user,
                args.host,
                identity_file,
                server_addr=args.nacos_server_addr,
                group=args.nacos_group,
                namespace=args.nacos_namespace,
                targets=build_targets(args),
            )
            gates["database"] = check_database(
                args.user,
                args.host,
                identity_file,
                mysql_container=args.mysql_container,
                databases=[args.test_database, args.prod_database],
            )
        else:
            gates["nacos"] = {"passed": False, "reason": "remote access gate failed"}
            gates["database"] = {"passed": False, "reason": "remote access gate failed"}
    return {
        "checkedAt": datetime.now().astimezone().isoformat(),
        "passed": preflight_exit_code(gates) == 0,
        "gates": gates,
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    result = run_preflight(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    exit_code = 0 if args.allow_fail else preflight_exit_code(result["gates"])
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
