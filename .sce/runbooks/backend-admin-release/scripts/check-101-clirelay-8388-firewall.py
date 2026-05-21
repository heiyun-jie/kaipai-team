import importlib.util
import shlex
import sys
import time
from pathlib import Path

import paramiko


ROOT = Path(__file__).resolve().parents[4]
SYNC_HELPER_PATH = ROOT / ".sce" / "runbooks" / "backend-admin-release" / "scripts" / "sync-release-helper-baseline.py"
TARGET_HOST = "101.43.57.62"
TARGET_USER = "kaipaile"


def load_sync_defaults():
    spec = importlib.util.spec_from_file_location("sync_release_helper_baseline", SYNC_HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sync helper defaults: {SYNC_HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_channel(channel, timeout_seconds: int = 30) -> tuple[int, str, str]:
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    deadline = time.time() + timeout_seconds
    while True:
        while channel.recv_ready():
            stdout_chunks.append(channel.recv(65535))
        while channel.recv_stderr_ready():
            stderr_chunks.append(channel.recv_stderr(65535))
        if channel.exit_status_ready():
            exit_code = channel.recv_exit_status()
            while channel.recv_ready():
                stdout_chunks.append(channel.recv(65535))
            while channel.recv_stderr_ready():
                stderr_chunks.append(channel.recv_stderr(65535))
            return (
                exit_code,
                b"".join(stdout_chunks).decode("utf-8", errors="replace"),
                b"".join(stderr_chunks).decode("utf-8", errors="replace"),
            )
        if time.time() > deadline:
            channel.close()
            return (
                124,
                b"".join(stdout_chunks).decode("utf-8", errors="replace"),
                b"".join(stderr_chunks).decode("utf-8", errors="replace") + "\nlocal timeout waiting for remote command",
            )
        time.sleep(0.1)


def run_sudo(client: paramiko.SSHClient, password: str, command: str) -> tuple[int, str, str]:
    actual = "sudo -S -p '' bash -lc " + shlex.quote(command)
    stdin, stdout, stderr = client.exec_command(actual, get_pty=True)
    stdin.write(password + "\n")
    stdin.flush()
    stdin.channel.shutdown_write()
    exit_code, stdout_text, stderr_text = read_channel(stdout.channel)
    return (
        exit_code,
        stdout_text.replace(password, "[REDACTED]"),
        stderr_text.replace(password, "[REDACTED]"),
    )


def main() -> int:
    defaults = load_sync_defaults()
    password = defaults.DEFAULT_PASSWORD
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=TARGET_HOST,
        username=TARGET_USER,
        password=password,
        timeout=20,
        banner_timeout=20,
        auth_timeout=20,
        look_for_keys=False,
        allow_agent=False,
    )
    checks = [
        ("docker_ps", "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}' | grep -E 'clirelay-8388|NAMES' || true"),
        ("listen_8388", "ss -lntup 2>/dev/null | grep ':8388' || true"),
        ("ufw", "ufw status verbose 2>&1 || true"),
        ("firewalld", "systemctl is-active firewalld 2>&1 || true; firewall-cmd --list-all 2>&1 || true"),
        ("iptables_input", "iptables -S INPUT 2>&1 | sed -n '1,80p'"),
        ("iptables_docker_user", "iptables -S DOCKER-USER 2>&1 | sed -n '1,80p'"),
        ("nft_relevant", "nft list ruleset 2>/dev/null | grep -En '8388|drop|reject' | head -80 || true"),
    ]
    try:
        for name, command in checks:
            print(f"--- {name} ---")
            exit_code, stdout_text, stderr_text = run_sudo(client, password, command)
            print(f"exit={exit_code}")
            print(stdout_text.strip() or "--")
            if stderr_text.strip():
                print("stderr:")
                print(stderr_text.strip())
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
