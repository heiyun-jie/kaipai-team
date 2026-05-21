import argparse
import json
import os
import re
import shlex
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
DEFAULT_DOMAIN = "kplyyk.com"
DEFAULT_API_DOMAIN = "api.kplyyk.com"
DEFAULT_BACKEND_URL = "http://127.0.0.1:8080"


@dataclass
class DomainProxyContext:
    release_id: str
    host: str
    user: str
    operator: str
    identity_file: Path
    domain: str
    api_domain: str
    backend_url: str
    api_only: bool


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
    log(f"local> {' '.join(command)}")
    return subprocess.run(
        command,
        check=check,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def ssh_base(context: DomainProxyContext) -> list[str]:
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


def run_ssh(context: DomainProxyContext, remote_command: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], check=check)


def require_key_auth(context: DomainProxyContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: DomainProxyContext) -> None:
    result = run_ssh(context, f"sudo -n {shlex.quote(REMOTE_HELPER_PATH)} --healthcheck")
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
            raise RuntimeError(f"missing helper output section: {field}\noutput:\n{output}")
        summary[field] = match.group(1).strip()
    return summary


def sync_proxy(context: DomainProxyContext) -> tuple[dict[str, str], int, str]:
    command = " ".join(
        [
            "sudo -n",
            shlex.quote(REMOTE_HELPER_PATH),
            "--release-id",
            shlex.quote(context.release_id),
            "--domain-api-proxy-sync",
            *(["--domain-api-proxy-api-only"] if context.api_only else []),
            "--domain-api-proxy-domain",
            shlex.quote(context.domain),
            "--domain-api-proxy-api-domain",
            shlex.quote(context.api_domain),
            "--domain-api-proxy-backend-url",
            shlex.quote(context.backend_url),
        ]
    )
    result = run_ssh(context, command, check=False)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_sections(
        result.stdout,
        [
            "REMOTE_DATE",
            "BACKUP_PATH",
            "NGINX_CONF_FILE",
            "DOMAIN",
            "API_DOMAIN",
            "BACKEND_URL",
            "DNS_OUTPUT",
            "ROOT_CERT_STATUS",
            "API_CERT_STATUS",
            "CANDIDATE_PREVIEW",
            "NGINX_TEST_OUTPUT",
            "NGINX_RELOAD_OUTPUT",
            "RESTORE_TEST_OUTPUT",
            "INTERNAL_HTTP_DOCS_PROBE",
            "INTERNAL_HTTP_SEND_CODE_PROBE",
            "INTERNAL_HTTPS_DOCS_PROBE",
            "INTERNAL_HTTPS_SEND_CODE_PROBE",
            "FINAL_STATUS",
            "FAIL_REASON",
            "BLOCK_REASON",
        ],
    )
    return summary, result.returncode, result.stderr


def write_record(context: DomainProxyContext, summary: dict[str, str], return_code: int) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    if record_path.exists():
        raise RuntimeError(f"record already exists: {record_path}")

    final_status = summary.get("FINAL_STATUS", "unknown")
    title_status = "通过" if final_status == "passed" else "阻塞" if final_status == "blocked" else "失败"
    title = "API 域名 Nginx 反代同步记录" if context.api_only else "根域名 API Nginx 反代同步记录"
    lines = [
        f"# {title}（{title_status}）",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 操作人：`{context.operator}`",
        f"- 目标主机：`{context.host}`",
        f"- 根域名：`{context.domain}`",
        f"- 现有 API 子域名：`{context.api_domain}`",
        f"- API-only 模式：`{str(context.api_only).lower()}`",
        f"- 后端反代目标：`{context.backend_url}`",
        f"- helper 返回码：`{return_code}`",
        f"- helper 状态：`{final_status}`",
        "",
        "## 2. 远端落点",
        "",
        f"- 备份目录：`{summary.get('BACKUP_PATH')}`",
        f"- nginx 配置：`{summary.get('NGINX_CONF_FILE')}`",
        f"- 根域名证书状态：`{summary.get('ROOT_CERT_STATUS')}`",
        f"- API 子域名证书状态：`{summary.get('API_CERT_STATUS')}`",
        "",
        "## 3. DNS 与阻塞",
        "",
        "```text",
        summary.get("DNS_OUTPUT") or "--",
        "```",
        "",
        "```text",
        summary.get("BLOCK_REASON") or "--",
        "```",
        "",
        "## 4. Nginx 检查",
        "",
        "```text",
        summary.get("NGINX_TEST_OUTPUT") or "--",
        summary.get("NGINX_RELOAD_OUTPUT") or "--",
        "```",
        "",
        "## 5. 内网代理探活",
        "",
        "### 5.1 HTTP OpenAPI",
        "",
        "```text",
        summary.get("INTERNAL_HTTP_DOCS_PROBE") or "--",
        "```",
        "",
        "### 5.2 HTTP sendCode",
        "",
        "```text",
        summary.get("INTERNAL_HTTP_SEND_CODE_PROBE") or "--",
        "```",
        "",
        "### 5.3 HTTPS OpenAPI",
        "",
        "```text",
        summary.get("INTERNAL_HTTPS_DOCS_PROBE") or "--",
        "```",
        "",
        "### 5.4 HTTPS sendCode",
        "",
        "```text",
        summary.get("INTERNAL_HTTPS_SEND_CODE_PROBE") or "--",
        "```",
        "",
        "## 6. 生效配置预览",
        "",
        "```nginx",
        summary.get("CANDIDATE_PREVIEW") or "--",
        "```",
        "",
        "## 7. 失败原因",
        "",
        "```text",
        summary.get("FAIL_REASON") or "--",
        "```",
    ]
    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync host nginx reverse proxy for the root API domain.")
    parser.add_argument("--label", required=True)
    parser.add_argument("--operator", default=DEFAULT_OPERATOR)
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--identity-file", default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)))
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--api-domain", default=DEFAULT_API_DOMAIN)
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Only gate and probe the API domain; do not block on the root domain DNS/certificate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = DomainProxyContext(
        release_id=f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-domain-api-proxy-{args.label}",
        host=args.host,
        user=args.user,
        operator=args.operator,
        identity_file=Path(args.identity_file),
        domain=args.domain,
        api_domain=args.api_domain,
        backend_url=args.backend_url,
        api_only=args.api_only,
    )
    if not context.identity_file.exists():
        raise RuntimeError(f"identity file not found: {context.identity_file}")

    require_key_auth(context)
    require_helper(context)
    summary, return_code, stderr_text = sync_proxy(context)
    record_path = write_record(context, summary, return_code)
    payload = {
        "release_id": context.release_id,
        "status": summary["FINAL_STATUS"],
        "return_code": return_code,
        "domain": context.domain,
        "api_domain": context.api_domain,
        "api_only": context.api_only,
        "backend_url": context.backend_url,
        "record_path": str(record_path),
        "block_reason": summary.get("BLOCK_REASON"),
        "fail_reason": summary.get("FAIL_REASON"),
        "stderr": stderr_text.strip(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if summary["FINAL_STATUS"] == "passed":
        return 0
    if summary["FINAL_STATUS"] == "blocked":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
