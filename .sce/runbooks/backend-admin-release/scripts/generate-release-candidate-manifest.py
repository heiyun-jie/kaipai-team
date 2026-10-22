import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


REPOSITORIES = (
    ("root", Path(".")),
    ("backend", Path("kaipaile-server")),
    ("admin", Path("kaipai-admin")),
    ("frontend", Path("kaipai-frontend")),
)

MIGRATION_FILES = (
    "V20260723_001__career_profile_domain_foundation.sql",
    "V20260723_002__actor_media_asset_relations.sql",
    "V20260723_003__share_card_favorite.sql",
    "V20260723_004__ai_profile_import_governance.sql",
    "V20260723_005__ai_profile_import_permission_alignment.sql",
    "V20260724_001__ai_profile_import_request_scene.sql",
    "V20260726_001__ai_profile_import_prompt_template_governance.sql",
    "V20260726_002__ai_profile_import_prompt_permission_alignment.sql",
    "V20260731_001__actor_card_tables.sql",
    "V20260731_002__actor_card_background_seed.sql",
    "V20260810_001__actor_card_attachment_asset_binding.sql",
    "V20260814_001__actor_card_background_style_cleanup.sql",
    "V20260814_002__actor_card_background_provision.sql",
    "V20260818_001__actor_card_media_binding.sql",
)

MIGRATION_RELATIVE_DIR = Path("src/main/resources/db/migration")
DEFAULT_TEST_API_BASE_URL = "https://test-api.kplyyk.com"
DEFAULT_RELEASE_API_BASE_URL = "https://api.kplyyk.com"
RECORDS_RELATIVE_DIR = Path(".sce/runbooks/backend-admin-release/records")


def run_git(repository: Path, arguments: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=check,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_artifact_directory(path: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for source in sorted((item for item in path.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        relative_path = source.relative_to(path).as_posix()
        files.append(
            {
                "path": relative_path,
                "size": source.stat().st_size,
                "sha256": sha256_file(source),
            }
        )
    encoded = json.dumps(files, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "fileCount": len(files),
        "totalSize": sum(item["size"] for item in files),
        "treeSha256": sha256_bytes(encoded),
        "files": files,
    }


def resolve_record_artifact(evidence_path: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise RuntimeError(f"artifact path must stay relative to the evidence directory: {relative_path}")
    resolved = (evidence_path.parent / candidate).resolve()
    try:
        resolved.relative_to(evidence_path.parent.resolve())
    except ValueError as exc:
        raise RuntimeError(f"artifact path escapes the evidence directory: {relative_path}") from exc
    return resolved


def validate_artifact_evidence(
    evidence_path: Path,
    *,
    candidate_id: str,
    candidate_input_sha256_value: str,
    test_api_base_url: str,
    release_api_base_url: str,
) -> dict[str, Any]:
    evidence_path = evidence_path.resolve()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("candidateId") != candidate_id:
        raise RuntimeError("artifact evidence candidateId does not match the manifest")
    if evidence.get("candidateInputSha256") != candidate_input_sha256_value:
        raise RuntimeError("artifact evidence was built from a different candidate input")
    if evidence.get("status") != "PASSED":
        raise RuntimeError("artifact evidence status must be PASSED")

    required_artifacts = {
        "backend-jar": "file",
        "admin-dist": "directory",
        "mini-program-test": "directory",
        "mini-program-release": "directory",
    }
    artifacts = evidence.get("artifacts")
    if not isinstance(artifacts, list):
        raise RuntimeError("artifact evidence artifacts must be a list")
    by_name = {item.get("name"): item for item in artifacts if isinstance(item, dict)}
    if set(by_name) != set(required_artifacts):
        raise RuntimeError("artifact evidence must contain exactly the four required artifacts")

    validated_artifacts: list[dict[str, Any]] = []
    for artifact_name, artifact_type in required_artifacts.items():
        artifact = by_name[artifact_name]
        if artifact.get("type") != artifact_type:
            raise RuntimeError(f"artifact type mismatch: {artifact_name}")
        relative_path = artifact.get("relativePath")
        if not isinstance(relative_path, str):
            raise RuntimeError(f"artifact relativePath is missing: {artifact_name}")
        source = resolve_record_artifact(evidence_path, relative_path)
        if artifact_type == "file":
            if not source.is_file():
                raise RuntimeError(f"artifact file is missing: {artifact_name}")
            actual = {"size": source.stat().st_size, "sha256": sha256_file(source)}
            if actual["size"] != artifact.get("size") or actual["sha256"] != artifact.get("sha256"):
                raise RuntimeError(f"artifact file hash mismatch: {artifact_name}")
        else:
            if not source.is_dir():
                raise RuntimeError(f"artifact directory is missing: {artifact_name}")
            actual = hash_artifact_directory(source)
            for field in ("fileCount", "totalSize", "treeSha256"):
                if actual[field] != artifact.get(field):
                    raise RuntimeError(f"artifact directory {field} mismatch: {artifact_name}")
        validated_artifacts.append(artifact)

    api_target_proof = evidence.get("apiTargetProof", {})
    for environment_name, expected_url in (
        ("test", test_api_base_url),
        ("release", release_api_base_url),
    ):
        proof = api_target_proof.get(environment_name, {})
        if proof.get("expectedBaseUrl") != expected_url or proof.get("passed") is not True:
            raise RuntimeError(f"API target proof did not pass: {environment_name}")
        if not proof.get("matchedFiles") or proof.get("forbiddenMatches"):
            raise RuntimeError(f"API target proof is incomplete: {environment_name}")

    dependency_audit = evidence.get("dependencyAudit")
    if not isinstance(dependency_audit, dict) or dependency_audit.get("gate") not in {
        "PASSED",
        "REVIEW_REQUIRED",
    }:
        raise RuntimeError("artifact evidence dependency audit gate is missing")

    if not re.fullmatch(r"[0-9a-f]{64}", sha256_file(evidence_path)):
        raise RuntimeError("failed to hash artifact evidence")
    return {
        "artifacts": validated_artifacts,
        "apiTargetProof": api_target_proof,
        "dependencyAudit": dependency_audit,
        "artifactEvidence": {
            "path": evidence_path.name,
            "sha256": sha256_file(evidence_path),
        },
    }


def parse_porcelain_v1_z(raw_status: str) -> list[dict[str, str | None]]:
    records = raw_status.split("\0")
    changes: list[dict[str, str | None]] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2] != " ":
            raise RuntimeError(f"unsupported git status record: {record!r}")

        status = record[:2]
        path = record[3:]
        original_path = None
        if "R" in status or "C" in status:
            if index >= len(records) or not records[index]:
                raise RuntimeError(f"missing original path for git status record: {record!r}")
            original_path = records[index]
            index += 1

        changes.append(
            {
                "status": status,
                "path": path.replace("\\", "/"),
                "originalPath": original_path.replace("\\", "/") if original_path else None,
            }
        )
    return changes


def hash_overlay(repository_name: str, repository: Path, change: dict[str, str | None]) -> dict[str, Any]:
    relative_path = str(change["path"])
    source = repository / Path(relative_path)
    if source.is_symlink():
        target = source.readlink().as_posix().encode("utf-8")
        size = len(target)
        checksum = sha256_bytes(target)
        hash_kind = "symlink-target"
        state = "present"
    elif source.is_file():
        size = source.stat().st_size
        checksum = sha256_file(source)
        hash_kind = "file-content"
        state = "present"
    else:
        tombstone = f"DELETE\0{relative_path}".encode("utf-8")
        size = 0
        checksum = sha256_bytes(tombstone)
        hash_kind = "deletion-tombstone"
        state = "deleted"

    return {
        "repository": repository_name,
        "path": relative_path,
        "originalPath": change["originalPath"],
        "worktreeStatus": change["status"],
        "state": state,
        "size": size,
        "sha256": checksum,
        "hashKind": hash_kind,
    }


def collect_repository(repository_name: str, repository: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not repository.is_dir():
        raise RuntimeError(f"repository directory not found: {repository_name}")

    top_level = Path(run_git(repository, ["rev-parse", "--show-toplevel"]).stdout.strip()).resolve()
    if top_level != repository.resolve():
        raise RuntimeError(f"repository boundary mismatch for {repository_name}: {top_level}")

    branch = run_git(repository, ["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    commit = run_git(repository, ["rev-parse", "HEAD"]).stdout.strip()
    raw_status = run_git(
        repository,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
    ).stdout
    changes = parse_porcelain_v1_z(raw_status)
    overlays = [hash_overlay(repository_name, repository, change) for change in changes]
    overlays.sort(key=lambda item: (item["path"], item["worktreeStatus"]))

    return (
        {
            "name": repository_name,
            "path": "." if repository_name == "root" else repository.name,
            "branch": branch,
            "commit": commit,
            "dirty": bool(overlays),
            "dirtyEntryCount": len(overlays),
        },
        overlays,
    )


def is_git_tracked(repository: Path, relative_path: Path) -> bool:
    result = run_git(
        repository,
        ["ls-files", "--error-unmatch", "--", relative_path.as_posix()],
        check=False,
    )
    return result.returncode == 0


def collect_migrations(backend_repository: Path) -> list[dict[str, Any]]:
    migrations: list[dict[str, Any]] = []
    for index, file_name in enumerate(MIGRATION_FILES, start=1):
        relative_path = MIGRATION_RELATIVE_DIR / file_name
        source = backend_repository / relative_path
        exists = source.is_file()
        tracked = is_git_tracked(backend_repository, relative_path) if exists else False
        status_result = run_git(
            backend_repository,
            ["status", "--porcelain=v1", "--untracked-files=all", "--", relative_path.as_posix()],
            check=False,
        )
        migrations.append(
            {
                "sequence": index,
                "fileName": file_name,
                "path": relative_path.as_posix(),
                "exists": exists,
                "gitTracked": tracked,
                "worktreeStatus": status_result.stdout[:2] if status_result.stdout else "",
                "size": source.stat().st_size if exists else None,
                "sha256": sha256_file(source) if exists else None,
                "source": "overlay" if status_result.stdout else "commit",
            }
        )
    return migrations


def candidate_input_sha256(
    repositories: list[dict[str, Any]],
    overlays: list[dict[str, Any]],
    migrations: list[dict[str, Any]],
    test_api_base_url: str,
    release_api_base_url: str,
) -> str:
    candidate_input = {
        "repositories": repositories,
        "overlays": overlays,
        "migrations": migrations,
        "testApiBaseUrl": test_api_base_url,
        "releaseApiBaseUrl": release_api_base_url,
    }
    encoded = json.dumps(candidate_input, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(encoded)


def build_manifest(
    repository_root: Path,
    candidate_id: str,
    *,
    test_api_base_url: str = DEFAULT_TEST_API_BASE_URL,
    release_api_base_url: str = DEFAULT_RELEASE_API_BASE_URL,
    artifact_evidence_path: Path | None = None,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    repositories: list[dict[str, Any]] = []
    overlays: list[dict[str, Any]] = []
    for repository_name, relative_path in REPOSITORIES:
        repository_record, repository_overlays = collect_repository(
            repository_name,
            repository_root / relative_path,
        )
        repositories.append(repository_record)
        overlays.extend(repository_overlays)

    migrations = collect_migrations(repository_root / "kaipaile-server")
    input_sha256 = candidate_input_sha256(
        repositories,
        overlays,
        migrations,
        test_api_base_url,
        release_api_base_url,
    )
    blockers: list[dict[str, str]] = []
    for migration in migrations:
        if not migration["exists"]:
            blockers.append(
                {
                    "code": "MIGRATION_MISSING",
                    "subject": migration["fileName"],
                    "message": "fixed migration file is missing",
                }
            )
        elif not migration["gitTracked"]:
            blockers.append(
                {
                    "code": "MIGRATION_UNTRACKED",
                    "subject": migration["fileName"],
                    "message": "fixed migration file must be Git-tracked before candidate freeze",
                }
            )

    artifact_validation = None
    if artifact_evidence_path:
        artifact_validation = validate_artifact_evidence(
            artifact_evidence_path,
            candidate_id=candidate_id,
            candidate_input_sha256_value=input_sha256,
            test_api_base_url=test_api_base_url,
            release_api_base_url=release_api_base_url,
        )
        if artifact_validation["dependencyAudit"]["gate"] != "PASSED":
            blockers.append(
                {
                    "code": "DEPENDENCY_AUDIT_REVIEW_PENDING",
                    "subject": "admin/mini-program production dependencies",
                    "message": "high-severity npm audit findings require compatibility-aware review before freeze",
                }
            )
    else:
        blockers.extend(
            [
            {
                "code": "ARTIFACTS_NOT_CAPTURED",
                "subject": "backend/admin/mini-program",
                "message": "candidate artifacts and their hashes have not been captured",
            },
            {
                "code": "API_TARGETS_NOT_PROVEN",
                "subject": "mini-program test/release",
                "message": "intended API Base URLs are recorded but artifact-level proof is pending",
            },
            ]
        )

    blockers.extend(
        [
            {
                "code": "REMOTE_HELPER_NOT_VERIFIED",
                "subject": "production release helper",
                "message": "remote helper sync and safe-field verification require separate authorization",
            },
            {
                "code": "CREDENTIAL_RISK_PENDING",
                "subject": "release credentials",
                "message": "credential category owners and rotation decisions are pending",
            },
        ]
    )

    manifest = {
        "schemaVersion": 1,
        "candidateId": candidate_id,
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "phase": "00-231",
        "repositories": repositories,
        "overlays": overlays,
        "overlayPolicy": {
            "mode": "all-dirty-paths-explicitly-enumerated",
            "declaredOverlayCount": len(overlays),
            "unlistedDirtyPathCount": 0,
        },
        "migrations": migrations,
        "artifacts": artifact_validation["artifacts"] if artifact_validation else [],
        "artifactEvidence": artifact_validation["artifactEvidence"] if artifact_validation else None,
        "testApiBaseUrl": test_api_base_url,
        "releaseApiBaseUrl": release_api_base_url,
        "apiTargetProof": artifact_validation["apiTargetProof"] if artifact_validation else {
            "test": "PENDING",
            "release": "PENDING",
        },
        "dependencyAudit": artifact_validation["dependencyAudit"] if artifact_validation else {
            "gate": "PENDING",
        },
        "securityGate": {
            "localSanitizerTests": "PENDING",
            "remoteHelperBaseline": "AWAITING_SEPARATE_AUTHORIZATION",
            "remoteSafeFieldVerification": "AWAITING_SEPARATE_AUTHORIZATION",
        },
        "credentialRiskGate": {
            "status": "PENDING",
            "secretValuesRecorded": False,
        },
        "blockers": blockers,
        "decision": "NO-GO" if blockers else "GO",
        "status": "DRAFT" if blockers else "FROZEN",
    }
    manifest["candidateInputSha256"] = input_sha256
    return manifest


def write_manifest(
    manifest: dict[str, Any],
    output_directory: Path,
    *,
    refresh_existing_draft: bool = False,
) -> tuple[Path, Path, str]:
    if refresh_existing_draft:
        manifest_path = output_directory / "candidate-manifest.json"
        if not manifest_path.is_file():
            raise RuntimeError("cannot refresh a candidate manifest that does not exist")
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("status") != "DRAFT":
            raise RuntimeError("only a DRAFT candidate manifest may be refreshed")
        if existing.get("candidateId") != manifest.get("candidateId"):
            raise RuntimeError("candidateId changed while refreshing the manifest")
        if existing.get("candidateInputSha256") != manifest.get("candidateInputSha256"):
            raise RuntimeError("candidate input changed; generate a new candidateId instead of refreshing")
    else:
        output_directory.mkdir(parents=True, exist_ok=False)
    manifest_path = output_directory / "candidate-manifest.json"
    temporary_path = output_directory / "candidate-manifest.json.tmp"
    temporary_path.write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(manifest_path)
    manifest_sha256 = sha256_file(manifest_path)
    checksum_path = output_directory / "candidate-manifest.sha256"
    checksum_path.write_text(f"{manifest_sha256}  candidate-manifest.json\n", encoding="ascii")
    return manifest_path, checksum_path, manifest_sha256


def verify_manifest(manifest_path: Path, repository_root: Path) -> dict[str, Any]:
    stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_manifest = build_manifest(
        repository_root,
        stored_manifest["candidateId"],
        test_api_base_url=stored_manifest["testApiBaseUrl"],
        release_api_base_url=stored_manifest["releaseApiBaseUrl"],
    )
    stored_input_sha256 = stored_manifest.get("candidateInputSha256")
    current_input_sha256 = current_manifest["candidateInputSha256"]
    current = stored_input_sha256 == current_input_sha256
    return {
        "candidateId": stored_manifest["candidateId"],
        "verification": "CURRENT" if current else "INVALIDATED",
        "storedCandidateInputSha256": stored_input_sha256,
        "currentCandidateInputSha256": current_input_sha256,
        "current": current,
    }


def default_repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def parse_args() -> argparse.Namespace:
    now = datetime.now().astimezone()
    parser = argparse.ArgumentParser(description="Generate a secret-free KaiPai release-candidate manifest.")
    parser.add_argument("--repository-root", type=Path, default=default_repository_root())
    parser.add_argument("--candidate-id", default=now.strftime("%Y%m%d-%H%M%S-v3-draft"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--verify-manifest", type=Path)
    parser.add_argument("--artifact-evidence", type=Path)
    parser.add_argument("--refresh-existing-draft", action="store_true")
    parser.add_argument("--test-api-base-url", default=DEFAULT_TEST_API_BASE_URL)
    parser.add_argument("--release-api-base-url", default=DEFAULT_RELEASE_API_BASE_URL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify_manifest:
        verification = verify_manifest(args.verify_manifest.resolve(), args.repository_root)
        print(json.dumps(verification, ensure_ascii=True, indent=2))
        return 0 if verification["current"] else 3

    output_directory = args.output_dir or (
        args.repository_root.resolve() / RECORDS_RELATIVE_DIR / args.candidate_id / "00-231"
    )
    manifest = build_manifest(
        args.repository_root,
        args.candidate_id,
        test_api_base_url=args.test_api_base_url,
        release_api_base_url=args.release_api_base_url,
        artifact_evidence_path=args.artifact_evidence,
    )
    manifest_path, checksum_path, manifest_sha256 = write_manifest(
        manifest,
        output_directory,
        refresh_existing_draft=args.refresh_existing_draft,
    )
    print(
        json.dumps(
            {
                "candidateId": manifest["candidateId"],
                "status": manifest["status"],
                "decision": manifest["decision"],
                "blockerCount": len(manifest["blockers"]),
                "manifestPath": str(manifest_path),
                "checksumPath": str(checksum_path),
                "manifestSha256": manifest_sha256,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0 if manifest["decision"] == "GO" else 2


if __name__ == "__main__":
    raise SystemExit(main())
