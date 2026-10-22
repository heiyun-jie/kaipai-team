#!/usr/bin/env python3
"""Fail-closed admission gate for KaiPai mini-program manual acceptance."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
GENERATOR_PATH = SCRIPT_DIR / "generate-release-candidate-manifest.py"
RECORDS_RELATIVE_DIR = Path(".sce/runbooks/backend-admin-release/records")
DEFAULT_RUNTIME_RELATIVE_DIR = Path("kaipai-frontend/dist/dev/mp-weixin")
ISOLATED_BUILD_RELATIVE_DIR = Path("kaipai-frontend/dist/build/mp-weixin")
RUNTIME_SUFFIXES = {".js", ".json", ".wxml", ".wxss"}
CANDIDATE_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")

READY = "READY_FOR_MANUAL_ACCEPTANCE"
INVALID = "INVALID_CANDIDATE"
REFREEZE = "CANDIDATE_REFREEZE_REQUIRED"
RUNTIME_NOT_SWITCHED = "RUNTIME_NOT_SWITCHED"
TEST_STACK_NOT_READY = "TEST_STACK_NOT_READY"
EXIT_CODES = {
    READY: 0,
    INVALID: 2,
    REFREEZE: 3,
    RUNTIME_NOT_SWITCHED: 4,
    TEST_STACK_NOT_READY: 5,
}
TEST_ACCEPTANCE_IRRELEVANT_BLOCKERS = {
    "REMOTE_HELPER_NOT_VERIFIED",
    "CREDENTIAL_RISK_PENDING",
}


def load_generator_module():
    spec = importlib.util.spec_from_file_location("release_candidate_manifest_acceptance", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator_module()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def resolve_candidate_record(repository_root: Path, candidate_id: str) -> Path:
    if not CANDIDATE_ID_PATTERN.fullmatch(candidate_id):
        raise RuntimeError("candidateId contains unsupported characters")
    records_root = (repository_root / RECORDS_RELATIVE_DIR).resolve()
    record = (records_root / candidate_id / "00-231").resolve()
    try:
        record.relative_to(records_root)
    except ValueError as exc:
        raise RuntimeError("candidate record escapes the records directory") from exc
    return record


def verify_checksum_sidecar(checksum_path: Path, target_path: Path) -> str:
    if not checksum_path.is_file() or not target_path.is_file():
        raise RuntimeError(f"checksum input is missing: {target_path.name}")
    lines = checksum_path.read_text(encoding="ascii").splitlines()
    if len(lines) != 1:
        raise RuntimeError(f"checksum sidecar must contain one line: {checksum_path.name}")
    match = re.fullmatch(r"([0-9a-f]{64})  (.+)", lines[0])
    if not match or match.group(2) != target_path.name:
        raise RuntimeError(f"checksum sidecar format mismatch: {checksum_path.name}")
    actual = GENERATOR.sha256_file(target_path)
    if actual != match.group(1):
        raise RuntimeError(f"checksum mismatch: {target_path.name}")
    return actual


def artifact_by_name(evidence: dict[str, Any], name: str) -> dict[str, Any]:
    for item in evidence.get("artifacts", []):
        if isinstance(item, dict) and item.get("name") == name:
            return item
    raise RuntimeError(f"candidate artifact is missing: {name}")


def validate_manifest_test_boundary(manifest: dict[str, Any], evidence_sha256: str) -> None:
    artifact_evidence = manifest.get("artifactEvidence")
    if not isinstance(artifact_evidence, dict):
        raise RuntimeError("candidate manifest does not bind artifact evidence")
    if artifact_evidence.get("path") != "artifact-evidence.json" or artifact_evidence.get("sha256") != evidence_sha256:
        raise RuntimeError("candidate manifest artifact evidence binding mismatch")

    mini_audit = manifest.get("dependencyAudit", {}).get("miniProgram", {})
    if mini_audit.get("classification") == "CONTROLLED_BUILD_TOOLCHAIN_ONLY":
        try:
            expiry = datetime.fromisoformat(mini_audit["riskExpiry"])
            current = expiry.tzinfo is not None and datetime.now(timezone.utc) < expiry
        except (KeyError, TypeError, ValueError):
            current = False
        if not current:
            raise RuntimeError("mini-program build dependency review expired or missing")

    status_pair = (manifest.get("status"), manifest.get("decision"))
    if status_pair == ("FROZEN", "GO"):
        return
    if status_pair != ("DRAFT", "NO-GO"):
        raise RuntimeError("candidate manifest status/decision is unsupported")
    blockers = manifest.get("blockers")
    if not isinstance(blockers, list):
        raise RuntimeError("candidate manifest blockers must be a list")
    blocker_codes = {
        item.get("code")
        for item in blockers
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    }
    if len(blocker_codes) != len(blockers) or not blocker_codes.issubset(TEST_ACCEPTANCE_IRRELEVANT_BLOCKERS):
        raise RuntimeError("candidate manifest contains blockers that affect test acceptance")


def compare_directory(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(path.resolve()), "exists": path.is_dir(), "equivalent": False}
    if not path.is_dir():
        return result
    actual = GENERATOR.hash_artifact_directory(path)
    result.update({field: actual[field] for field in ("fileCount", "totalSize", "treeSha256")})
    result["equivalent"] = all(actual[field] == expected.get(field) for field in ("fileCount", "totalSize", "treeSha256"))
    return result


def repository_input_check(
    repository_root: Path,
    manifest: dict[str, Any],
    repository_name: str,
) -> dict[str, Any]:
    stored_repository = next(
        (item for item in manifest.get("repositories", []) if item.get("name") == repository_name),
        None,
    )
    if stored_repository is None:
        raise RuntimeError(f"candidate repository input is missing: {repository_name}")
    repository_path = repository_root / str(stored_repository["path"])
    current_repository, current_overlays = GENERATOR.collect_repository(repository_name, repository_path)
    stored_overlays = [item for item in manifest.get("overlays", []) if item.get("repository") == repository_name]
    stored_payload = {"repository": stored_repository, "overlays": stored_overlays}
    current_payload = {"repository": current_repository, "overlays": current_overlays}
    return {
        "repository": repository_name,
        "current": stored_payload == current_payload,
        "storedInputSha256": sha256_json(stored_payload),
        "currentInputSha256": sha256_json(current_payload),
        "storedOverlayCount": len(stored_overlays),
        "currentOverlayCount": len(current_overlays),
    }


def scan_api_targets(path: Path, test_url: str, release_url: str) -> dict[str, Any]:
    markers = {
        "test": test_url.encode("utf-8"),
        "release": release_url.encode("utf-8"),
        "local127": b"http://127.0.0.1",
        "localhost": b"http://localhost",
        "localIpv6": b"http://[::1]",
    }
    matches: dict[str, list[str]] = {name: [] for name in markers}
    for source in sorted((item for item in path.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        if source.suffix.lower() not in RUNTIME_SUFFIXES:
            continue
        content = source.read_bytes()
        relative = source.relative_to(path).as_posix()
        for name, marker in markers.items():
            if marker in content:
                matches[name].append(relative)
    return {
        "passed": bool(matches["test"]) and not any(matches[name] for name in ("release", "local127", "localhost", "localIpv6")),
        "testMatchedFiles": matches["test"],
        "releaseMatchedFiles": matches["release"],
        "localMatchedFiles": sorted(set(matches["local127"] + matches["localhost"] + matches["localIpv6"])),
    }


def verify_runtime_proof(
    proof_path: Path,
    *,
    candidate_id: str,
    runtime_dir: Path,
    runtime_tree_sha256: str | None,
    test_url: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(proof_path.resolve()), "exists": proof_path.is_file(), "passed": False}
    if not proof_path.is_file():
        return result
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    required = {
        "schemaVersion": proof.get("schemaVersion") == 1,
        "candidateId": proof.get("candidateId") == candidate_id,
        "projectPath": Path(str(proof.get("projectPath", ""))).resolve() == runtime_dir.resolve(),
        "runtimeTreeSha256": proof.get("runtimeTreeSha256") == runtime_tree_sha256,
        "expectedApiBaseUrl": proof.get("expectedApiBaseUrl") == test_url,
        "testApiMatches": isinstance(proof.get("testApiMatches"), int) and proof["testApiMatches"] > 0,
        "localApiMatches": proof.get("localApiMatches") == 0,
        "releaseApiMatches": proof.get("releaseApiMatches") == 0,
        "liveRequestVerified": proof.get("liveRequestVerified") is True,
        "liveRequestEnvironment": proof.get("liveRequestEnvironment") == "test",
        "status": proof.get("status") == "PASSED",
    }
    result["checks"] = required
    result["passed"] = all(required.values())
    return result


def verify_test_stack_proof(
    proof_path: Path,
    *,
    candidate_id: str,
    backend_artifact: dict[str, Any],
    manifest_sha256: str,
    evidence_sha256: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {"path": str(proof_path.resolve()), "exists": proof_path.is_file(), "passed": False}
    if not proof_path.is_file():
        return result
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    backend_sha256 = backend_artifact.get("sha256")
    backup_sha256 = proof.get("testDatabaseBackupSha256")
    required = {
        "schemaVersion": proof.get("schemaVersion") == 1,
        "candidateId": proof.get("candidateId") == candidate_id,
        "candidateManifestSha256": proof.get("candidateManifestSha256") == manifest_sha256,
        "artifactEvidenceSha256": proof.get("artifactEvidenceSha256") == evidence_sha256,
        "candidateBackendJarSha256": proof.get("candidateBackendJarSha256") == backend_sha256,
        "runtimeBackendJarSha256": proof.get("runtimeBackendJarSha256") == backend_sha256,
        "testContainerName": proof.get("testContainerName") == "kaipai-backend-test",
        "database": proof.get("database") == "kaipai_test",
        "migration": proof.get("migration") == "V20260901_001__actor_card_internal_auto_expand.sql",
        "testDatabaseBackupSha256": isinstance(backup_sha256, str)
        and re.fullmatch(r"[0-9a-f]{64}", backup_sha256) is not None,
        "schemaContractPassed": proof.get("schemaContractPassed") is True,
        "apiHealthPassed": proof.get("apiHealthPassed") is True,
        "productionContainerUnchanged": proof.get("productionContainerUnchanged") is True,
        "productionMutation": proof.get("productionMutation") == "NONE",
        "status": proof.get("status") == "PASSED",
    }
    result["checks"] = required
    result["candidateBackendJarSha256"] = backend_sha256
    result["runtimeBackendJarSha256"] = proof.get("runtimeBackendJarSha256")
    result["passed"] = all(required.values())
    return result


def invalid_result(candidate_id: str, message: str) -> dict[str, Any]:
    return {
        "candidateId": candidate_id,
        "status": INVALID,
        "exitCode": EXIT_CODES[INVALID],
        "readyForManualAcceptance": False,
        "error": message,
    }


def evaluate_acceptance(
    repository_root: Path,
    candidate_id: str,
    *,
    runtime_dir: Path | None = None,
    build_dir: Path | None = None,
    runtime_proof: Path | None = None,
    test_stack_proof: Path | None = None,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    fixed_runtime_dir = (repository_root / DEFAULT_RUNTIME_RELATIVE_DIR).resolve()
    runtime_dir = (runtime_dir or fixed_runtime_dir).resolve()
    # Manual acceptance is bound to the frozen candidate and fixed dev runtime.
    # A workspace build directory is an optional diagnostic only; requiring it
    # here recreates the dual-entry failure that 00-252 removes.
    try:
        if runtime_dir != fixed_runtime_dir:
            raise RuntimeError("--runtime-dir must be the fixed dist/dev/mp-weixin runtime directory")
        if build_dir is not None:
            build_dir = build_dir.resolve()
            try:
                build_dir.relative_to(repository_root)
            except ValueError as exc:
                raise RuntimeError("--build-dir must stay inside the repository") from exc
            if build_dir == runtime_dir:
                raise RuntimeError("--build-dir must not be the fixed dist/dev runtime directory")
        record = resolve_candidate_record(repository_root, candidate_id)
        manifest_path = record / "candidate-manifest.json"
        evidence_path = record / "artifact-evidence.json"
        manifest_sha256 = verify_checksum_sidecar(record / "candidate-manifest.sha256", manifest_path)
        evidence_sha256 = verify_checksum_sidecar(record / "artifact-evidence.sha256", evidence_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if manifest.get("candidateId") != candidate_id or evidence.get("candidateId") != candidate_id:
            raise RuntimeError("candidateId does not match the frozen record")
        validate_manifest_test_boundary(manifest, evidence_sha256)
        GENERATOR.validate_artifact_evidence(
            evidence_path,
            candidate_id=candidate_id,
            candidate_input_sha256_value=manifest["candidateInputSha256"],
            test_api_base_url=manifest["testApiBaseUrl"],
            release_api_base_url=manifest["releaseApiBaseUrl"],
        )
        mini_program = artifact_by_name(evidence, "mini-program-test")
        backend_artifact = artifact_by_name(evidence, "backend-jar")
        candidate_dir = GENERATOR.resolve_record_artifact(evidence_path, str(mini_program["relativePath"]))
        candidate_check = compare_directory(candidate_dir, mini_program)
        if not candidate_check["equivalent"]:
            raise RuntimeError("frozen mini-program-test no longer matches artifact evidence")
    except (KeyError, OSError, RuntimeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return invalid_result(candidate_id, str(exc))

    try:
        input_checks = [
            repository_input_check(repository_root, manifest, name)
            for name in ("backend", "admin", "frontend")
        ]
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        return invalid_result(candidate_id, str(exc))

    build_check = (
        compare_directory(build_dir, mini_program)
        if build_dir is not None
        else {
            "checked": False,
            "equivalent": True,
            "reason": "workspace build is not a manual runtime entry",
        }
    )
    runtime_check = compare_directory(runtime_dir, mini_program)
    runtime_tree = runtime_check.get("treeSha256")
    api_check = scan_api_targets(runtime_dir, manifest["testApiBaseUrl"], manifest["releaseApiBaseUrl"]) if runtime_dir.is_dir() else {"passed": False}
    proof_path = runtime_proof or record.parent / "00-243" / "runtime-readiness.json"
    try:
        proof_check = verify_runtime_proof(
            proof_path,
            candidate_id=candidate_id,
            runtime_dir=runtime_dir,
            runtime_tree_sha256=runtime_tree,
            test_url=manifest["testApiBaseUrl"],
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        proof_check = {"path": str(proof_path.resolve()), "exists": proof_path.is_file(), "passed": False, "error": str(exc)}

    stack_proof_path = test_stack_proof or record.parent / "00-247" / "test-stack-readiness.json"
    try:
        stack_proof_check = verify_test_stack_proof(
            stack_proof_path,
            candidate_id=candidate_id,
            backend_artifact=backend_artifact,
            manifest_sha256=manifest_sha256,
            evidence_sha256=evidence_sha256,
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        stack_proof_check = {
            "path": str(stack_proof_path.resolve()),
            "exists": stack_proof_path.is_file(),
            "passed": False,
            "error": str(exc),
        }

    inputs_current = all(item["current"] for item in input_checks)
    if not inputs_current or not build_check["equivalent"]:
        status = REFREEZE
    elif not runtime_check["equivalent"] or not api_check.get("passed") or not proof_check.get("passed"):
        status = RUNTIME_NOT_SWITCHED
    elif not stack_proof_check.get("passed"):
        status = TEST_STACK_NOT_READY
    else:
        status = READY

    return {
        "candidateId": candidate_id,
        "status": status,
        "exitCode": EXIT_CODES[status],
        "readyForManualAcceptance": status == READY,
        "recordPath": str(record),
        "candidateManifestSha256": manifest_sha256,
        "artifactEvidenceSha256": evidence_sha256,
        "candidate": candidate_check,
        "candidateInputs": {"current": inputs_current, "repositories": input_checks},
        "workspaceBuild": build_check,
        "runtimeMirror": runtime_check,
        "runtimeApiTarget": api_check,
        "runtimeProof": proof_check,
        "testStackProof": stack_proof_check,
    }


def default_repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a frozen mini-program candidate before manual acceptance.")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--repository-root", type=Path, default=default_repository_root())
    parser.add_argument("--runtime-dir", type=Path)
    parser.add_argument(
        "--build-dir",
        type=Path,
        help="Optional isolated Candidate build directory; omit for the fixed dist/dev manual runtime.",
    )
    parser.add_argument("--runtime-proof", type=Path)
    parser.add_argument("--test-stack-proof", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON output path; written for both pass and fail results.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = evaluate_acceptance(
        args.repository_root,
        args.candidate_id,
        runtime_dir=args.runtime_dir,
        build_dir=args.build_dir,
        runtime_proof=args.runtime_proof,
        test_stack_proof=args.test_stack_proof,
    )
    rendered = json.dumps(result, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return int(result["exitCode"])


if __name__ == "__main__":
    raise SystemExit(main())
