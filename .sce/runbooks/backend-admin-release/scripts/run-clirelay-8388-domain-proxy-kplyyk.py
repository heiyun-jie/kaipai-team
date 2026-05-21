import importlib.util
import json
import shlex
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
SYNC_HELPER_PATH = RUNBOOK_DIR / "scripts" / "sync-release-helper-baseline.py"

TARGET_HOST = "101.43.57.62"
TARGET_USER = "kaipaile"
TARGET_UPLOAD_DIR = "/home/kaipaile"
NGINX_SITE = "/etc/nginx/sites-available/default"


def load_sync_defaults():
    spec = importlib.util.spec_from_file_location("sync_release_helper_baseline", SYNC_HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sync helper defaults: {SYNC_HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SYNC_DEFAULTS = load_sync_defaults()


@dataclass
class Context:
    release_id: str
    target_host: str
    target_user: str
    target_password: str


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def run_remote(client: paramiko.SSHClient, command: str, *, context: Context, use_sudo: bool = False) -> tuple[int, str, str]:
    actual = f"sudo -S -p '' {command}" if use_sudo else command
    log(f"remote101> {actual}")
    stdin, stdout, stderr = client.exec_command(actual, get_pty=use_sudo)
    if use_sudo:
        stdin.write(context.target_password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
    exit_code = stdout.channel.recv_exit_status()
    stdout_text = stdout.read().decode("utf-8", errors="replace").replace(context.target_password, "[REDACTED]")
    stderr_text = stderr.read().decode("utf-8", errors="replace").replace(context.target_password, "[REDACTED]")
    log(f"remote101< exit={exit_code}")
    return exit_code, stdout_text, stderr_text


def deploy_domain_proxy(context: Context) -> tuple[int, str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    log(f"connect target ssh {context.target_user}@{context.target_host}")
    client.connect(
        hostname=context.target_host,
        username=context.target_user,
        password=context.target_password,
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
        look_for_keys=False,
        allow_agent=False,
    )
    marker_start = "# BEGIN clirelay-8388 domain proxy"
    marker_end = "# END clirelay-8388 domain proxy"
    location_block = f"""
    {marker_start}
    location = /manage {{
        return 302 /manage/dashboard;
    }}

    location ^~ /manage/ {{
        proxy_pass http://127.0.0.1:8388;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    location = /v0 {{
        proxy_pass http://127.0.0.1:8388;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    location ^~ /v0/ {{
        proxy_pass http://127.0.0.1:8388;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    location = /v1 {{
        proxy_pass http://127.0.0.1:8388;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}

    location ^~ /v1/ {{
        proxy_pass http://127.0.0.1:8388;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
    {marker_end}
""".strip("\n")
    script = f"""#!/usr/bin/env bash
set -euo pipefail
release_id={shlex.quote(context.release_id)}
site={shlex.quote(NGINX_SITE)}
backup="${{site}}.bak-${{release_id}}"
marker_start={shlex.quote(marker_start)}
marker_end={shlex.quote(marker_end)}
block_file="/tmp/${{release_id}}-clirelay-location.conf"
cp "$site" "$backup"
cat > "$block_file" <<'BLOCK'
{location_block}
BLOCK

python3 - "$site" "$block_file" "$marker_start" "$marker_end" <<'PY'
import pathlib
import re
import sys

site_path = pathlib.Path(sys.argv[1])
block_path = pathlib.Path(sys.argv[2])
marker_start = sys.argv[3]
marker_end = sys.argv[4]
text = site_path.read_text()
block = block_path.read_text().rstrip() + "\\n"

text = re.sub(
    r"\\n\\s*" + re.escape(marker_start) + r".*?" + re.escape(marker_end) + r"\\n",
    "\\n",
    text,
    flags=re.S,
)

server_match = re.search(r"server\\s*\\{{(?P<body>.*?)\\n\\}}", text, flags=re.S)
inserted = False
pieces = []
last = 0
for match in re.finditer(r"server\\s*\\{{.*?\\n\\}}", text, flags=re.S):
    server_text = match.group(0)
    if re.search(r"server_name\\s+kplyyk\\.com\\s*;", server_text):
        if "location ^~ /.well-known/acme-challenge/" in server_text:
            acme = re.search(r"(\\n\\s*location \\^~ /\\.well-known/acme-challenge/ \\{{.*?\\n\\s*\\}}\\n)", server_text, flags=re.S)
            if not acme:
                raise SystemExit("cannot locate acme location in kplyyk.com server")
            insert_at = acme.end()
            server_text = server_text[:insert_at] + "\\n" + block + server_text[insert_at:]
        else:
            insert_at = server_text.find("\\n}}")
            server_text = server_text[:insert_at] + "\\n" + block + server_text[insert_at:]
        inserted = True
    pieces.append(text[last:match.start()])
    pieces.append(server_text)
    last = match.end()
pieces.append(text[last:])

if not inserted:
    raise SystemExit("kplyyk.com server block not found")

site_path.write_text("".join(pieces))
PY

nginx -t
if command -v systemctl >/dev/null 2>&1; then
  systemctl reload nginx
else
  nginx -s reload
fi

echo "nginx_site=$site"
echo "backup=$backup"
echo "probe_internal_manage"
curl -sS --max-time 10 -o /tmp/clirelay-domain-manage -w 'manage_status=%{{http_code}} time=%{{time_total}} size=%{{size_download}}\\n' -H 'Host: kplyyk.com' http://127.0.0.1/manage/dashboard
head -c 120 /tmp/clirelay-domain-manage || true
echo
echo "probe_internal_manage_asset"
asset="$(grep -o '/manage/assets/[^"]*\\.js' /tmp/clirelay-domain-manage | head -1 || true)"
if [[ -n "$asset" ]]; then
  curl -sS --max-time 10 -o /tmp/clirelay-domain-asset -w "asset_status=%{{http_code}} asset=${{asset}} size=%{{size_download}}\\n" -H 'Host: kplyyk.com' "http://127.0.0.1${{asset}}"
else
  echo "asset_status=missing"
fi
"""
    remote_script = f"{TARGET_UPLOAD_DIR}/{context.release_id}-clirelay-domain-proxy.sh"
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_script, "w") as handle:
                handle.write(script)
        finally:
            sftp.close()
        run_remote(client, f"chmod 0700 {shlex.quote(remote_script)}", context=context)
        result = run_remote(client, f"bash {shlex.quote(remote_script)}", context=context, use_sudo=True)
        run_remote(client, f"rm -f {shlex.quote(remote_script)}", context=context)
        return result
    finally:
        client.close()


def write_record(context: Context, result: tuple[int, str, str]) -> Path:
    exit_code, stdout_text, stderr_text = result
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    lines = [
        "# clirelay-8388 kplyyk.com 域名代理发布记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 目标服务器：`{context.target_host}`",
        f"- Nginx 配置：`{NGINX_SITE}`",
        "- 域名入口：`http://kplyyk.com/manage/dashboard`",
        "- 管理 API：`http://kplyyk.com/v0/management/...`",
        "- OpenAI 兼容 API：`http://kplyyk.com/v1/...`",
        "- 后端上游：`http://127.0.0.1:8388`",
        "- 说明：保留 `http://kplyyk.com/` 后台管理端根入口，新增 `/manage`、`/v0`、`/v1` 前缀代理。",
        f"- 返回码：`{exit_code}`",
        "",
        "## 2. stdout",
        "",
        "```text",
        stdout_text.strip() or "--",
        "```",
        "",
        "## 3. stderr",
        "",
        "```text",
        stderr_text.strip() or "--",
        "```",
    ]
    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def main() -> int:
    release_id = f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-domain-proxy-clirelay-8388-kplyyk"
    context = Context(
        release_id=release_id,
        target_host=TARGET_HOST,
        target_user=TARGET_USER,
        target_password=SYNC_DEFAULTS.DEFAULT_PASSWORD,
    )
    result = deploy_domain_proxy(context)
    record_path = write_record(context, result)
    payload = {
        "release_id": context.release_id,
        "status": "passed" if result[0] == 0 else "failed",
        "return_code": result[0],
        "record_path": str(record_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return result[0]


if __name__ == "__main__":
    raise SystemExit(main())
