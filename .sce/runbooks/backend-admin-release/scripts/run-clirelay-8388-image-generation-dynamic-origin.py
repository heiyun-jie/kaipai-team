import importlib.util
import json
import shlex
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

TARGET_HOST = "101.43.57.62"
TARGET_USER = "kaipaile"
TARGET_UPLOAD_DIR = "/home/kaipaile"
TARGET_APP_DIR = "/opt/clirelay-8388"


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


def deploy_patch(context: Context) -> tuple[int, str, str]:
    remote_script = f"{TARGET_UPLOAD_DIR}/{context.release_id}-image-generation-dynamic-origin.sh"
    script = r"""#!/usr/bin/env bash
set -euo pipefail

release_id=__RELEASE_ID__
target_dir=__TARGET_APP_DIR__
panel_dir="${target_dir}/runtime/panel"
backup_root="/opt/clirelay-8388-backups/${release_id}"
mkdir -p "$backup_root"

echo "remote_date=$(date '+%F %T %z')"
echo "release_id=${release_id}"
echo "target_dir=${target_dir}"

if [[ ! -f "${target_dir}/docker-compose.yml" ]]; then
  echo "missing compose file: ${target_dir}/docker-compose.yml" >&2
  exit 2
fi

cp -a "${target_dir}/docker-compose.yml" "${backup_root}/docker-compose.yml.before"
if [[ -d "$panel_dir" ]]; then
  cp -a "$panel_dir" "${backup_root}/panel.before"
fi

if [[ ! -d "$panel_dir" ]] || ! grep -R -q --binary-files=without-match 'gpt-image-2 生图工作台' "$panel_dir" 2>/dev/null; then
  rm -rf "$panel_dir"
  mkdir -p "$panel_dir"
  docker cp clirelay-8388-green:/CLIProxyAPI/panel/. "$panel_dir"/
fi

python3 - "$panel_dir" <<'PY'
import pathlib
import re
import sys


panel_dir = pathlib.Path(sys.argv[1])


def replace_js_function(source: str, name: str, replacement: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    if start < 0:
        return source
    brace = source.find("{", start)
    if brace < 0:
        return source
    depth = 0
    index = brace
    while index < len(source):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[:start] + replacement + source[index + 1 :]
        index += 1
    return source


changed = []
for path in panel_dir.rglob("*"):
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    original = text
    if "gpt-image-2 生图工作台" not in text and "preferredLanHost" not in text and "192.168.1.59" not in text:
        continue
    text = text.replace("目标内网：", "当前入口：")
    text = text.replace("http://192.168.1.59:8388", "自动识别当前入口")
    text = text.replace(
        'const preferredLanHost = "192.168.1.59";',
        'const preferredLanHost = window.location.hostname || "localhost";',
    )
    text = text.replace(
        'const preferredLanOrigin = `http://${preferredLanHost}:8388`;',
        'const preferredLanOrigin = window.location.origin;',
    )
    text = replace_js_function(
        text,
        "redirectLocalhostToLan",
        '''function redirectLocalhostToLan() {
          return false;
        }''',
    )
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))

if not changed:
    dynamic = False
    old_static_host = False
    for path in panel_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "192.168.1.59" in text:
            old_static_host = True
        if "gpt-image-2 生图工作台" in text and "window.location.origin" in text:
            dynamic = True
    if not dynamic or old_static_host:
        raise SystemExit("no image-generation panel file was changed")
    print("patched_files")
    print("already_dynamic")
else:
    print("patched_files")
    for path in changed:
        print(path)
PY

python3 - "${target_dir}/docker-compose.yml" <<'PY'
import pathlib
import re
import sys

compose_path = pathlib.Path(sys.argv[1])
mount_line = "      - ./runtime/panel:/CLIProxyAPI/panel"
text = compose_path.read_text()
lines = text.splitlines()

def add_mount(service_name: str) -> None:
    global lines
    service_pattern = f"  {service_name}:"
    start = next((idx for idx, line in enumerate(lines) if line == service_pattern), None)
    if start is None:
        raise SystemExit(f"service not found: {service_name}")
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if re.match(r"^  [A-Za-z0-9_.-]+:", lines[idx]):
            end = idx
            break
    segment = lines[start:end]
    if mount_line in segment:
        return
    volumes_index = next((start + idx for idx, line in enumerate(segment) if line == "    volumes:"), None)
    if volumes_index is None:
        raise SystemExit(f"volumes section not found: {service_name}")
    lines.insert(volumes_index + 1, mount_line)

add_mount("app-blue")
add_mount("app-green")
compose_path.write_text("\n".join(lines) + "\n")
PY

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "Docker Compose is not available" >&2
  exit 3
fi

cd "$target_dir"
"${compose_cmd[@]}" --profile green up -d

for i in $(seq 1 36); do
  blue_health="$(docker inspect clirelay-8388-blue --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null || true)"
  green_health="$(docker inspect clirelay-8388-green --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null || true)"
  proxy_status="$(docker inspect clirelay-8388-proxy --format '{{.State.Status}}' 2>/dev/null || true)"
  if [[ "$proxy_status" == "running" && "$blue_health" == "healthy" && "$green_health" == "healthy" ]]; then
    break
  fi
  sleep 5
done

echo "docker_ps"
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | grep -E 'clirelay-8388|NAMES'

echo "panel_static_check"
if grep -R --line-number --binary-files=without-match '192\.168\.1\.59' "$panel_dir" 2>/dev/null; then
  echo "old_static_host_still_present" >&2
  exit 4
else
  echo "old_static_host_absent"
fi
grep --line-number 'window.location.origin\|当前入口' "$panel_dir/image-generation.html" | head -40

echo "probe_upstream_image_generation"
curl -sS --max-time 10 http://127.0.0.1:8388/manage/image-generation -o /tmp/clirelay-image-generation-dynamic.html
grep -E 'window.location.origin|当前入口|192\.168\.1\.59' /tmp/clirelay-image-generation-dynamic.html || true
"""
    script = script.replace("__RELEASE_ID__", shlex.quote(context.release_id))
    script = script.replace("__TARGET_APP_DIR__", shlex.quote(TARGET_APP_DIR))

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
        "# clirelay-8388 生图工作台动态入口修复记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 目标服务器：`{context.target_host}`",
        f"- 目标目录：`{TARGET_APP_DIR}`",
        "- 修复点：`/manage/image-generation` 不再写死 `192.168.1.59:8388`，改用 `window.location.origin`。",
        "- 持久化方式：将 `/CLIProxyAPI/panel` 复制到运行态 `runtime/panel` 并通过 compose volume 挂载。",
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
    context = Context(
        release_id=f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-clirelay-8388-image-generation-dynamic-origin",
        target_host=TARGET_HOST,
        target_user=TARGET_USER,
        target_password=SYNC_DEFAULTS.DEFAULT_PASSWORD,
    )
    result = deploy_patch(context)
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
