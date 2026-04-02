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

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_PASSWORD = "kaipaile888"
DEFAULT_OPERATOR = "codex"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-admin-release-helper.sh"
REMOTE_SUDOERS_PATH = "/etc/sudoers.d/kaipai-admin-release"
REMOTE_BARE_REPO_PATH = f"/home/{DEFAULT_USER}/kaipai-admin-release.git"


@dataclass
class BootstrapContext:
    host: str
    user: str
    password: str
    operator: str
    identity_file: Path


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
    if identity_file.exists() and identity_file.with_suffix(identity_file.suffix + ".pub").exists():
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


def ssh_base(context: BootstrapContext) -> list[str]:
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


def verify_native_auth(context: BootstrapContext) -> None:
    result = run_process(ssh_base(context) + ["printf 'bootstrap-ok'"], capture_output=True)
    if result.stdout.strip() != "bootstrap-ok":
        raise RuntimeError("native ssh key verification returned unexpected output")
    log("native ssh key auth verified")


def verify_helper(context: BootstrapContext) -> None:
    result = run_process(
        ssh_base(context)
        + [f"sudo -n {shlex.quote(REMOTE_HELPER_PATH)} --healthcheck"],
        capture_output=True,
    )
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("remote helper healthcheck returned unexpected output")
    log("remote helper and sudoers verified")


def verify_bare_repo(context: BootstrapContext) -> None:
    result = run_process(
        ssh_base(context)
        + [f"test -d {shlex.quote(REMOTE_BARE_REPO_PATH)} && test -f {shlex.quote(REMOTE_BARE_REPO_PATH + '/HEAD')} && printf 'bare-ok'"],
        capture_output=True,
    )
    if result.stdout.strip() != "bare-ok":
        raise RuntimeError("remote bare repo verification returned unexpected output")
    log("remote bare repo verified")


def bootstrap(context: BootstrapContext) -> None:
    helper_script = (SCRIPTS_DIR / "kaipai-admin-release-helper.sh").read_text(encoding="utf-8")
    sudoers_content = f"{context.user} ALL=(root) NOPASSWD: {REMOTE_HELPER_PATH}\n"
    public_key = context.identity_file.with_suffix(context.identity_file.suffix + ".pub").read_text(encoding="utf-8").strip()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    log(f"connect bootstrap ssh {context.user}@{context.host}")
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

        helper_tmp = f"/home/{context.user}/kaipai-admin-release-helper.sh.tmp"
        sudoers_tmp = f"/home/{context.user}/kaipai-admin-release.sudoers.tmp"
        sftp = client.open_sftp()
        try:
            with sftp.open(helper_tmp, "w") as remote_helper:
                remote_helper.write(helper_script)
            with sftp.open(sudoers_tmp, "w") as remote_sudoers:
                remote_sudoers.write(sudoers_content)
        finally:
            sftp.close()

        install_helper = f"install -o root -g root -m 0755 {shlex.quote(helper_tmp)} {shlex.quote(REMOTE_HELPER_PATH)}"
        require_ok(run_remote(client, install_helper, password=context.password, use_sudo=True), install_helper)

        install_sudoers = f"install -o root -g root -m 0440 {shlex.quote(sudoers_tmp)} {shlex.quote(REMOTE_SUDOERS_PATH)}"
        require_ok(run_remote(client, install_sudoers, password=context.password, use_sudo=True), install_sudoers)

        visudo_check = f"visudo -cf {shlex.quote(REMOTE_SUDOERS_PATH)}"
        require_ok(run_remote(client, visudo_check, password=context.password, use_sudo=True), visudo_check)

        ensure_git_repo = (
            "sh -lc "
            + repr(
                f"test -d {REMOTE_BARE_REPO_PATH} || git init --bare {REMOTE_BARE_REPO_PATH}; "
                f"chown -R {context.user}:{context.user} {REMOTE_BARE_REPO_PATH}"
            )
        )
        require_ok(run_remote(client, ensure_git_repo, password=context.password, use_sudo=True), ensure_git_repo)

        cleanup = f"rm -f {shlex.quote(helper_tmp)} {shlex.quote(sudoers_tmp)}"
        require_ok(run_remote(client, cleanup), cleanup)
    finally:
        client.close()

    verify_native_auth(context)
    verify_helper(context)
    verify_bare_repo(context)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap native ssh/git prerequisites for admin release.")
    parser.add_argument("--operator", default=DEFAULT_OPERATOR, help="operator name for audit display")
    parser.add_argument("--host", default=os.getenv("KAIPAI_RELEASE_HOST", DEFAULT_HOST))
    parser.add_argument("--user", default=os.getenv("KAIPAI_RELEASE_USER", DEFAULT_USER))
    parser.add_argument("--password", default=os.getenv("KAIPAI_RELEASE_PASSWORD", DEFAULT_PASSWORD))
    parser.add_argument(
        "--identity-file",
        default=os.getenv("KAIPAI_RELEASE_IDENTITY_FILE", str(DEFAULT_IDENTITY_FILE)),
        help="OpenSSH private key path used for native ssh/git release",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = BootstrapContext(
        host=args.host,
        user=args.user,
        password=args.password,
        operator=args.operator,
        identity_file=Path(args.identity_file),
    )
    ensure_keypair(context.identity_file)
    bootstrap(context)
    print(
        f"bootstrap completed for {context.user}@{context.host} "
        f"with key {context.identity_file}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
