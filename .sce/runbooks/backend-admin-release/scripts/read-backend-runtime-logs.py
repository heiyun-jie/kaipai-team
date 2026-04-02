import argparse
import json
import os
import shutil
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_DIR = ROOT / ".sce" / "runbooks" / "backend-admin-release"
DIAGNOSTICS_DIR = RUNBOOK_DIR / "records" / "diagnostics"

DEFAULT_HOST = "101.43.57.62"
DEFAULT_USER = "kaipaile"
DEFAULT_IDENTITY_FILE = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".ssh" / "kaipai_release_ed25519"
DEFAULT_CONTAINER = "kaipai-backend"
DEFAULT_SINCE = "15m"
DEFAULT_TAIL = 400
REMOTE_HELPER_PATH = "/usr/local/bin/kaipai-backend-release-helper.sh"


@dataclass
class DiagnosticContext:
    capture_id: str
    host: str
    user: str
    identity_file: Path
    container: str
    since: str
    tail: int
    grep: str | None
    output_dir: Path


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


def ssh_base(context: DiagnosticContext) -> list[str]:
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


def run_ssh(context: DiagnosticContext, remote_command: str) -> subprocess.CompletedProcess[str]:
    return run_process(ssh_base(context) + [remote_command], capture_output=True)


def require_key_auth(context: DiagnosticContext) -> None:
    result = run_ssh(context, "printf 'key-auth-ok'")
    if result.stdout.strip() != "key-auth-ok":
        raise RuntimeError("ssh key auth probe returned unexpected output")
    log("native ssh key auth verified")


def require_helper(context: DiagnosticContext) -> None:
    result = run_ssh(context, f"sudo -n {REMOTE_HELPER_PATH} --healthcheck")
    if result.stdout.strip() != "helper-ok":
        raise RuntimeError("backend helper healthcheck returned unexpected output")
    log("remote backend helper and sudoers verified")


def run_remote_bash(context: DiagnosticContext, command: str) -> str:
    result = run_ssh(context, command)
    if result.stderr and result.stderr.strip():
        log(f"remote stderr> {result.stderr.strip()}")
    return result.stdout


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def sanitize_label(label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in label.strip())
    collapsed = "-".join(part for part in normalized.split("-") if part)
    return collapsed or "backend-runtime-diagnostic"


def filter_logs(content: str, grep: str | None) -> str:
    if not grep:
        return ""
    keyword = grep.lower()
    return "\n".join(line for line in content.splitlines() if keyword in line.lower())


def parse_helper_output(output: str) -> dict[str, str]:
    fields = [
        "REMOTE_DATE",
        "DOCKER_PS",
        "DOCKER_INSPECT_ENV",
        "DOCKER_LOGS_TAIL",
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
        section = output[content_start:stop].strip("\r\n")
        summary[field] = section
    return summary


def collect(context: DiagnosticContext) -> None:
    ensure_dir(context.output_dir)
    helper_command = (
        f"sudo -n {REMOTE_HELPER_PATH} "
        f"--runtime-diagnostics "
        f"--container {shlex.quote(context.container)} "
        f"--since {shlex.quote(context.since)} "
        f"--tail {context.tail}"
    )
    try:
        result = run_ssh(context, helper_command)
        helper_stdout = result.stdout
        if result.stderr and result.stderr.strip():
            log(f"remote stderr> {result.stderr.strip()}")
    except subprocess.CalledProcessError as exc:
        helper_stdout = exc.stdout or ""
        helper_stderr = exc.stderr or ""
        if helper_stderr.strip():
            log(f"remote stderr> {helper_stderr.strip()}")
        if "__FINAL_STATUS_BEGIN__" not in helper_stdout:
            raise

    summary = parse_helper_output(helper_stdout)
    if summary["FINAL_STATUS"] != "passed":
        raise RuntimeError(f"runtime diagnostic helper failed: {summary['FAIL_REASON']}")

    remote_date = summary["REMOTE_DATE"]
    docker_ps = summary["DOCKER_PS"]
    inspect_env = summary["DOCKER_INSPECT_ENV"]
    docker_logs = summary["DOCKER_LOGS_TAIL"]
    filtered_logs = filter_logs(docker_logs, context.grep)

    metadata = {
        "captureId": context.capture_id,
        "capturedAt": datetime.now().astimezone().isoformat(),
        "remoteDate": remote_date,
        "host": context.host,
        "user": context.user,
        "container": context.container,
        "since": context.since,
        "tail": context.tail,
        "grep": context.grep,
        "files": {
            "dockerPs": "docker-ps.txt",
            "inspectEnv": "docker-inspect-env.txt",
            "dockerLogs": "docker-logs.txt",
            "filteredLogs": "docker-logs.filtered.txt" if context.grep else None,
        },
    }

    write_text(context.output_dir / "docker-ps.txt", docker_ps)
    write_text(context.output_dir / "docker-inspect-env.txt", inspect_env)
    write_text(context.output_dir / "docker-logs.txt", docker_logs)
    if context.grep:
        write_text(context.output_dir / "docker-logs.filtered.txt", filtered_logs)
    write_text(context.output_dir / "summary.json", json.dumps(metadata, ensure_ascii=False, indent=2))

    log(f"diagnostic capture saved: {context.output_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read backend runtime status and logs from the standard remote environment.",
    )
    parser.add_argument("--label", default="backend-runtime-diagnostic")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--container", default=DEFAULT_CONTAINER)
    parser.add_argument("--since", default=DEFAULT_SINCE)
    parser.add_argument("--tail", type=int, default=DEFAULT_TAIL)
    parser.add_argument("--grep")
    args = parser.parse_args()

    capture_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{sanitize_label(args.label)}"
    output_dir = DIAGNOSTICS_DIR / capture_id
    context = DiagnosticContext(
        capture_id=capture_id,
        host=args.host,
        user=args.user,
        identity_file=Path(args.identity_file),
        container=args.container,
        since=args.since,
        tail=args.tail,
        grep=args.grep,
        output_dir=output_dir,
    )

    require_key_auth(context)
    require_helper(context)
    collect(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
