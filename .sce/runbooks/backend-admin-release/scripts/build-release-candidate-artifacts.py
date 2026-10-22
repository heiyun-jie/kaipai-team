import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
GENERATOR_PATH = SCRIPT_DIR / "generate-release-candidate-manifest.py"
BUILD_ROOT_RELATIVE_DIR = Path("tmp/release-candidate-builds")
REPOSITORY_PATHS = {
    "backend": Path("kaipaile-server"),
    "admin": Path("kaipai-admin"),
    "frontend": Path("kaipai-frontend"),
}
RUNTIME_SUFFIXES = {".js", ".json", ".wxml", ".wxss", ".wxs"}
LOCAL_BASE_URLS = (
    "http://127.0.0.1",
    "http://localhost",
    "http://[::1]",
)
REPRODUCIBLE_OUTPUT_TIMESTAMP = "2000-01-01T00:00:00Z"
SOURCE_DATE_EPOCH = "946684800"
MIN_SAFE_VUE_I18N_VERSION = (9, 14, 5)
MINI_PROGRAM_BUILD_ONLY_ADVISORY_PACKAGES = {
    "@vue/server-renderer",
    "baseline-browser-mapping",
    "braces",
    "source-map-js",
    "@babel/core",
    "@intlify/core-base",
    "@intlify/message-resolver",
    "adm-zip",
    "brace-expansion",
    "browserslist",
    "esbuild",
    "follow-redirects",
    "immutable",
    "jpeg-js",
    "nanoid",
    "phin",
    "picomatch",
    "postcss",
    "postcss-selector-parser",
    "vite",
    "ws",
    "yaml",
}
MINI_PROGRAM_FORBIDDEN_TOOLCHAIN_MARKERS = (
    b"ssrRenderAttrs",
    b"renderToString",
    b"SourceMapConsumer",
    b"baseline-browser-mapping",
    b"braces/lib/parse",
    b"@dcloudio/uni-cli-shared",
    b"adm-zip",
    b"follow-redirects",
    b"jpeg-js",
    b"launch-editor",
    b"picomatch",
    b"postcss-load-config",
)
MINI_PROGRAM_BUILD_RISK_EXPIRY = "2026-11-05T23:59:59+08:00"
MINI_PROGRAM_ADVISORY_REVIEW_PATH = SCRIPT_DIR / "miniprogram-reviewed-build-advisories.json"
TEST_PROJECT_PRIVATE_CONFIG = {"setting": {"urlCheck": False}}


def load_generator_module():
    spec = importlib.util.spec_from_file_location("release_candidate_manifest", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator_module()


def log(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"[{timestamp}] {message}", flush=True)


def resolve_executable(name: str) -> str:
    candidates = [f"{name}.cmd", f"{name}.exe", name] if os.name == "nt" else [name]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError(f"required executable not found: {name}")


def run_process(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    log(f"local build> {' '.join(command)}")
    subprocess.run(command, cwd=cwd, env=env, check=True)


def summarize_npm_audit(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata") if isinstance(payload, dict) else None
    vulnerabilities = metadata.get("vulnerabilities") if isinstance(metadata, dict) else None
    if (not isinstance(payload, dict) or "error" in payload or not isinstance(vulnerabilities, dict)
        or not isinstance(payload.get("vulnerabilities"), dict)
        or any(type(vulnerabilities.get(key)) is not int or vulnerabilities[key] < 0 for key in ("high", "critical"))):
        raise RuntimeError("npm audit returned an error or invalid audit schema")
    counts = {
        severity: int(vulnerabilities.get(severity, 0) or 0)
        for severity in ("info", "low", "moderate", "high", "critical", "total")
    }
    direct_findings = []
    advisory_packages: set[str] = set()
    advisory_keys: set[str] = set()
    for name, finding in sorted(payload.get("vulnerabilities", {}).items()):
        if not isinstance(finding, dict):
            continue
        for advisory in finding.get("via", []):
            if isinstance(advisory, dict) and advisory.get("name"):
                advisory_packages.add(str(advisory["name"]))
                advisory_keys.add(f"{advisory['name']}|{advisory.get('url', '[missing-url]')}")
        if finding.get("isDirect"):
            direct_findings.append(
                {
                    "name": name,
                    "severity": finding.get("severity", "unknown"),
                    "fixAvailable": bool(finding.get("fixAvailable")),
                }
            )
    return {
        "counts": counts,
        "directFindings": direct_findings,
        "vulnerablePackages": sorted(payload.get("vulnerabilities", {}).keys()),
        "advisoryPackages": sorted(advisory_packages),
        "advisoryKeys": sorted(advisory_keys),
        "gate": "PASSED" if counts["high"] == 0 and counts["critical"] == 0 else "REVIEW_REQUIRED",
    }


def parse_numeric_version(version: str) -> tuple[int, ...]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        return ()
    return tuple(int(part) for part in match.groups())


def lock_package_version(lock_payload: dict[str, Any], package_path: str) -> str | None:
    package = lock_payload.get("packages", {}).get(package_path, {})
    version = package.get("version") if isinstance(package, dict) else None
    return str(version) if version else None


def classify_miniprogram_dependency_audit(
    audit: dict[str, Any],
    snapshot: Path,
    artifact_directory: Path,
) -> dict[str, Any]:
    review = json.loads(MINI_PROGRAM_ADVISORY_REVIEW_PATH.read_text(encoding="utf-8"))
    reviewed_keys = set(review["advisories"])
    unknown_advisories = sorted(set(audit.get("advisoryKeys", [])) - reviewed_keys)
    advisory_identity_complete = isinstance(audit.get("advisoryKeys"), list) and (
        not audit.get("advisoryPackages") or bool(audit["advisoryKeys"])) and (
        not audit.get("counts", {}).get("high", 0) or bool(audit.get("advisoryPackages")))
    try:
        expiries = [datetime.fromisoformat(value) for value in (MINI_PROGRAM_BUILD_RISK_EXPIRY, review["expiresAt"])]
        review_current = all(value.tzinfo is not None and datetime.now(timezone.utc) < value for value in expiries)
    except (ValueError, TypeError):
        review_current = False
    lock_payload = json.loads((snapshot / "package-lock.json").read_text(encoding="utf-8"))
    reviewed_lock_current = GENERATOR.sha256_file(snapshot / "package-lock.json") == review.get("frontendLockfileSha256")
    runtime_vue_i18n = lock_package_version(lock_payload, "node_modules/vue-i18n")
    runtime_core_base = lock_package_version(
        lock_payload,
        "node_modules/vue-i18n/node_modules/@intlify/core-base",
    )
    build_core_base = lock_package_version(lock_payload, "node_modules/@intlify/core-base")
    runtime_i18n_safe = bool(
        runtime_vue_i18n
        and runtime_core_base
        and parse_numeric_version(runtime_vue_i18n) >= MIN_SAFE_VUE_I18N_VERSION
        and parse_numeric_version(runtime_core_base) >= MIN_SAFE_VUE_I18N_VERSION
    )

    advisory_packages = set(audit.get("advisoryPackages", []))
    unreviewed_advisory_packages = sorted(
        advisory_packages - MINI_PROGRAM_BUILD_ONLY_ADVISORY_PACKAGES
    )
    artifact_files = sorted(
        (path for path in artifact_directory.rglob("*") if path.is_file()),
        key=lambda path: path.as_posix(),
    )
    source_map_files = [
        path.relative_to(artifact_directory).as_posix()
        for path in artifact_files
        if path.suffix.lower() == ".map"
    ]
    package_manifest_files = [
        path.relative_to(artifact_directory).as_posix()
        for path in artifact_files
        if path.name in {"package.json", "package-lock.json", "pnpm-lock.yaml"}
        or "node_modules" in path.parts
    ]
    marker_matches: list[dict[str, str]] = []
    for path in artifact_files:
        if path.suffix.lower() not in RUNTIME_SUFFIXES:
            continue
        content = path.read_bytes()
        for marker in MINI_PROGRAM_FORBIDDEN_TOOLCHAIN_MARKERS:
            if marker in content:
                marker_matches.append(
                    {
                        "marker": marker.decode("ascii"),
                        "path": path.relative_to(artifact_directory).as_posix(),
                    }
                )

    proof = {
        "runtimeVueI18nVersion": runtime_vue_i18n,
        "runtimeIntlifyCoreBaseVersion": runtime_core_base,
        "buildToolchainIntlifyCoreBaseVersion": build_core_base,
        "runtimeI18nSafe": runtime_i18n_safe,
        "sourceMapFiles": source_map_files,
        "packageManifestFiles": package_manifest_files,
        "forbiddenToolchainMarkerMatches": marker_matches,
        "artifactFileCount": len(artifact_files),
    }
    passed = bool(
        audit.get("counts", {}).get("critical", 0) == 0
        and review_current
        and reviewed_lock_current
        and advisory_identity_complete
        and not unknown_advisories
        and not unreviewed_advisory_packages
        and runtime_i18n_safe
        and not source_map_files
        and not package_manifest_files
        and not marker_matches
    )
    return {
        **audit,
        "classification": "CONTROLLED_BUILD_TOOLCHAIN_ONLY" if passed else "REVIEW_REQUIRED",
        "unreviewedAdvisoryPackages": unreviewed_advisory_packages,
        "unreviewedAdvisories": unknown_advisories,
        "advisoryIdentityComplete": advisory_identity_complete,
        "reviewCurrent": review_current,
        "reviewedLockCurrent": reviewed_lock_current,
        "reviewPolicySha256": GENERATOR.sha256_file(MINI_PROGRAM_ADVISORY_REVIEW_PATH),
        "artifactReachabilityProof": proof,
        "residualRiskDecision": "RISK_ACCEPTED_WITH_EXPIRY" if passed else "NOT_ACCEPTED",
        "riskExpiry": MINI_PROGRAM_BUILD_RISK_EXPIRY if passed else None,
        "operatingConstraints": [
            "do not expose the Vite development server to untrusted networks",
            "build only repository-controlled source and assets",
            "do not publish node_modules, source maps, or build-tool manifests",
            "repeat this review before the expiry or when dependency inputs change",
        ],
        "gate": "PASSED" if passed else "REVIEW_REQUIRED",
    }


def classify_miniprogram_artifacts(audit: dict[str, Any], snapshot: Path, test_directory: Path, release_directory: Path) -> dict[str, Any]:
    results = {name: classify_miniprogram_dependency_audit(audit, snapshot, directory)
               for name, directory in (("test", test_directory), ("release", release_directory))}
    passed = all(result["gate"] == "PASSED" for result in results.values())
    return {**results["release"], "artifactAuditByEnvironment": results,
            "gate": "PASSED" if passed else "REVIEW_REQUIRED",
            "classification": "CONTROLLED_BUILD_TOOLCHAIN_ONLY" if passed else "REVIEW_REQUIRED",
            "residualRiskDecision": "RISK_ACCEPTED_WITH_EXPIRY" if passed else "NOT_ACCEPTED",
            "riskExpiry": MINI_PROGRAM_BUILD_RISK_EXPIRY if passed else None}


def collect_npm_audit(snapshot: Path) -> dict[str, Any]:
    command = [resolve_executable("npm"), "audit", "--omit=dev", "--json"]
    log(f"local audit> {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=snapshot,
        env=sanitized_build_environment(),
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if not result.stdout.strip():
        raise RuntimeError("npm audit did not return JSON output")
    if result.returncode not in (0, 1):
        raise RuntimeError(f"npm audit command failed with exit code {result.returncode}")
    summary = summarize_npm_audit(json.loads(result.stdout))
    if result.returncode == 1 and not summary["counts"]["total"]:
        raise RuntimeError("npm audit failed without a complete vulnerability report")
    return summary


def assert_descendant(path: Path, allowed_root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = allowed_root.resolve()
    if resolved_path == resolved_root:
        raise RuntimeError(f"refusing to operate on the build root itself: {resolved_path}")
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise RuntimeError(f"path escapes the candidate build root: {resolved_path}") from exc


def remove_build_path(path: Path, allowed_root: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    assert_descendant(path, allowed_root)
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def validate_archive_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        candidate = Path(member.filename)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise RuntimeError(f"unsafe path in git archive: {member.filename}")


def prepare_git_snapshot(
    live_repository: Path,
    snapshot: Path,
    commit: str,
    build_root: Path,
) -> None:
    assert_descendant(snapshot, build_root)
    snapshot.mkdir(parents=True, exist_ok=False)
    archive_path = snapshot.parent / f"{snapshot.name}.zip"
    assert_descendant(archive_path, build_root)
    run_process(
        [
            resolve_executable("git"),
            "-C",
            str(live_repository),
            "archive",
            "--format=zip",
            f"--output={archive_path}",
            commit,
        ],
        cwd=live_repository,
    )
    with zipfile.ZipFile(archive_path) as archive:
        validate_archive_members(archive)
        archive.extractall(snapshot)
    archive_path.unlink()


def resolve_overlay_path(root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise RuntimeError(f"unsafe overlay path: {relative_path}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise RuntimeError(f"overlay path escapes repository: {relative_path}") from exc
    return resolved


def verify_overlay_source(source: Path, overlay: dict[str, Any]) -> None:
    hash_kind = overlay["hashKind"]
    if hash_kind == "file-content":
        if not source.is_file() or GENERATOR.sha256_file(source) != overlay["sha256"]:
            raise RuntimeError(f"overlay file changed after candidate capture: {overlay['path']}")
    elif hash_kind == "symlink-target":
        if not source.is_symlink():
            raise RuntimeError(f"overlay symlink changed after candidate capture: {overlay['path']}")
        target_hash = GENERATOR.sha256_bytes(source.readlink().as_posix().encode("utf-8"))
        if target_hash != overlay["sha256"]:
            raise RuntimeError(f"overlay symlink target changed after candidate capture: {overlay['path']}")
    else:
        tombstone = f"DELETE\0{overlay['path']}".encode("utf-8")
        if overlay["state"] != "deleted" or GENERATOR.sha256_bytes(tombstone) != overlay["sha256"]:
            raise RuntimeError(f"overlay deletion marker is invalid: {overlay['path']}")


def apply_manifest_overlays(
    repository_name: str,
    live_repository: Path,
    snapshot: Path,
    overlays: list[dict[str, Any]],
    build_root: Path,
) -> None:
    for overlay in (item for item in overlays if item["repository"] == repository_name):
        target = resolve_overlay_path(snapshot, overlay["path"])
        original_path = overlay.get("originalPath")
        if original_path:
            original_target = resolve_overlay_path(snapshot, original_path)
            remove_build_path(original_target, build_root)

        source = resolve_overlay_path(live_repository, overlay["path"])
        verify_overlay_source(source, overlay)
        if overlay["state"] == "deleted":
            remove_build_path(target, build_root)
            continue
        if overlay["hashKind"] == "symlink-target":
            raise RuntimeError("candidate snapshots do not support symlink overlays on Windows")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if GENERATOR.sha256_file(target) != overlay["sha256"]:
            raise RuntimeError(f"overlay copy hash mismatch: {repository_name}/{overlay['path']}")


def sanitized_build_environment(api_base_url: str | None = None) -> dict[str, str]:
    blocked_fragments = ("PASSWORD", "SECRET", "TOKEN", "CREDENTIAL", "PRIVATE_KEY", "ACCESS_KEY")
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith("VITE_")
        and not any(fragment in key.upper() for fragment in blocked_fragments)
    }
    environment["CI"] = "true"
    environment["NO_COLOR"] = "1"
    environment["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    if api_base_url:
        environment["VITE_API_BASE_URL"] = api_base_url
    return environment


def record_directory_artifact(
    name: str,
    relative_path: str,
    directory: Path,
    evidence_directory: Path,
) -> dict[str, Any]:
    tree = GENERATOR.hash_artifact_directory(directory)
    file_manifest_directory = evidence_directory / "artifact-file-manifests"
    file_manifest_directory.mkdir(parents=True, exist_ok=True)
    file_manifest_path = file_manifest_directory / f"{name}.json"
    file_manifest_path.write_text(
        json.dumps(tree["files"], ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "name": name,
        "type": "directory",
        "relativePath": relative_path,
        "fileCount": tree["fileCount"],
        "totalSize": tree["totalSize"],
        "treeSha256": tree["treeSha256"],
        "fileManifestPath": file_manifest_path.relative_to(evidence_directory).as_posix(),
        "fileManifestSha256": GENERATOR.sha256_file(file_manifest_path),
    }


def scan_api_target(
    artifact_directory: Path,
    expected_base_url: str,
    forbidden_base_urls: tuple[str, ...],
) -> dict[str, Any]:
    expected = expected_base_url.encode("utf-8")
    matched_files: list[str] = []
    forbidden_matches: list[dict[str, Any]] = []
    runtime_files = sorted(
        (path for path in artifact_directory.rglob("*") if path.is_file() and path.suffix.lower() in RUNTIME_SUFFIXES),
        key=lambda path: path.as_posix(),
    )
    for path in runtime_files:
        content = path.read_bytes()
        relative_path = path.relative_to(artifact_directory).as_posix()
        if expected in content:
            matched_files.append(relative_path)
    for forbidden_base_url in forbidden_base_urls:
        encoded = forbidden_base_url.encode("utf-8")
        files = [
            path.relative_to(artifact_directory).as_posix()
            for path in runtime_files
            if encoded in path.read_bytes()
        ]
        if files:
            forbidden_matches.append({"baseUrl": forbidden_base_url, "files": files})
    return {
        "expectedBaseUrl": expected_base_url,
        "matchedFiles": matched_files,
        "forbiddenMatches": forbidden_matches,
        "runtimeFileCount": len(runtime_files),
        "passed": bool(matched_files) and not forbidden_matches,
    }


def copy_artifact_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        raise RuntimeError(f"artifact destination already exists: {destination}")
    shutil.copytree(source, destination)


def build_backend(snapshot: Path, artifact_directory: Path) -> dict[str, Any]:
    run_process(
        [
            resolve_executable("mvn"),
            "-DskipTests",
            f"-Dproject.build.outputTimestamp={REPRODUCIBLE_OUTPUT_TIMESTAMP}",
            "clean",
            "package",
        ],
        cwd=snapshot,
        env=sanitized_build_environment(),
    )
    source = snapshot / "target" / "kaipai-backend-1.0.0-SNAPSHOT.jar"
    if not source.is_file():
        raise RuntimeError("backend build did not produce the expected JAR")
    destination_directory = artifact_directory / "backend"
    destination_directory.mkdir(parents=True, exist_ok=False)
    destination = destination_directory / source.name
    shutil.copy2(source, destination)
    return {
        "name": "backend-jar",
        "type": "file",
        "relativePath": destination.relative_to(artifact_directory.parent).as_posix(),
        "size": destination.stat().st_size,
        "sha256": GENERATOR.sha256_file(destination),
    }


def build_admin(
    snapshot: Path,
    artifact_directory: Path,
    evidence_directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    npm = resolve_executable("npm")
    environment = sanitized_build_environment()
    run_process([npm, "ci"], cwd=snapshot, env=environment)
    audit = collect_npm_audit(snapshot)
    run_process([npm, "run", "build"], cwd=snapshot, env=environment)
    source = snapshot / "dist"
    if not source.is_dir():
        raise RuntimeError("admin build did not produce dist")
    destination = artifact_directory / "admin"
    copy_artifact_directory(source, destination)
    return (
        record_directory_artifact(
            "admin-dist",
            destination.relative_to(evidence_directory).as_posix(),
            destination,
            evidence_directory,
        ),
        audit,
    )


def run_frontend_build(snapshot: Path, api_base_url: str, build_root: Path) -> Path:
    output_parent = snapshot / "dist" / "build"
    remove_build_path(output_parent, build_root)
    output = output_parent / "mp-weixin"
    uni = snapshot / "node_modules" / ".bin" / ("uni.cmd" if os.name == "nt" else "uni")
    if not uni.is_file():
        raise RuntimeError("uni executable is missing after npm ci")
    environment = sanitized_build_environment(api_base_url)
    # Candidate/release builds run in an isolated snapshot. They must never
    # inherit the workspace test runtime output or depend on its postbuild hook.
    environment["UNI_OUTPUT_DIR"] = str(output.resolve())
    run_process([str(uni), "build", "-p", "mp-weixin"], cwd=snapshot, env=environment)
    run_process(
        [
            resolve_executable("powershell"),
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/sync-mp-weixin.ps1",
            "-ArtifactOnly",
        ],
        cwd=snapshot,
        env=environment,
    )
    if not output.is_dir():
        raise RuntimeError("mini-program build did not produce dist/build/mp-weixin")
    return output


def write_test_project_private_config(output: Path) -> Path:
    private_config = output / "project.private.config.json"
    content = json.dumps(TEST_PROJECT_PRIVATE_CONFIG, ensure_ascii=True, indent=2) + "\n"
    private_config.write_bytes(content.encode("utf-8"))
    return private_config


def build_frontend(
    snapshot: Path,
    artifact_directory: Path,
    evidence_directory: Path,
    build_root: Path,
    test_api_base_url: str,
    release_api_base_url: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    npm = resolve_executable("npm")
    environment = sanitized_build_environment()
    run_process([npm, "ci"], cwd=snapshot, env=environment)
    audit = collect_npm_audit(snapshot)
    run_process([npm, "run", "prepare:tdesign"], cwd=snapshot, env=environment)

    test_output = run_frontend_build(snapshot, test_api_base_url, build_root)
    write_test_project_private_config(test_output)
    test_destination = artifact_directory / "mini-program-test"
    copy_artifact_directory(test_output, test_destination)
    test_proof = scan_api_target(
        test_destination,
        test_api_base_url,
        (release_api_base_url, *LOCAL_BASE_URLS),
    )
    if not test_proof["passed"]:
        raise RuntimeError(f"test mini-program API target proof failed: {test_proof}")

    release_output = run_frontend_build(snapshot, release_api_base_url, build_root)
    release_destination = artifact_directory / "mini-program-release"
    copy_artifact_directory(release_output, release_destination)
    release_proof = scan_api_target(
        release_destination,
        release_api_base_url,
        (test_api_base_url, *LOCAL_BASE_URLS),
    )
    if not release_proof["passed"]:
        raise RuntimeError(f"release mini-program API target proof failed: {release_proof}")

    audit = classify_miniprogram_artifacts(audit, snapshot, test_destination, release_destination)

    artifacts = [
        record_directory_artifact(
            "mini-program-test",
            test_destination.relative_to(evidence_directory).as_posix(),
            test_destination,
            evidence_directory,
        ),
        record_directory_artifact(
            "mini-program-release",
            release_destination.relative_to(evidence_directory).as_posix(),
            release_destination,
            evidence_directory,
        ),
    ]
    return artifacts, {"test": test_proof, "release": release_proof}, audit


def prepare_snapshots(
    repository_root: Path,
    manifest: dict[str, Any],
    build_root: Path,
) -> dict[str, Path]:
    if build_root.exists():
        raise RuntimeError(f"candidate build root already exists: {build_root}")
    build_root.mkdir(parents=True, exist_ok=False)
    repositories = {item["name"]: item for item in manifest["repositories"]}
    snapshots: dict[str, Path] = {}
    for repository_name, relative_path in REPOSITORY_PATHS.items():
        live_repository = repository_root / relative_path
        snapshot = build_root / repository_name
        prepare_git_snapshot(
            live_repository,
            snapshot,
            repositories[repository_name]["commit"],
            build_root,
        )
        apply_manifest_overlays(
            repository_name,
            live_repository,
            snapshot,
            manifest["overlays"],
            build_root,
        )
        snapshots[repository_name] = snapshot
    return snapshots


def build_candidate_artifacts(repository_root: Path, manifest_path: Path, build_root: Path) -> Path:
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verification = GENERATOR.verify_manifest(manifest_path, repository_root)
    if not verification["current"]:
        raise RuntimeError("candidate manifest is INVALIDATED; generate a new candidate before building")

    evidence_directory = manifest_path.parent
    evidence_path = evidence_directory / "artifact-evidence.json"
    artifact_directory = evidence_directory / "artifacts"
    if evidence_path.exists() or artifact_directory.exists():
        raise RuntimeError("artifact evidence already exists for this candidate")

    snapshots = prepare_snapshots(repository_root, manifest, build_root)
    artifact_directory.mkdir(parents=True, exist_ok=False)
    artifacts = [build_backend(snapshots["backend"], artifact_directory)]
    admin_artifact, admin_audit = build_admin(
        snapshots["admin"], artifact_directory, evidence_directory
    )
    artifacts.append(admin_artifact)
    frontend_artifacts, api_target_proof, frontend_audit = build_frontend(
        snapshots["frontend"],
        artifact_directory,
        evidence_directory,
        build_root,
        manifest["testApiBaseUrl"],
        manifest["releaseApiBaseUrl"],
    )
    artifacts.extend(frontend_artifacts)
    evidence = {
        "schemaVersion": 1,
        "candidateId": manifest["candidateId"],
        "candidateInputSha256": manifest["candidateInputSha256"],
        "sourceManifestSha256": GENERATOR.sha256_file(manifest_path),
        "builtAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sourcePolicy": "git-commit-plus-explicit-manifest-overlays",
        "desktopInterference": False,
        "artifacts": artifacts,
        "apiTargetProof": api_target_proof,
        "dependencyAudit": {
            "admin": admin_audit,
            "miniProgram": frontend_audit,
            "gate": "PASSED"
            if admin_audit["gate"] == "PASSED" and frontend_audit["gate"] == "PASSED"
            else "REVIEW_REQUIRED",
        },
        "status": "PASSED",
    }
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    checksum = GENERATOR.sha256_file(evidence_path)
    (evidence_directory / "artifact-evidence.sha256").write_text(
        f"{checksum}  artifact-evidence.json\n",
        encoding="ascii",
    )
    return evidence_path


def default_repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build KaiPai candidate artifacts from commit + manifest overlays.")
    parser.add_argument("--repository-root", type=Path, default=default_repository_root())
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--build-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repository_root = args.repository_root.resolve()
    manifest = json.loads(args.manifest.resolve().read_text(encoding="utf-8"))
    build_root = args.build_root or (
        repository_root / BUILD_ROOT_RELATIVE_DIR / manifest["candidateId"]
    )
    evidence_path = build_candidate_artifacts(repository_root, args.manifest, build_root.resolve())
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "candidateId": evidence["candidateId"],
                "status": evidence["status"],
                "artifactCount": len(evidence["artifacts"]),
                "apiTargetProof": {
                    key: value["passed"] for key, value in evidence["apiTargetProof"].items()
                },
                "evidencePath": str(evidence_path),
                "evidenceSha256": GENERATOR.sha256_file(evidence_path),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
