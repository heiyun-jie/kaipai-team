import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
SYNC_HELPER_PATH = RUNBOOK_DIR / "scripts" / "sync-release-helper-baseline.py"

SOURCE_ALIAS = "hy-backup"
TARGET_HOST = "101.43.57.62"
TARGET_USER = "kaipaile"
TARGET_UPLOAD_DIR = "/home/kaipaile"
TARGET_APP_DIR = "/opt/clirelay-8388"
TUNNEL_KEY_PATH_108 = "/home/zeno-deocker/.ssh/kaipai_101_reverse_tunnel_ed25519"
TUNNEL_SERVICE_NAME = "kaipai-101-clirelay-proxy-tunnel.service"
TUNNEL_LISTEN = "172.19.0.1:17890"
TUNNEL_TARGET = "127.0.0.1:7890"
CONTAINER_PROXY_URL = "http://172.19.0.1:17890"


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


def resolve_executable(name: str) -> str:
    if os.name == "nt":
        resolved = shutil.which(f"{name}.exe") or shutil.which(f"{name}.cmd") or shutil.which(name)
    else:
        resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required executable not found: {name}")
    return resolved


def run_process(command: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    log(f"local> {' '.join(command)}")
    raw_result = subprocess.run(
        command,
        input=input_text.encode("utf-8") if input_text is not None else None,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    result = subprocess.CompletedProcess(
        args=raw_result.args,
        returncode=raw_result.returncode,
        stdout=raw_result.stdout.decode("utf-8", errors="replace"),
        stderr=raw_result.stderr.decode("utf-8", errors="replace"),
    )
    if check and result.returncode != 0:
        if result.stdout.strip():
            log(f"local stdout:\n{result.stdout}")
        if result.stderr.strip():
            log(f"local stderr:\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
    return result


def run_108_script(script: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_process([resolve_executable("ssh"), SOURCE_ALIAS, "bash", "-s"], input_text=script, check=check)


def run_remote_101(client: paramiko.SSHClient, command: str, *, context: Context, use_sudo: bool = False) -> tuple[int, str, str]:
    actual = f"sudo -S -p '' {command}" if use_sudo else command
    log(f"remote101> {actual}")
    stdin, stdout, stderr = client.exec_command(actual, get_pty=use_sudo)
    if use_sudo:
        stdin.write(context.target_password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    while True:
        while stdout.channel.recv_ready():
            stdout_chunks.append(stdout.channel.recv(65535))
        while stdout.channel.recv_stderr_ready():
            stderr_chunks.append(stdout.channel.recv_stderr(65535))
        if stdout.channel.exit_status_ready():
            exit_code = stdout.channel.recv_exit_status()
            while stdout.channel.recv_ready():
                stdout_chunks.append(stdout.channel.recv(65535))
            while stdout.channel.recv_stderr_ready():
                stderr_chunks.append(stdout.channel.recv_stderr(65535))
            break
        time.sleep(0.1)
    stdout_text = b"".join(stdout_chunks).decode("utf-8", errors="replace").replace(context.target_password, "[REDACTED]")
    stderr_text = b"".join(stderr_chunks).decode("utf-8", errors="replace").replace(context.target_password, "[REDACTED]")
    log(f"remote101< exit={exit_code}")
    return exit_code, stdout_text, stderr_text


def generate_108_key_and_check_proxy() -> tuple[str, str]:
    script = f"""
set -euo pipefail
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
if [[ ! -f {shlex.quote(TUNNEL_KEY_PATH_108)} ]]; then
  ssh-keygen -t ed25519 -f {shlex.quote(TUNNEL_KEY_PATH_108)} -N '' -C 'kaipai-101-clirelay-proxy-tunnel' >/dev/null
fi
chmod 600 {shlex.quote(TUNNEL_KEY_PATH_108)}
echo "public_key_start"
cat {shlex.quote(TUNNEL_KEY_PATH_108)}.pub
echo "public_key_end"
echo "proxy_probe_start"
curl -I -x http://127.0.0.1:7890 --connect-timeout 8 --max-time 20 https://chatgpt.com/backend-api/wham/usage 2>&1 | sed -n '1,30p' || true
echo "proxy_probe_end"
"""
    result = run_108_script(script)
    lines = result.stdout.splitlines()
    try:
        start = lines.index("public_key_start") + 1
        end = lines.index("public_key_end")
    except ValueError as exc:
        raise RuntimeError(f"failed to parse 108 public key output:\n{result.stdout}") from exc
    public_key = "\n".join(lines[start:end]).strip()
    if not public_key.startswith("ssh-ed25519 "):
        raise RuntimeError(f"unexpected tunnel public key: {public_key[:40]}")
    return public_key, result.stdout


def configure_101(context: Context, public_key: str) -> tuple[int, str, str]:
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
    key_options = f'restrict,port-forwarding,permitlisten="{TUNNEL_LISTEN}"'
    authorized_key = f"{key_options} {public_key}"
    script = f"""#!/usr/bin/env bash
set -euo pipefail
release_id={shlex.quote(context.release_id)}
target_dir={shlex.quote(TARGET_APP_DIR)}
proxy_url={shlex.quote(CONTAINER_PROXY_URL)}
authorized_key={shlex.quote(authorized_key)}
sshd_dropin="/etc/ssh/sshd_config.d/kaipai-clirelay-reverse-tunnel.conf"
backup_root="/opt/clirelay-8388-backups/${{release_id}}"
mkdir -p "$backup_root"

echo "remote_date=$(date '+%F %T %z')"
echo "release_id=$release_id"
echo "docker_gateway={TUNNEL_LISTEN.split(':')[0]}"

mkdir -p "/home/{TARGET_USER}/.ssh"
chmod 700 "/home/{TARGET_USER}/.ssh"
touch "/home/{TARGET_USER}/.ssh/authorized_keys"
chmod 600 "/home/{TARGET_USER}/.ssh/authorized_keys"
chown -R "{TARGET_USER}:{TARGET_USER}" "/home/{TARGET_USER}/.ssh"
tmp_auth="$(mktemp)"
grep -v 'kaipai-101-clirelay-proxy-tunnel' "/home/{TARGET_USER}/.ssh/authorized_keys" > "$tmp_auth" || true
printf '%s\\n' "$authorized_key" >> "$tmp_auth"
install -o "{TARGET_USER}" -g "{TARGET_USER}" -m 0600 "$tmp_auth" "/home/{TARGET_USER}/.ssh/authorized_keys"
rm -f "$tmp_auth"

mkdir -p /etc/ssh/sshd_config.d
if [[ -f "$sshd_dropin" ]]; then
  cp -a "$sshd_dropin" "$backup_root/$(basename "$sshd_dropin").before"
fi
printf '%s\\n' 'GatewayPorts clientspecified' > "$sshd_dropin"
sshd -t
if command -v systemctl >/dev/null 2>&1; then
  systemctl reload ssh || systemctl reload sshd
else
  service ssh reload || service sshd reload
fi
echo "sshd_gatewayports=$(sshd -T | awk 'tolower($1)==\"gatewayports\" {{print $2; exit}}')"

cp -a "$target_dir/runtime/config/config.yaml" "$backup_root/config.yaml.before"
python3 - "$target_dir/runtime/config/config.yaml" "$proxy_url" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
proxy_url = sys.argv[2]
text = path.read_text()
new_text, count = re.subn(r'(?m)^proxy-url:.*$', 'proxy-url: "' + proxy_url + '"', text, count=1)
if count != 1:
    raise SystemExit("top-level proxy-url not found")
path.write_text(new_text)
PY
echo "top_level_proxy_url=$(grep -n '^proxy-url:' "$target_dir/runtime/config/config.yaml" | head -1)"

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "Docker Compose is not available" >&2
  exit 4
fi
cd "$target_dir"
"${{compose_cmd[@]}}" --profile green up -d
echo "docker_ps"
docker ps --format 'table {{{{.Names}}}}\\t{{{{.Image}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}' | grep -E 'clirelay-8388|NAMES'
"""
    remote_script = f"{TARGET_UPLOAD_DIR}/{context.release_id}-configure-101-quota-proxy.sh"
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_script, "w") as handle:
                handle.write(script)
        finally:
            sftp.close()
        run_remote_101(client, f"chmod 0700 {shlex.quote(remote_script)}", context=context)
        result = run_remote_101(client, f"bash {shlex.quote(remote_script)}", context=context, use_sudo=True)
        run_remote_101(client, f"rm -f {shlex.quote(remote_script)}", context=context)
        return result
    finally:
        client.close()


def start_108_tunnel(context: Context) -> subprocess.CompletedProcess[str]:
    service = f"""[Unit]
Description=Kaipai 101 clirelay proxy reverse tunnel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/ssh -N -o BatchMode=yes -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=accept-new -i {TUNNEL_KEY_PATH_108} -R {TUNNEL_LISTEN}:{TUNNEL_TARGET} {TARGET_USER}@{TARGET_HOST}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
"""
    escaped_service = shlex.quote(service)
    script = f"""
set -euo pipefail
mkdir -p "$HOME/.config/systemd/user"
printf '%s' {escaped_service} > "$HOME/.config/systemd/user/{TUNNEL_SERVICE_NAME}"
systemctl --user daemon-reload
systemctl --user enable --now {shlex.quote(TUNNEL_SERVICE_NAME)}
sleep 2
systemctl --user --no-pager --full status {shlex.quote(TUNNEL_SERVICE_NAME)} | sed -n '1,80p' || true
systemctl --user is-active --quiet {shlex.quote(TUNNEL_SERVICE_NAME)}
echo "tunnel_processes"
pgrep -af 'kaipai_101_reverse_tunnel_ed25519|172.19.0.1:17890' || true
"""
    return run_108_script(script)


def verify_101(context: Context) -> tuple[int, str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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
    script = f"""#!/usr/bin/env bash
set -euo pipefail
echo "listen_tunnel"
listener=""
for attempt in $(seq 1 20); do
  listener="$(ss -lntup 2>/dev/null | grep '{TUNNEL_LISTEN}' || true)"
  if [[ -n "$listener" ]]; then
    printf '%s\\n' "$listener"
    break
  fi
  sleep 1
done
if [[ -z "$listener" ]]; then
  echo "ERROR: tunnel listener {TUNNEL_LISTEN} is not ready after 20 seconds" >&2
  ss -lntup 2>/dev/null | grep ':17890' || true
  exit 11
fi
echo "host_proxy_probe"
probe_file="$(mktemp)"
curl -I -sS -x {shlex.quote(CONTAINER_PROXY_URL)} --connect-timeout 8 --max-time 25 https://chatgpt.com/backend-api/wham/usage 2>&1 | tee "$probe_file" | sed -n '1,40p'
if ! grep -q 'HTTP/1.1 200 Connection established' "$probe_file"; then
  echo "ERROR: proxy handshake through {CONTAINER_PROXY_URL} did not succeed" >&2
  rm -f "$probe_file"
  exit 12
fi
rm -f "$probe_file"
echo "container_proxy_probe"
docker exec clirelay-8388-green sh -lc 'HTTPS_PROXY={CONTAINER_PROXY_URL} https_proxy={CONTAINER_PROXY_URL} wget -S -O - --timeout=20 https://chatgpt.com/backend-api/wham/usage 2>&1 | head -60' || true
echo "management_channels_probe"
curl -sS --max-time 15 -H 'Authorization: Bearer 123456' http://127.0.0.1:8388/v0/management/image-generation/channels || true
echo
echo "config_proxy"
docker exec clirelay-8388-green sh -lc "grep -n '^proxy-url:' /CLIProxyAPI/config.yaml | head -1" || true
"""
    remote_script = f"{TARGET_UPLOAD_DIR}/{context.release_id}-verify-101-quota-proxy.sh"
    try:
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_script, "w") as handle:
                handle.write(script)
        finally:
            sftp.close()
        run_remote_101(client, f"chmod 0700 {shlex.quote(remote_script)}", context=context)
        result = run_remote_101(client, f"bash {shlex.quote(remote_script)}", context=context, use_sudo=True)
        run_remote_101(client, f"rm -f {shlex.quote(remote_script)}", context=context)
        return result
    finally:
        client.close()


def write_record(
    context: Context,
    key_output: str,
    configure_result: tuple[int, str, str],
    tunnel_result: subprocess.CompletedProcess[str],
    verify_result: tuple[int, str, str],
) -> Path:
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    status = "passed" if configure_result[0] == 0 and tunnel_result.returncode == 0 and verify_result[0] == 0 else "failed"
    lines = [
        "# clirelay-8388 101 配额代理隧道修复记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 目标：`{context.target_host}:{TARGET_APP_DIR}`",
        f"- 隧道来源：`{SOURCE_ALIAS}:{TUNNEL_TARGET}`",
        f"- 隧道监听：`101:{TUNNEL_LISTEN}`",
        f"- 容器代理：`{CONTAINER_PROXY_URL}`",
        f"- 状态：`{status}`",
        "",
        "## 2. 108 代理与密钥准备",
        "",
        "```text",
        redact_key_output(key_output).strip(),
        "```",
        "",
        "## 3. 101 配置输出",
        "",
        "```text",
        configure_result[1].strip() or "--",
        "```",
        "",
        "## 4. 108 隧道服务输出",
        "",
        "```text",
        (tunnel_result.stdout + "\n" + tunnel_result.stderr).strip() or "--",
        "```",
        "",
        "## 5. 101 验证输出",
        "",
        "```text",
        verify_result[1].strip() or "--",
        "```",
        "",
        "## 6. stderr",
        "",
        "```text",
        "\n".join(part.strip() for part in [configure_result[2], verify_result[2]] if part.strip()) or "--",
        "```",
    ]
    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def redact_key_output(text: str) -> str:
    lines = []
    skip = False
    for line in text.splitlines():
        if line == "public_key_start":
            skip = True
            lines.append("public_key_start")
            lines.append("[PUBLIC_KEY_REDACTED]")
            continue
        if line == "public_key_end":
            skip = False
            lines.append(line)
            continue
        if skip:
            continue
        lines.append(line)
    return "\n".join(lines)


def main() -> int:
    context = Context(
        release_id=f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-clirelay-8388-101-quota-proxy-tunnel",
        target_host=TARGET_HOST,
        target_user=TARGET_USER,
        target_password=SYNC_DEFAULTS.DEFAULT_PASSWORD,
    )
    public_key, key_output = generate_108_key_and_check_proxy()
    configure_result = configure_101(context, public_key)
    tunnel_result = start_108_tunnel(context)
    verify_result = verify_101(context)
    record_path = write_record(context, key_output, configure_result, tunnel_result, verify_result)
    status = "passed" if configure_result[0] == 0 and tunnel_result.returncode == 0 and verify_result[0] == 0 else "failed"
    payload = {
        "release_id": context.release_id,
        "status": status,
        "return_code": 0 if status == "passed" else 1,
        "record_path": str(record_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload["return_code"]


if __name__ == "__main__":
    raise SystemExit(main())
