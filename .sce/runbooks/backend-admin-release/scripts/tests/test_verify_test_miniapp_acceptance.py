import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "verify-test-miniapp-acceptance.py"
SPEC = importlib.util.spec_from_file_location("verify_test_miniapp_acceptance", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class TestMiniappAcceptanceTests(unittest.TestCase):
    candidate_id = "candidate-test-001"

    def test_expired_review_is_rejected_even_for_previously_frozen_manifest(self):
        manifest = {'artifactEvidence': {'path': 'artifact-evidence.json', 'sha256': 'x'},
                    'status': 'FROZEN', 'decision': 'GO',
                    'dependencyAudit': {'miniProgram': {'classification': 'CONTROLLED_BUILD_TOOLCHAIN_ONLY',
                        'riskExpiry': '2000-01-01T00:00:00+00:00'}}}
        with self.assertRaisesRegex(RuntimeError, 'expired'):
            MODULE.validate_manifest_test_boundary(manifest, 'x')

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.repositories = {}
        for name, relative in (("backend", "kaipaile-server"), ("admin", "kaipai-admin"), ("frontend", "kaipai-frontend")):
            repository = self.root / relative
            repository.mkdir(parents=True)
            self._git(repository, "init")
            self._git(repository, "config", "user.email", "tests@example.invalid")
            self._git(repository, "config", "user.name", "KaiPai Tests")
            (repository / "source.txt").write_text(f"{name}\n", encoding="utf-8")
            if name == "frontend":
                (repository / ".gitignore").write_text("dist/\n", encoding="utf-8")
                self._git(repository, "add", ".gitignore")
            self._git(repository, "add", "source.txt")
            self._git(repository, "commit", "-m", "fixture")
            self.repositories[name] = repository

        self.record = self.root / MODULE.RECORDS_RELATIVE_DIR / self.candidate_id / "00-231"
        self.record.mkdir(parents=True)
        self.runtime_dir = self.root / MODULE.DEFAULT_RUNTIME_RELATIVE_DIR
        self.build_dir = self.root / MODULE.ISOLATED_BUILD_RELATIVE_DIR
        self.proof_path = self.record.parent / "00-243" / "runtime-readiness.json"
        self.stack_proof_path = self.record.parent / "00-247" / "test-stack-readiness.json"
        self._write_candidate()

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def _git(repository: Path, *arguments: str):
        subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    @staticmethod
    def _write_sidecar(path: Path, target: Path):
        path.write_text(f"{MODULE.GENERATOR.sha256_file(target)}  {target.name}\n", encoding="ascii")

    @staticmethod
    def _directory_artifact(name: str, relative_path: str, path: Path):
        hashed = MODULE.GENERATOR.hash_artifact_directory(path)
        return {"name": name, "type": "directory", "relativePath": relative_path, **{key: hashed[key] for key in ("fileCount", "totalSize", "treeSha256")}}

    def _write_candidate(self):
        artifacts_root = self.record / "artifacts"
        backend_dir = artifacts_root / "backend"
        admin_dir = artifacts_root / "admin"
        test_dir = artifacts_root / "mini-program-test"
        release_dir = artifacts_root / "mini-program-release"
        for path in (backend_dir, admin_dir, test_dir, release_dir):
            path.mkdir(parents=True)
        backend_file = backend_dir / "backend.jar"
        backend_file.write_bytes(b"fixture-jar")
        (admin_dir / "index.html").write_text("admin", encoding="utf-8")
        (test_dir / "app.js").write_text('const api = "https://test-api.kplyyk.com";\n', encoding="utf-8")
        (release_dir / "app.js").write_text('const api = "https://api.kplyyk.com";\n', encoding="utf-8")

        repositories = []
        overlays = []
        for name in ("backend", "admin", "frontend"):
            repository, repository_overlays = MODULE.GENERATOR.collect_repository(name, self.repositories[name])
            repositories.append(repository)
            overlays.extend(repository_overlays)
        manifest = {
            "schemaVersion": 1,
            "candidateId": self.candidate_id,
            "testApiBaseUrl": "https://test-api.kplyyk.com",
            "releaseApiBaseUrl": "https://api.kplyyk.com",
            "repositories": repositories,
            "overlays": overlays,
            "candidateInputSha256": "1" * 64,
            "decision": "NO-GO",
            "status": "DRAFT",
            "blockers": [
                {"code": "REMOTE_HELPER_NOT_VERIFIED"},
                {"code": "CREDENTIAL_RISK_PENDING"},
            ],
        }
        manifest_path = self.record / "candidate-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        evidence = {
            "schemaVersion": 1,
            "candidateId": self.candidate_id,
            "candidateInputSha256": manifest["candidateInputSha256"],
            "sourceManifestSha256": MODULE.GENERATOR.sha256_file(manifest_path),
            "artifacts": [
                {
                    "name": "backend-jar",
                    "type": "file",
                    "relativePath": "artifacts/backend/backend.jar",
                    "size": backend_file.stat().st_size,
                    "sha256": MODULE.GENERATOR.sha256_file(backend_file),
                },
                self._directory_artifact("admin-dist", "artifacts/admin", admin_dir),
                self._directory_artifact("mini-program-test", "artifacts/mini-program-test", test_dir),
                self._directory_artifact("mini-program-release", "artifacts/mini-program-release", release_dir),
            ],
            "apiTargetProof": {
                "test": {"expectedBaseUrl": manifest["testApiBaseUrl"], "matchedFiles": ["app.js"], "forbiddenMatches": [], "passed": True},
                "release": {"expectedBaseUrl": manifest["releaseApiBaseUrl"], "matchedFiles": ["app.js"], "forbiddenMatches": [], "passed": True},
            },
            "dependencyAudit": {"gate": "PASSED"},
            "status": "PASSED",
        }
        evidence_path = self.record / "artifact-evidence.json"
        evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        self._write_sidecar(self.record / "artifact-evidence.sha256", evidence_path)
        manifest["artifactEvidence"] = {
            "path": "artifact-evidence.json",
            "sha256": MODULE.GENERATOR.sha256_file(evidence_path),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self._write_sidecar(self.record / "candidate-manifest.sha256", manifest_path)

        for destination in (self.build_dir, self.runtime_dir):
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(test_dir, destination)
        runtime_hash = MODULE.GENERATOR.hash_artifact_directory(self.runtime_dir)
        self.proof_path.parent.mkdir(parents=True)
        self.proof_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "candidateId": self.candidate_id,
                    "projectPath": str(self.runtime_dir.resolve()),
                    "runtimeTreeSha256": runtime_hash["treeSha256"],
                    "expectedApiBaseUrl": manifest["testApiBaseUrl"],
                    "testApiMatches": 1,
                    "localApiMatches": 0,
                    "releaseApiMatches": 0,
                    "liveRequestVerified": True,
                    "liveRequestEnvironment": "test",
                    "status": "PASSED",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.stack_proof_path.parent.mkdir(parents=True)
        self.stack_proof_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "candidateId": self.candidate_id,
                    "candidateManifestSha256": MODULE.GENERATOR.sha256_file(manifest_path),
                    "artifactEvidenceSha256": MODULE.GENERATOR.sha256_file(evidence_path),
                    "candidateBackendJarSha256": MODULE.GENERATOR.sha256_file(backend_file),
                    "runtimeBackendJarSha256": MODULE.GENERATOR.sha256_file(backend_file),
                    "testContainerName": "kaipai-backend-test",
                    "database": "kaipai_test",
                    "migration": "V20260901_001__actor_card_internal_auto_expand.sql",
                    "testDatabaseBackupSha256": "a" * 64,
                    "schemaContractPassed": True,
                    "apiHealthPassed": True,
                    "productionContainerUnchanged": True,
                    "productionMutation": "NONE",
                    "status": "PASSED",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def _evaluate(self):
        return MODULE.evaluate_acceptance(
            self.root,
            self.candidate_id,
            runtime_dir=self.runtime_dir,
            build_dir=self.build_dir,
            runtime_proof=self.proof_path,
            test_stack_proof=self.stack_proof_path,
        )

    def test_equivalent_candidate_is_ready_for_manual_acceptance(self):
        result = self._evaluate()
        self.assertEqual(MODULE.READY, result["status"])
        self.assertEqual(0, result["exitCode"])
        self.assertTrue(result["readyForManualAcceptance"])

    def test_frontend_input_change_requires_refreeze(self):
        (self.repositories["frontend"] / "source.txt").write_text("changed\n", encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.REFREEZE, result["status"])
        self.assertFalse(result["candidateInputs"]["current"])

    def test_workspace_build_drift_requires_refreeze(self):
        (self.build_dir / "app.js").write_text("changed build\n", encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.REFREEZE, result["status"])
        self.assertFalse(result["workspaceBuild"]["equivalent"])

    def test_manual_runtime_gate_does_not_require_workspace_build(self):
        (self.build_dir / "app.js").write_text("stale workspace build\n", encoding="utf-8")
        result = MODULE.evaluate_acceptance(
            self.root,
            self.candidate_id,
            runtime_dir=self.runtime_dir,
            runtime_proof=self.proof_path,
            test_stack_proof=self.stack_proof_path,
        )
        self.assertEqual(MODULE.READY, result["status"])
        self.assertFalse(result["workspaceBuild"]["checked"])
        self.assertTrue(result["workspaceBuild"]["equivalent"])

    def test_runtime_override_cannot_create_second_entry(self):
        alternate_runtime = self.root / "alternate-runtime"
        shutil.copytree(self.runtime_dir, alternate_runtime)
        result = MODULE.evaluate_acceptance(
            self.root,
            self.candidate_id,
            runtime_dir=alternate_runtime,
            runtime_proof=self.proof_path,
            test_stack_proof=self.stack_proof_path,
        )
        self.assertEqual(MODULE.INVALID, result["status"])
        self.assertIn("fixed dist/dev/mp-weixin", result["error"])

    def test_runtime_drift_reports_not_switched(self):
        (self.runtime_dir / "app.js").write_text("changed runtime\n", encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.RUNTIME_NOT_SWITCHED, result["status"])
        self.assertFalse(result["runtimeMirror"]["equivalent"])

    def test_runtime_proof_must_bind_same_candidate(self):
        proof = json.loads(self.proof_path.read_text(encoding="utf-8"))
        proof["candidateId"] = "different-candidate"
        self.proof_path.write_text(json.dumps(proof), encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.RUNTIME_NOT_SWITCHED, result["status"])
        self.assertFalse(result["runtimeProof"]["passed"])

    def test_test_stack_proof_is_required(self):
        self.stack_proof_path.unlink()
        result = self._evaluate()
        self.assertEqual(MODULE.TEST_STACK_NOT_READY, result["status"])
        self.assertEqual(5, result["exitCode"])
        self.assertFalse(result["testStackProof"]["exists"])

    def test_runtime_backend_must_match_candidate_jar(self):
        proof = json.loads(self.stack_proof_path.read_text(encoding="utf-8"))
        proof["runtimeBackendJarSha256"] = "b" * 64
        self.stack_proof_path.write_text(json.dumps(proof), encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.TEST_STACK_NOT_READY, result["status"])
        self.assertFalse(result["testStackProof"]["checks"]["runtimeBackendJarSha256"])

    def test_test_schema_contract_must_pass(self):
        proof = json.loads(self.stack_proof_path.read_text(encoding="utf-8"))
        proof["schemaContractPassed"] = False
        self.stack_proof_path.write_text(json.dumps(proof), encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.TEST_STACK_NOT_READY, result["status"])
        self.assertFalse(result["testStackProof"]["checks"]["schemaContractPassed"])

    def test_frozen_candidate_tamper_is_invalid(self):
        candidate = self.record / "artifacts/mini-program-test/app.js"
        candidate.write_text("tampered\n", encoding="utf-8")
        result = self._evaluate()
        self.assertEqual(MODULE.INVALID, result["status"])
        self.assertEqual(2, result["exitCode"])

    def test_test_relevant_manifest_blocker_is_invalid(self):
        manifest_path = self.record / "candidate-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["blockers"].append({"code": "TEST_ARTIFACT_NOT_VERIFIED"})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self._write_sidecar(self.record / "candidate-manifest.sha256", manifest_path)
        result = self._evaluate()
        self.assertEqual(MODULE.INVALID, result["status"])
        self.assertIn("affect test acceptance", result["error"])


if __name__ == "__main__":
    unittest.main()
