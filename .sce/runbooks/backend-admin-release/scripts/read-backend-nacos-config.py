import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
DIAGNOSTICS_DIR = RUNBOOK_DIR / "records" / "diagnostics"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_NACOS_SERVER_ADDR = "127.0.0.1:8848"
DEFAULT_NACOS_DATA_IDS = ["kaipai-backend", "kaipai-backend.yml", "kaipai-backend-dev.yml"]
DEFAULT_NACOS_GROUP = "DEFAULT_GROUP"
DEFAULT_NACOS_NAMESPACE = ""
DEFAULT_GREP = "WECHAT_MINIAPP|wechat\\.miniapp"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"


@dataclass
class NacosDiagnosticContext:
    capture_id: str
    host: str
    user: str
    identity_file: Path
    nacos_server_addr: str
    data_ids: list[str]
    group: str
    namespace: str
    grep: str
    output_dir: Path


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


def ssh_base(context: NacosDiagnosticContext) -> list[str]:
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


def run_ssh(context: NacosDiagnosticContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: NacosDiagnosticContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: NacosDiagnosticContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "backend-nacos-config-scan"


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "NACOS_SERVER_ADDR",
        "NACOS_DATA_IDS",
        "NACOS_LOGIN_OUTPUT",
        "NACOS_CONFIG_PRESENCE_SUMMARY",
        "NACOS_FILTERED_CONFIGS",
        "FINAL_STATUS",
        "FAIL_REASON",
    ]
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        match = re.search(rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}", output, re.S)
        if not match:
            raise RuntimeError(f"missing helper output section: {field}")
        summary[field] = match.group(1).strip()
    return summary


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def collect(context: NacosDiagnosticContext) -> None:
    ensure_dir(context.output_dir)
    data_ids_value = ",".join(context.data_ids)
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--nacos-config-scan "
        f"--nacos-server-addr {shlex.quote(context.nacos_server_addr)} "
        f"--nacos-data-ids {shlex.quote(data_ids_value)} "
        f"--nacos-group {shlex.quote(context.group)} "
        f"--nacos-namespace {shlex.quote(context.namespace)} "
        f"--nacos-grep {shlex.quote(context.grep)}"
    )
    result = run_ssh(context, helper_command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")

    summary = parse_helper_output(result.stdout)
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"nacos config scan failed: {summary['FAIL_REASON']}")

    metadata = {
        "captureId": context.capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "remoteDate": summary["REMOTE_DATE"],
        "host": context.host,
        "user": context.user,
        "nacosServerAddr": summary["NACOS_SERVER_ADDR"],
        "dataIds": context.data_ids,
        "group": context.group,
        "namespace": context.namespace,
        "grep": context.grep,
        "files": {
            "presenceSummary": "nacos-config-presence-summary.txt",
            "filteredConfigs": "nacos-filtered-configs.txt",
            "loginOutput": "nacos-login-output.txt",
        },
    }
    write_text(context.output_dir / "nacos-config-presence-summary.txt", summary["NACOS_CONFIG_PRESENCE_SUMMARY"])
    write_text(context.output_dir / "nacos-filtered-configs.txt", summary["NACOS_FILTERED_CONFIGS"])
    write_text(context.output_dir / "nacos-login-output.txt", summary["NACOS_LOGIN_OUTPUT"])
    write_text(context.output_dir / "summary.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    log(f"nacos diagnostic capture saved: {context.output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read backend Nacos config sources through the standard helper.")
    parser.add_argument("--label", default="backend-nacos-config-scan")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--nacos-server-addr", default=DEFAULT_NACOS_SERVER_ADDR)
    parser.add_argument("--nacos-data-id", action="append", dest="data_ids")
    parser.add_argument("--nacos-group", default=DEFAULT_NACOS_GROUP)
    parser.add_argument("--nacos-namespace", default=DEFAULT_NACOS_NAMESPACE)
    parser.add_argument("--grep", default=DEFAULT_GREP)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    output_dir = DIAGNOSTICS_DIR / capture_id
    context = NacosDiagnosticContext(
        capture_id=capture_id,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        nacos_server_addr=args.nacos_server_addr,
        data_ids=args.data_ids or list(DEFAULT_NACOS_DATA_IDS),
        group=args.nacos_group,
        namespace=args.nacos_namespace,
        grep=args.grep,
        output_dir=output_dir,
    )
    require_key_auth(context)
    require_helper(context)
    collect(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
