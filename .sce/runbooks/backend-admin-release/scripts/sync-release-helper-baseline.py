import argparse
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
SCRIPTS_DIR = RUNBOOK_DIR / "scripts"

DEFAULT_HOST = os.getenv("KAIPAI_RELEASE_HOST", "")
DEFAULT_USER = os.getenv("KAIPAI_RELEASE_USER", "")
DEFAULT_PASSWORD = os.getenv("KAIPAI_RELEASE_PASSWORD", "")
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_KNOWN_HOSTS_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "known_hosts"
REMOTE_ADMIN_HELPER_PATH = "/usr/local/bin/kaipai-admin-release-helper.sh"
REMOTE_BACKEND_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
REMOTE_SUDOERS_PATH = "/etc/sudoers.d/kaipai-admin-release"


@dataclass
class HelperSyncContext:
    host: str
    user: str
    password: str
    operator: str
    identity_file: Path
    known_hosts_file: Path


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
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )


def ensure_keypair(identity_file: Path) -> None:
    public_key_file = identity_file.with_suffix(identity_file.suffix + ".pub")
    if identity_file.exists() and public_key_file.exists():
        log(f"reuse existing release key {identity_file}")
        return
    identity_file.parent.mkdir(parents=True, exist_ok=True)
    ssh_keygen = resolve_executable("ssh-keygen")
    run_process(
        [
            ssh_keygen,
            "-t",
            "ed25519",
            "-f",
            str(identity_file),
            "-N",
            "",
            "-C",
            "kaipai-admin-release",
        ]
    )
    log(f"generated release key {identity_file}")


def run_remote(
    client: paramiko.SSHClient,
    command: str,
    *,
    password: str = "",
    use_sudo: bool = False,
) -> tuple[int, str, str]:
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


def require_ok(result: tuple[int, str, str], command: str) -> tuple[int, str, str]:
    exit_code, stdout_text, stderr_text = result
    if exit_code != 0:
        raise RuntimeError(f"command failed: {command}\nstdout:\n{stdout_text}\nstderr:\n{stderr_text}")
    return result


def ssh_base(context: HelperSyncContext) -> list[str]:
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
        "StrictHostKeyChecking=yes",
        "-o",
        f"UserKnownHostsFile={context.known_hosts_file}",
        f"{context.user}@{context.host}",
    ]


def verify_native_auth(context: HelperSyncContext) -> None:
    result = run_process(ssh_base(context) + ["printf 'helper-sync-ok'"], capture_output=True)
    if result.stdout.strip() != "helper-sync-ok":
        raise RuntimeError("native ssh key verification returned unexpected output")
    log("native ssh key auth verified")


def verify_helpers(context: HelperSyncContext) -> None:
    admin_result = run_process(
        ssh_base(context) + [f"sudo -n {shlex.quote(REMOTE_ADMIN_HELPER_PATH)} --healthcheck"],
        capture_output=True,
    )
    if admin_result.stdout.strip() != "helper-ok":
        raise RuntimeError("remote admin helper healthcheck returned unexpected output")
    backend_result = run_process(
        ssh_base(context) + [f"sudo -n {shlex.quote(REMOTE_BACKEND_HELPER_PATH)} --healthcheck"],
        capture_output=True,
    )
    if backend_result.stdout.strip() != "helper-ok":
        raise RuntimeError("remote backend helper healthcheck returned unexpected output")
    log("remote admin/backend helper and sudoers verified")


def create_ssh_client(context: HelperSyncContext) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.load_host_keys(str(context.known_hosts_file))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    return client


def sync_helper_baseline(context: HelperSyncContext) -> None:
    admin_helper_script = (SCRIPTS_DIR / "kaipai-admin-release-helper.sh").read_text(encoding="utf-8")
    backend_helper_script = (SCRIPTS_DIR / "kaipai-backend-release-helper.sh").read_text(encoding="utf-8")
    sudoers_content = (
        f"{context.user} ALL=(root) NOPASSWD: {REMOTE_ADMIN_HELPER_PATH}\n"
        f"{context.user} ALL=(root) NOPASSWD: {REMOTE_BACKEND_HELPER_PATH}\n"
    )
    public_key = context.identity_file.with_suffix(context.identity_file.suffix + ".pub").read_text(encoding="utf-8").strip()

    client = create_ssh_client(context)
    log(f"connect helper sync ssh {context.user}@{context.host}")
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
        auth_command = (
            "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && "
            f"grep -qxF {shlex.quote(public_key)} ~/.ssh/authorized_keys || printf '%s\\n' {shlex.quote(public_key)} >> ~/.ssh/authorized_keys"
        )
        require_ok(run_remote(client, auth_command), auth_command)

        admin_helper_tmp = f"/home/{context.user}/kaipai-admin-release-helper.sh.tmp"
        backend_helper_tmp = f"/home/{context.user}/kaipai-backend-release-helper.sh.tmp"
        sudoers_tmp = f"/home/{context.user}/kaipai-admin-release.sudoers.tmp"
        sftp = client.open_sftp()
        try:
            with sftp.open(admin_helper_tmp, "w") as remote_helper:
                remote_helper.write(admin_helper_script)
            with sftp.open(backend_helper_tmp, "w") as remote_helper:
                remote_helper.write(backend_helper_script)
            with sftp.open(sudoers_tmp, "w") as remote_sudoers:
                remote_sudoers.write(sudoers_content)
        finally:
            sftp.close()

        install_admin_helper = f"install -o root -g root -m 0755 {shlex.quote(admin_helper_tmp)} {shlex.quote(REMOTE_ADMIN_HELPER_PATH)}"
        require_ok(run_remote(client, install_admin_helper, password=context.password, use_sudo=True), install_admin_helper)

        install_backend_helper = f"install -o root -g root -m 0755 {shlex.quote(backend_helper_tmp)} {shlex.quote(REMOTE_BACKEND_HELPER_PATH)}"
        require_ok(run_remote(client, install_backend_helper, password=context.password, use_sudo=True), install_backend_helper)

        install_sudoers = f"install -o root -g root -m 0440 {shlex.quote(sudoers_tmp)} {shlex.quote(REMOTE_SUDOERS_PATH)}"
        require_ok(run_remote(client, install_sudoers, password=context.password, use_sudo=True), install_sudoers)

        visudo_check = f"visudo -cf {shlex.quote(REMOTE_SUDOERS_PATH)}"
        require_ok(run_remote(client, visudo_check, password=context.password, use_sudo=True), visudo_check)

        cleanup = f"rm -f {shlex.quote(admin_helper_tmp)} {shlex.quote(backend_helper_tmp)} {shlex.quote(sudoers_tmp)}"
        require_ok(run_remote(client, cleanup), cleanup)
    finally:
        client.close()

    verify_native_auth(context)
    verify_helpers(context)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair or resync remote helper and sudoers baseline for backend/admin release.")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR, help="operator name for audit display")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="bootstrap password; prefer KAIPAI_RELEASE_PASSWORD to avoid shell history exposure",
    )
    parser.add_argument(
        "--identity-file",
        default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)),
        help="OpenSSH private key path used for native ssh release",
    )
    parser.add_argument(
        "--known-hosts-file",
        default=os.getenv("KAIPAI_RELEASE_KNOWN_HOSTS_FILE", str(DEFAULT_KNOWN_HOSTS_FILE)),
        help="pinned OpenSSH known_hosts file; unknown host keys are rejected",
    )
    return parser.parse_args(argv)


def build_context(args: argparse.Namespace) -> HelperSyncContext:
    missing = []
    if not str(args.host).strip():
        missing.append("KAIPAI_RELEASE_HOST/--host")
    if not str(args.user).strip():
        missing.append("KAIPAI_RELEASE_USER/--user")
    if not args.password:
        missing.append("KAIPAI_RELEASE_PASSWORD/--password")
    if missing:
        raise RuntimeError(f"missing required helper sync input: {', '.join(missing)}")

    known_hosts_file = Path(args.known_hosts_file).expanduser()
    if not known_hosts_file.is_file():
        raise RuntimeError(
            f"known_hosts file not found: {known_hosts_file}; pin and verify the remote host key before helper sync"
        )

    return HelperSyncContext(
        host=str(args.host).strip(),
        user=str(args.user).strip(),
        password=args.password,
        operator=args.operator,
        identity_file=Path(args.identity_file).expanduser(),
        known_hosts_file=known_hosts_file,
    )


def main() -> int:
    args = parse_args()
    context = build_context(args)
    ensure_keypair(context.identity_file)
    sync_helper_baseline(context)
    print(
        f"helper baseline synced for {context.user}@{context.host} "
        f"with key {context.identity_file}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
