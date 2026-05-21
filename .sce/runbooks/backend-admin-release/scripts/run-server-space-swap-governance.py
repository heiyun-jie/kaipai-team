import argparse
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
class GovernanceContext:
    release_id: str
    host: str
    user: str
    password: str
    cutoff: str
    binlog_before: str
    swap_size: str
    swap_file: str


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def run_remote(client: paramiko.SSHClient, command: str, *, password: str = "", use_sudo: bool = False) -> tuple[int, str, str]:
    actual = f"sudo -S -p '' {command}" if use_sudo else command
    log(f"remote> {actual}")
    stdin, stdout, stderr = client.exec_command(actual, get_pty=use_sudo)
    if use_sudo:
        stdin.write(password + "\n")
        stdin.flush()
        stdin.channel.shutdown_write()
    exit_code = stdout.channel.recv_exit_status()
    stdout_text = stdout.read().decode("utf-8", errors="replace")
    stderr_text = stderr.read().decode("utf-8", errors="replace")
    if password:
        stdout_text = stdout_text.replace(password, "[REDACTED]")
        stderr_text = stderr_text.replace(password, "[REDACTED]")
    log(f"remote< exit={exit_code}")
    return exit_code, stdout_text, stderr_text


def require_ok(result: tuple[int, str, str], label: str) -> tuple[int, str, str]:
    exit_code, stdout_text, stderr_text = result
    if exit_code != 0:
        raise RuntimeError(f"{label} failed\nstdout:\n{stdout_text}\nstderr:\n{stderr_text}")
    return result


def shell_script(context: GovernanceContext) -> str:
    allowed_paths = [
        "/opt/kaipai/backups/releases",
        "/opt/kaipai/builds",
        "/opt/kaipai/repos/kaipai-admin-releases",
    ]
    allowed_cases = "|".join(allowed_paths)
    return f"""#!/usr/bin/env bash
set -euo pipefail

release_id={shlex.quote(context.release_id)}
cutoff={shlex.quote(context.cutoff)}
binlog_before={shlex.quote(context.binlog_before)}
swap_size={shlex.quote(context.swap_size)}
swap_file={shlex.quote(context.swap_file)}
record_root="/opt/kaipai/backups/ops-governance/${{release_id}}"
mkdir -p "$record_root"

emit() {{
  local name="$1"
  shift
  printf '__%s_BEGIN__\\n' "$name"
  "$@" || true
  printf '__%s_END__\\n' "$name"
}}

emit_text() {{
  local name="$1"
  local text="$2"
  printf '__%s_BEGIN__\\n%s\\n__%s_END__\\n' "$name" "$text" "$name"
}}

safe_clean_old_dirs() {{
  local base="$1"
  case "$base" in
    {allowed_cases}) ;;
    *) echo "refuse unsupported cleanup base: $base" >&2; return 2 ;;
  esac

  local resolved_base
  resolved_base="$(readlink -f "$base")"
  local list_file="$record_root/$(basename "$base").cleanup-candidates.txt"
  local size_file="$record_root/$(basename "$base").cleanup-size-before.txt"
  : > "$list_file"
  find "$base" -maxdepth 1 -mindepth 1 -type d ! -newermt "$cutoff" -print0 |
    while IFS= read -r -d '' target; do
      local resolved_target
      resolved_target="$(readlink -f "$target")"
      case "$resolved_target" in
        "$resolved_base"/*) printf '%s\\0' "$resolved_target" >> "$list_file" ;;
        *) echo "refuse path outside base: $target -> $resolved_target" >&2; return 3 ;;
      esac
    done

  if [[ -s "$list_file" ]]; then
    du -ch --files0-from="$list_file" > "$size_file" 2>&1 || true
    while IFS= read -r -d '' target; do
      rm -rf --one-file-system -- "$target"
    done < "$list_file"
  else
    printf '0\\ttotal\\n' > "$size_file"
  fi
}}

echo "remote_date=$(date '+%F %T %z')"
echo "release_id=$release_id"
echo "cutoff=$cutoff"
echo "binlog_before=$binlog_before"
echo "swap_size=$swap_size"
echo "swap_file=$swap_file"

emit BEFORE_RESOURCE bash -lc "free -h; df -hT -x tmpfs -x devtmpfs; du -h -d 1 /opt/kaipai 2>/dev/null | sort -h"
emit BEFORE_BINLOG bash -lc "ls -lh /opt/kaipai/mysql-data/binlog.* 2>/dev/null; du -ch /opt/kaipai/mysql-data/binlog.* 2>/dev/null | tail -n 1"

safe_clean_old_dirs /opt/kaipai/backups/releases
safe_clean_old_dirs /opt/kaipai/builds
safe_clean_old_dirs /opt/kaipai/repos/kaipai-admin-releases

emit CLEANUP_MANIFEST bash -lc "for f in '$record_root'/*.cleanup-size-before.txt; do echo ====\\$f; tail -n 20 \\$f; done; for f in '$record_root'/*.cleanup-candidates.txt; do echo ====\\$f; tr '\\0' '\\n' < \\$f | sed -n '1,20p'; echo count=\\$(tr '\\0' '\\n' < \\$f | sed '/^$/d' | wc -l); done"

db_dump="$record_root/kaipai_dev-before-binlog-purge.sql.gz"
if docker ps --format '{{{{.Names}}}}' | grep -qx 'kaipai-mysql'; then
  docker exec -e MYSQL_PWD=root123456 kaipai-mysql mysqldump --single-transaction --routines --triggers -uroot kaipai_dev | gzip -c > "$db_dump"
  chmod 0600 "$db_dump"
  docker exec -e MYSQL_PWD=root123456 kaipai-mysql mysql -uroot -e "SHOW REPLICA STATUS\\G" > "$record_root/mysql-replica-status-before.txt" 2>&1 || true
  if [[ -s "$record_root/mysql-replica-status-before.txt" ]] && grep -q 'Replica_IO_State\\|Slave_IO_State' "$record_root/mysql-replica-status-before.txt"; then
    echo "replica status is non-empty; skip binlog purge" > "$record_root/mysql-binlog-purge.txt"
  else
    docker exec -e MYSQL_PWD=root123456 kaipai-mysql mysql -uroot -e "SHOW BINARY LOGS; PURGE BINARY LOGS BEFORE '$binlog_before'; SHOW BINARY LOGS;" > "$record_root/mysql-binlog-purge.txt" 2>&1
    {{
      docker exec -e MYSQL_PWD=root123456 kaipai-mysql mysql -uroot -e "SET PERSIST binlog_expire_logs_seconds = 604800; SHOW VARIABLES LIKE 'binlog_expire_logs_seconds';"
    }} >> "$record_root/mysql-binlog-purge.txt" 2>&1 || {{
      echo "SET PERSIST failed; applying SET GLOBAL fallback for current mysqld lifetime" >> "$record_root/mysql-binlog-purge.txt"
      docker exec -e MYSQL_PWD=root123456 kaipai-mysql mysql -uroot -e "SET GLOBAL binlog_expire_logs_seconds = 604800; SHOW VARIABLES LIKE 'binlog_expire_logs_seconds';" >> "$record_root/mysql-binlog-purge.txt" 2>&1 || true
    }}
  fi
else
  echo "kaipai-mysql container not running; skip binlog purge" > "$record_root/mysql-binlog-purge.txt"
fi

emit MYSQL_GOVERNANCE bash -lc "ls -lh '$db_dump' 2>/dev/null || true; echo '-- replica --'; cat '$record_root/mysql-replica-status-before.txt' 2>/dev/null || true; echo '-- purge --'; cat '$record_root/mysql-binlog-purge.txt' 2>/dev/null || true"

if [[ ! "$swap_file" = /* ]]; then
  echo "swap file must be absolute: $swap_file" >&2
  exit 4
fi
if swapon --show=NAME --noheadings | grep -qx "$swap_file"; then
  echo "swap already active: $swap_file" > "$record_root/swap.txt"
else
  if [[ ! -e "$swap_file" ]]; then
    fallocate -l "$swap_size" "$swap_file" || dd if=/dev/zero of="$swap_file" bs=1M count=4096 status=progress
  fi
  chmod 0600 "$swap_file"
  mkswap -f "$swap_file" > "$record_root/swap-mkswap.txt" 2>&1
  swapon "$swap_file"
  echo "swap enabled: $swap_file $swap_size" > "$record_root/swap.txt"
fi
grep -qF "$swap_file none swap" /etc/fstab || printf '%s none swap sw 0 0\\n' "$swap_file" >> /etc/fstab
printf 'vm.swappiness=10\\n' > /etc/sysctl.d/99-kaipai-swap.conf
sysctl -p /etc/sysctl.d/99-kaipai-swap.conf > "$record_root/sysctl-swap.txt" 2>&1 || true

emit SWAP_STATUS bash -lc "cat '$record_root/swap.txt' 2>/dev/null; swapon --show; grep -nF '$swap_file' /etc/fstab; cat /etc/sysctl.d/99-kaipai-swap.conf; cat '$record_root/sysctl-swap.txt' 2>/dev/null"
emit AFTER_RESOURCE bash -lc "free -h; df -hT -x tmpfs -x devtmpfs; du -h -d 1 /opt/kaipai 2>/dev/null | sort -h"
emit AFTER_BINLOG bash -lc "ls -lh /opt/kaipai/mysql-data/binlog.* 2>/dev/null; du -ch /opt/kaipai/mysql-data/binlog.* 2>/dev/null | tail -n 1"
emit SERVICE_STATUS bash -lc "docker ps --format 'table {{{{.Names}}}}\\t{{{{.Image}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}'; curl -sS --max-time 10 -o /tmp/kp-docs-probe -w 'docs_status=%{{http_code}} time=%{{time_total}} size=%{{size_download}}\\n' http://127.0.0.1:8080/api/v3/api-docs 2>&1; head -c 120 /tmp/kp-docs-probe; echo"
emit_text RECORD_ROOT "$record_root"
"""


def parse_sections(output: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    lines = output.splitlines()
    current = None
    buf: list[str] = []
    for line in lines:
      if line.startswith("__") and line.endswith("_BEGIN__"):
          current = line[2:-8]
          buf = []
      elif line.startswith("__") and line.endswith("_END__") and current == line[2:-6]:
          sections[current] = "\n".join(buf).strip()
          current = None
          buf = []
      elif current is not None:
          buf.append(line)
    return sections


def write_record(context: GovernanceContext, stdout_text: str, stderr_text: str, exit_code: int) -> Path:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    sections = parse_sections(stdout_text)
    record_path = RECORDS_DIR / f"{context.release_id}.md"
    lines = [
        "# 101 空间治理与 Swap 启用记录",
        "",
        "## 1. 基本信息",
        "",
        f"- 批次号：`{context.release_id}`",
        f"- 执行时间：`{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}`",
        f"- 目标主机：`{context.host}`",
        f"- 清理 cutoff：`{context.cutoff}`",
        f"- binlog purge before：`{context.binlog_before}`",
        f"- swap：`{context.swap_file}` / `{context.swap_size}`",
        f"- 远端返回码：`{exit_code}`",
        f"- 远端记录目录：`{sections.get('RECORD_ROOT', '--')}`",
        "",
        "## 2. 治理前资源",
        "",
        "```text",
        sections.get("BEFORE_RESOURCE", "--"),
        "```",
        "",
        "## 3. 清理清单",
        "",
        "```text",
        sections.get("CLEANUP_MANIFEST", "--"),
        "```",
        "",
        "## 4. MySQL Binlog 治理",
        "",
        "```text",
        sections.get("MYSQL_GOVERNANCE", "--"),
        "```",
        "",
        "## 5. Swap 状态",
        "",
        "```text",
        sections.get("SWAP_STATUS", "--"),
        "```",
        "",
        "## 6. 治理后资源",
        "",
        "```text",
        sections.get("AFTER_RESOURCE", "--"),
        "```",
        "",
        "## 7. Binlog 治理后",
        "",
        "```text",
        sections.get("AFTER_BINLOG", "--"),
        "```",
        "",
        "## 8. 服务状态",
        "",
        "```text",
        sections.get("SERVICE_STATUS", "--"),
        "```",
        "",
        "## 9. stderr",
        "",
        "```text",
        stderr_text.strip() or "--",
        "```",
    ]
    record_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return record_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run controlled space cleanup and swap setup on the 101 server.")
    parser.add_argument("--host", default=SYNC_DEFAULTS.DEFAULT_HOST)
    parser.add_argument("--user", default=SYNC_DEFAULTS.DEFAULT_USER)
    parser.add_argument("--password", default=SYNC_DEFAULTS.DEFAULT_PASSWORD)
    parser.add_argument("--cutoff", default="2026-05-08")
    parser.add_argument("--binlog-before", default="2026-05-08 00:00:00")
    parser.add_argument("--swap-size", default="4G")
    parser.add_argument("--swap-file", default="/swapfile")
    parser.add_argument("--label", default="space-swap-governance")
    parser.add_argument("--kill-release-id", default="", help="Stop a stale remote governance script by release id and exit.")
    parser.add_argument("--kill-pid", default="", help="Stop a stale remote process by numeric pid and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.kill_pid:
        if not args.kill_pid.isdigit():
            raise RuntimeError(f"unsafe pid: {args.kill_pid}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        log(f"connect kill-pid ssh {args.user}@{args.host}")
        client.connect(
            hostname=args.host,
            username=args.user,
            password=args.password,
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
            look_for_keys=False,
            allow_agent=False,
        )
        try:
            command = f"bash -lc 'kill {args.kill_pid} || true; sleep 1; kill -9 {args.kill_pid} 2>/dev/null || true; ps -fp {args.kill_pid} || true'"
            exit_code, stdout_text, stderr_text = run_remote(client, command, password=args.password, use_sudo=True)
        finally:
            client.close()
        print(json.dumps({"pid": args.kill_pid, "return_code": exit_code, "stdout": stdout_text, "stderr": stderr_text}, ensure_ascii=False, indent=2))
        return exit_code

    if args.kill_release_id:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        log(f"connect kill-stale ssh {args.user}@{args.host}")
        client.connect(
            hostname=args.host,
            username=args.user,
            password=args.password,
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
            look_for_keys=False,
            allow_agent=False,
        )
        try:
            safe_release_id = "".join(ch for ch in args.kill_release_id if ch.isalnum() or ch in "._-")
            if safe_release_id != args.kill_release_id or not safe_release_id:
                raise RuntimeError(f"unsafe release id: {args.kill_release_id}")
            command = (
                "bash -lc "
                + shlex.quote(
                    f"pkill -f {shlex.quote(safe_release_id + '.sh')} || true; "
                    f"sleep 1; ps -ef | grep {shlex.quote(safe_release_id)} | grep -v grep || true"
                )
            )
            exit_code, stdout_text, stderr_text = run_remote(client, command, password=args.password, use_sudo=True)
        finally:
            client.close()
        print(json.dumps({"release_id": args.kill_release_id, "return_code": exit_code, "stdout": stdout_text, "stderr": stderr_text}, ensure_ascii=False, indent=2))
        return exit_code

    context = GovernanceContext(
        release_id=f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-{args.label}",
        host=args.host,
        user=args.user,
        password=args.password,
        cutoff=args.cutoff,
        binlog_before=args.binlog_before,
        swap_size=args.swap_size,
        swap_file=args.swap_file,
    )
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    log(f"connect governance ssh {context.user}@{context.host}")
    client.connect(
        hostname=context.host,
        username=context.user,
        password=context.password,
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
        look_for_keys=False,
        allow_agent=False,
    )
    try:
        remote_script = f"/home/{context.user}/{context.release_id}.sh"
        sftp = client.open_sftp()
        try:
            with sftp.open(remote_script, "w") as handle:
                handle.write(shell_script(context))
        finally:
            sftp.close()
        require_ok(run_remote(client, f"chmod 0700 {shlex.quote(remote_script)}"), "chmod remote script")
        exit_code, stdout_text, stderr_text = run_remote(
            client,
            f"bash {shlex.quote(remote_script)}",
            password=context.password,
            use_sudo=True,
        )
        run_remote(client, f"rm -f {shlex.quote(remote_script)}")
    finally:
        client.close()
    record_path = write_record(context, stdout_text, stderr_text, exit_code)
    payload = {
        "release_id": context.release_id,
        "host": context.host,
        "status": "passed" if exit_code == 0 else "failed",
        "return_code": exit_code,
        "record_path": str(record_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
