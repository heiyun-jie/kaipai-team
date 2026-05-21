import argparse
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
RECORDS_DIR = RUNBOOK_DIR / "records"
TMP_DIR = ROOT / "tmp" / "clirelay-8388-runtime-deploy"
SYNC_HELPER_PATH = RUNBOOK_DIR / "scripts" / "sync-release-helper-baseline.py"

SOURCE_ALIAS = "hy-backup"
SOURCE_APP_DIR = "/home/zeno-deocker/docker-apps/clirelay-8388"
TARGET_APP_DIR = "/opt/clirelay-8388"
TARGET_HOST = "101.43.57.62"
TARGET_USER = "kaipaile"
TARGET_UPLOAD_DIR = "/home/kaipaile"

IMAGES = [
    "clirelay-8388:20260502-monitor-token-units",
    "clirelay-8388:20260429-1150-imagepage-fix",
    "clirelay-8388-proxy:20260428-224900-quota-fix2",
]


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
class DeployContext:
    release_id: str
    target_host: str
    target_user: str
    target_password: str
    identity_file: Path
    local_dir: Path
    runtime_archive: Path
    images_archive: Path
    remote_runtime_archive: str
    remote_images_archive: str


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


def ssh_101_base(context: DeployContext) -> list[str]:
    return [
        resolve_executable("ssh"),
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{context.target_user}@{context.target_host}",
    ]


def scp_101_base(context: DeployContext) -> list[str]:
    return [
        resolve_executable("scp"),
        "-i",
        str(context.identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def require_101_key_auth(context: DeployContext) -> None:
    result = run_process(ssh_101_base(context) + ["printf 101-key-ok"])
    if result.stdout.strip() != "101-key-ok":
        raise RuntimeError(f"101 key auth unexpected output: {result.stdout}")


def package_on_108(context: DeployContext) -> tuple[str, str]:
    image_args = " ".join(shlex.quote(image) for image in IMAGES)
    remote_runtime = f"/tmp/{context.release_id}-runtime.tgz"
    remote_images = f"/tmp/{context.release_id}-images.tgz"
    remote_script = f"""
set -euo pipefail
release_id={shlex.quote(context.release_id)}
src={shlex.quote(SOURCE_APP_DIR)}
snapshot="/tmp/${{release_id}}-snapshot"
runtime_archive={shlex.quote(remote_runtime)}
images_archive={shlex.quote(remote_images)}
rm -rf "$snapshot" "$runtime_archive" "$images_archive"
mkdir -p "$snapshot"
rsync -a \
  --exclude '/image' \
  --exclude '/runtime/data/usage.db' \
  --exclude '/runtime/data/usage.db-wal' \
  --exclude '/runtime/data/usage.db-shm' \
  "$src/" "$snapshot/clirelay-8388/"
mkdir -p "$snapshot/clirelay-8388/runtime/data"
SRC_DB="$src/runtime/data/usage.db" DST_DB="$snapshot/clirelay-8388/runtime/data/usage.db" python3 -c "import os, sqlite3; src=sqlite3.connect(os.environ['SRC_DB']); dst=sqlite3.connect(os.environ['DST_DB']); src.backup(dst); dst.close(); src.close()"
tar -C "$snapshot" -czf "$runtime_archive" clirelay-8388
docker save {image_args} | gzip -c > "$images_archive"
sha256sum "$runtime_archive" "$images_archive"
ls -lh "$runtime_archive" "$images_archive"
"""
    result = run_process([resolve_executable("ssh"), SOURCE_ALIAS, "bash", "-s"], input_text=remote_script)
    return remote_runtime, remote_images + "\n" + result.stdout


def download_from_108(context: DeployContext, remote_runtime: str, remote_images: str) -> None:
    context.local_dir.mkdir(parents=True, exist_ok=True)
    run_process([resolve_executable("scp"), f"{SOURCE_ALIAS}:{remote_runtime}", str(context.runtime_archive)])
    run_process([resolve_executable("scp"), f"{SOURCE_ALIAS}:{remote_images}", str(context.images_archive)])


def upload_to_101(context: DeployContext) -> None:
    require_101_key_auth(context)
    run_process(
        scp_101_base(context)
        + [
            str(context.runtime_archive),
            f"{context.target_user}@{context.target_host}:{context.remote_runtime_archive}",
        ]
    )
    run_process(
        scp_101_base(context)
        + [
            str(context.images_archive),
            f"{context.target_user}@{context.target_host}:{context.remote_images_archive}",
        ]
    )


def run_remote_101(client: paramiko.SSHClient, command: str, *, context: DeployContext, use_sudo: bool = False) -> tuple[int, str, str]:
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


def deploy_on_101(context: DeployContext) -> tuple[int, str, str]:
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
    script = f"""#!/usr/bin/env bash
set -euo pipefail
release_id={shlex.quote(context.release_id)}
runtime_archive={shlex.quote(context.remote_runtime_archive)}
images_archive={shlex.quote(context.remote_images_archive)}
target_dir={shlex.quote(TARGET_APP_DIR)}
release_root="/opt/clirelay-8388-releases/${{release_id}}"
backup_root="/opt/clirelay-8388-backups/${{release_id}}"
mkdir -p "$release_root" "$backup_root"

echo "remote_date=$(date '+%F %T %z')"
echo "release_id=$release_id"
echo "before_resource"
free -h
df -hT -x tmpfs -x devtmpfs
ss -lntup 2>/dev/null | grep ':8388' || true

if docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  compose_cmd=(docker-compose)
else
  echo "Docker Compose is not available" >&2
  exit 4
fi
echo "compose_command=${{compose_cmd[*]}}"

install -m 0600 "$runtime_archive" "$release_root/runtime.tgz"
install -m 0600 "$images_archive" "$release_root/images.tgz"
rm -f "$runtime_archive" "$images_archive"
sha256sum "$release_root/runtime.tgz" "$release_root/images.tgz"

if docker ps -a --format '{{{{.Names}}}}' | grep -Eq '^clirelay-8388-(proxy|blue|green)$'; then
  if [[ -f "$target_dir/docker-compose.yml" ]]; then
    (cd "$target_dir" && "${{compose_cmd[@]}}" --profile green down) || true
  else
    docker rm -f clirelay-8388-proxy clirelay-8388-blue clirelay-8388-green || true
  fi
fi

if [[ -d "$target_dir" ]]; then
  mv "$target_dir" "$backup_root/clirelay-8388.before"
fi

gunzip -c "$release_root/images.tgz" | docker load
tar -C /opt -xzf "$release_root/runtime.tgz"

if [[ ! -d "$target_dir" ]]; then
  echo "target dir missing after extract: $target_dir" >&2
  exit 3
fi

cp -a "$target_dir/runtime/config/config.yaml" "$target_dir/runtime/config/config.yaml.before-101-runtime-deploy"
sed -i -E 's#^proxy-url:.*#proxy-url: ""#' "$target_dir/runtime/config/config.yaml"
chown -R root:root "$target_dir"

cd "$target_dir"
"${{compose_cmd[@]}}" --profile green up -d

for i in $(seq 1 36); do
  proxy_status="$(docker inspect clirelay-8388-proxy --format '{{{{.State.Status}}}}' 2>/dev/null || true)"
  blue_health="$(docker inspect clirelay-8388-blue --format '{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}none{{{{end}}}}' 2>/dev/null || true)"
  green_health="$(docker inspect clirelay-8388-green --format '{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}none{{{{end}}}}' 2>/dev/null || true)"
  if [[ "$proxy_status" == "running" && "$blue_health" == "healthy" && "$green_health" == "healthy" ]]; then
    break
  fi
  sleep 5
done

echo "docker_ps"
docker ps --format 'table {{{{.Names}}}}\\t{{{{.Image}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}' | grep -E 'clirelay-8388|NAMES'
echo "health"
docker inspect clirelay-8388-proxy clirelay-8388-blue clirelay-8388-green --format '{{{{.Name}}}} status={{{{.State.Status}}}} health={{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}none{{{{end}}}} restart={{{{.RestartCount}}}} oom={{{{.State.OOMKilled}}}}'
echo "probe_dashboard"
curl -sS --max-time 10 -o /tmp/clirelay-8388-dashboard -w 'dashboard_status=%{{http_code}} time=%{{time_total}} size=%{{size_download}}\\n' http://127.0.0.1:8388/manage/dashboard || true
head -c 160 /tmp/clirelay-8388-dashboard || true
echo
echo "after_resource"
free -h
df -hT -x tmpfs -x devtmpfs
du -h -d 1 /opt/clirelay-8388 2>/dev/null | sort -h
"""
    # Upload and execute through a temporary file to avoid sudo/stdin interaction.
    remote_script = f"{TARGET_UPLOAD_DIR}/{context.release_id}-deploy.sh"
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


def write_record(context: DeployContext, package_output: str, deploy_result: tuple[int, str, str]) -> Path:
    exit_code, stdout_text, stderr_text = deploy_result
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    lines = [
        "# clirelay-8388 运行态部署到 101 记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 来源：`{SOURCE_ALIAS}:{SOURCE_APP_DIR}`",
        f"- 目标：`{context.target_host}:{TARGET_APP_DIR}`",
        "- 部署方式：`运行态迁移，不在 101 构建`",
        "- 运行配置调整：`proxy-url` 从 108 局域网代理改为空代理",
        f"- 返回码：`{exit_code}`",
        "",
        "## 2. 镜像",
        "",
        "```text",
        "\n".join(IMAGES),
        "```",
        "",
        "## 3. 108 打包输出",
        "",
        "```text",
        package_output.strip(),
        "```",
        "",
        "## 4. 101 部署输出",
        "",
        "```text",
        stdout_text.strip() or "--",
        "```",
        "",
        "## 5. stderr",
        "",
        "```text",
        stderr_text.strip() or "--",
        "```",
    ]
    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy the clirelay-8388 runtime from 108 to 101 without building on 101.")
    parser.add_argument("--label", default="clirelay-8388-runtime-101")
    parser.add_argument("--target-host", default=TARGET_HOST)
    parser.add_argument("--target-user", default=TARGET_USER)
    parser.add_argument("--target-password", default=SYNC_DEFAULTS.DEFAULT_PASSWORD)
    parser.add_argument("--identity-file", default=str(SYNC_DEFAULTS.DEFAULT_IDENTITY_FILE))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    release_id = f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-{args.label}"
    local_dir = TMP_DIR / release_id
    context = DeployContext(
        release_id=release_id,
        target_host=args.target_host,
        target_user=args.target_user,
        target_password=args.target_password,
        identity_file=Path(args.identity_file),
        local_dir=local_dir,
        runtime_archive=local_dir / "runtime.tgz",
        images_archive=local_dir / "images.tgz",
        remote_runtime_archive=f"{TARGET_UPLOAD_DIR}/{release_id}-runtime.tgz",
        remote_images_archive=f"{TARGET_UPLOAD_DIR}/{release_id}-images.tgz",
    )
    remote_runtime, package_output = package_on_108(context)
    remote_images = f"/tmp/{context.release_id}-images.tgz"
    download_from_108(context, remote_runtime, remote_images)
    upload_to_101(context)
    deploy_result = deploy_on_101(context)
    record_path = write_record(context, package_output, deploy_result)
    payload = {
        "release_id": context.release_id,
        "status": "passed" if deploy_result[0] == 0 else "failed",
        "return_code": deploy_result[0],
        "record_path": str(record_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return deploy_result[0]


if __name__ == "__main__":
    raise SystemExit(main())
