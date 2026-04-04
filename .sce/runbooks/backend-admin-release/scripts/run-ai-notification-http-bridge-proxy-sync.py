import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
DEFAULT_PROXY_LOCATION = "/bridge/ai-notification/"
DEFAULT_PROXY_PASS_URL = "http://172.17.0.1:19081/"


@dataclass
class BridgeProxyContext:
    release_id: str
    host: str
    user: str
    operator: str
    identity_file: Path
    proxy_location: str
    proxy_pass_url: str


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


def ssh_base(context: BridgeProxyContext) -> list[str]:
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


def run_ssh(context: BridgeProxyContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: BridgeProxyContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: BridgeProxyContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def parse_helper_sections(output: str, fields: list[str]) -> dict[str, str]:
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        match = re.search(rf"{re.escape(begin)}\n(.*?)\n{re.escape(end)}", output, re.S)
        if not match:
            raise RuntimeError(f"missing helper output section: {field}")
        summary[field] = match.group(1).strip()
    return summary


def sync_proxy(context: BridgeProxyContext) -> dict[str, str]:
    command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--release-id {context.release_id} "
        f"--bridge-proxy-sync "
        f"--bridge-proxy-location {context.proxy_location} "
        f"--bridge-proxy-pass-url {context.proxy_pass_url}"
    )
    result = run_ssh(context, command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_sections(
        result.stdout,
        [
            "REMOTE_DATE",
            "BACKUP_PATH",
            "NGINX_CONF_FILE",
            "BRIDGE_PROXY_LOCATION",
            "BRIDGE_PROXY_PASS_URL",
            "CANDIDATE_PREVIEW",
            "NGINX_TEST_OUTPUT",
            "NGINX_RELOAD_OUTPUT",
            "PROBE_OUTPUT",
            "FINAL_STATUS",
            "FAIL_REASON",
        ],
    )
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"bridge proxy sync failed: {summary['FAIL_REASON']}")
    return summary


def write_record(context: BridgeProxyContext, summary: dict[str, str]) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    lines = [
        "# AI 通知 HTTP Bridge 代理路由同步记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 操作人：`{context.operator}`",
        f"- 目标主机：`{context.host}`",
        f"- 路由：`{context.proxy_location}`",
        f"- 反代目标：`{context.proxy_pass_url}`",
        "",
        "## 2. 远端结果",
        "",
        f"- 备份目录：`{summary.get('BACKUP_PATH')}`",
        f"- nginx 配置：`{summary.get('NGINX_CONF_FILE')}`",
        "",
        "## 3. Nginx 检查",
        "",
        f"- `nginx -t`：`{summary.get('NGINX_TEST_OUTPUT')}`",
        f"- `nginx reload`：`{summary.get('NGINX_RELOAD_OUTPUT') or '--'}`",
        "",
        "## 4. 代理探活",
        "",
        "```text",
        summary.get("PROBE_OUTPUT") or "--",
        "```",
    ]
    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync nginx proxy route for the AI notification HTTP bridge mock.")
    parser.add_argument("--label", required=True)
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--proxy-location", default=DEFAULT_PROXY_LOCATION)
    parser.add_argument("--proxy-pass-url", default=DEFAULT_PROXY_PASS_URL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = BridgeProxyContext(
        release_id=f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-ai-notification-http-bridge-proxy-{args.label}",
        host=args.host,
        user=args.user,
        operator=args.operator,
        identity_file=Path(args.identity_file),
        proxy_location=args.proxy_location,
        proxy_pass_url=args.proxy_pass_url,
    )
    if not context.identity_file.exists():
        raise RuntimeError(f"identity file not found: {context.identity_file}")

    require_key_auth(context)
    require_helper(context)
    summary = sync_proxy(context)
    record_path = write_record(context, summary)
    print(
        json.dumps(
            {
                "release_id": context.release_id,
                "status": "completed",
                "proxy_location": context.proxy_location,
                "proxy_pass_url": context.proxy_pass_url,
                "record_path": str(record_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
