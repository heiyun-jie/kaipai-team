import argparse
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"
SYNC_ARTIFACTS_PATH = ROOT / ".sce" / "specs" / "00-28-architecture-driven-delivery-governance" / "execution" / "verify" / "sync-verify-validation-artifacts.py"


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


def sync_artifacts(sample_dir: Path) -> None:
    python = resolve_executable("python")
    run_process([python, str(SYNC_ARTIFACTS_PATH), "--sample-dir", str(sample_dir)])


def ssh_base(host: str, user: str, identity_file: Path) -> list[str]:
    ssh = resolve_executable("ssh")
    return [
        ssh,
        "-i",
        str(identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{user}@{host}",
    ]


def scp_base(identity_file: Path) -> list[str]:
    scp = resolve_executable("scp")
    return [
        scp,
        "-i",
        str(identity_file),
        "-o",
        "BatchMode=yes",
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ]


def run_ssh(host: str, user: str, identity_file: Path, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(host, user, identity_file) + [remote_command], capture_output=True)


def require_key_auth(host: str, user: str, identity_file: Path) -> None:
    result = run_ssh(host, user, identity_file, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(host: str, user: str, identity_file: Path) -> None:
    result = run_ssh(host, user, identity_file, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "MYSQL_DATABASE",
        "MYSQL_CONTAINER",
        "MYSQL_RESULT",
        "FINAL_STATUS",
        "FAIL_REASON",
    ]
    summary: dict[str, str] = {}
    for field in fields:
        begin = f"__{field}_BEGIN__"
        end = f"__{field}_END__"
        start = output.find(begin)
        stop = output.find(end)
        if start == -1 or stop == -1 or stop < start:
            raise RuntimeError(f"missing helper output section: {field}")
        content_start = start + len(begin)
        summary[field] = output[content_start:stop].strip("\r\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute verify validation.sql against the standard remote MySQL runtime.")
    parser.add_argument("--sample-dir", required=True)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--database", default="kaipai_dev")
    parser.add_argument("--mysql-container", default="kaipai-mysql")
    args = parser.parse_args()

    sample_dir = Path(args.sample_dir).resolve()
    sql_path = sample_dir / "validation.sql"
    result_path = sample_dir / "validation-result.txt"
    if not sql_path.exists():
        raise RuntimeError(f"validation.sql not found: {sql_path}")

    identity_file = Path(args.identity_file)
    require_key_auth(args.host, args.user, identity_file)
    require_helper(args.host, args.user, identity_file)

    remote_dir = f"/home/{args.user}/spec-validation/{sample_dir.name}"
    remote_sql = f"{remote_dir}/validation.sql"

    run_ssh(args.host, args.user, identity_file, f"mkdir -p {remote_dir}")
    run_process(scp_base(identity_file) + [str(sql_path), f"{args.user}@{args.host}:{remote_sql}"])

    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--mysql-validation "
        f"--mysql-script-path {remote_sql} "
        f"--mysql-database {args.database} "
        f"--mysql-container {args.mysql_container}"
    )
    result = run_ssh(args.host, args.user, identity_file, helper_command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    summary = parse_helper_output(result.stdout)
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"mysql validation helper failed: {summary['FAIL_REASON']}")

    result_path.write_text(summary["MYSQL_RESULT"] + "\n", encoding="utf-8")
    log(f"validation result saved: {result_path}")
    sync_artifacts(sample_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
