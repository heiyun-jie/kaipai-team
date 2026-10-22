import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "generate-release-candidate-manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("generate_release_candidate_manifest", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_git(repository: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )


class ReleaseCandidateManifestTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        self.repositories = {
            "root": self.root,
            "backend": self.root / "kaipaile-server",
            "admin": self.root / "kaipai-admin",
            "frontend": self.root / "kaipai-frontend",
        }
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / ".gitignore").write_text(
            "kaipaile-server/\nkaipai-admin/\nkaipai-frontend/\nrecords/\n",
            encoding="utf-8",
        )
        for name, repository in self.repositories.items():
            repository.mkdir(parents=True, exist_ok=True)
            run_git(repository, "init", "-b", "V3.0")
            run_git(repository, "config", "user.email", "candidate-test@example.invalid")
            run_git(repository, "config", "user.name", "Candidate Test")
            (repository / f"{name}.txt").write_text(f"{name}\n", encoding="utf-8")

        migration_directory = self.repositories["backend"] / self.module.MIGRATION_RELATIVE_DIR
        migration_directory.mkdir(parents=True)
        for migration_name in self.module.MIGRATION_FILES:
            (migration_directory / migration_name).write_text(
                f"-- {migration_name}\nSELECT 1;\n",
                encoding="utf-8",
            )
        for repository in self.repositories.values():
            run_git(repository, "add", ".")
            run_git(repository, "commit", "-m", "baseline")

    def tearDown(self):
        self.temp_directory.cleanup()

    def create_artifact_evidence(self, manifest):
        evidence_directory = self.root / "records" / manifest["candidateId"]
        artifact_root = evidence_directory / "artifacts"
        backend = artifact_root / "backend" / "app.jar"
        backend.parent.mkdir(parents=True)
        backend.write_bytes(b"jar")

        artifacts = [
            {
                "name": "backend-jar",
                "type": "file",
                "relativePath": backend.relative_to(evidence_directory).as_posix(),
                "size": backend.stat().st_size,
                "sha256": self.module.sha256_file(backend),
            }
        ]
        for name in ("admin-dist", "mini-program-test", "mini-program-release"):
            directory = artifact_root / name
            directory.mkdir(parents=True)
            (directory / "app.js").write_text(f"{name}\n", encoding="utf-8")
            tree = self.module.hash_artifact_directory(directory)
            artifacts.append(
                {
                    "name": name,
                    "type": "directory",
                    "relativePath": directory.relative_to(evidence_directory).as_posix(),
                    "fileCount": tree["fileCount"],
                    "totalSize": tree["totalSize"],
                    "treeSha256": tree["treeSha256"],
                }
            )

        evidence = {
            "candidateId": manifest["candidateId"],
            "candidateInputSha256": manifest["candidateInputSha256"],
            "status": "PASSED",
            "artifacts": artifacts,
            "apiTargetProof": {
                "test": {
                    "expectedBaseUrl": manifest["testApiBaseUrl"],
                    "matchedFiles": ["common/vendor.js"],
                    "forbiddenMatches": [],
                    "passed": True,
                },
                "release": {
                    "expectedBaseUrl": manifest["releaseApiBaseUrl"],
                    "matchedFiles": ["common/vendor.js"],
                    "forbiddenMatches": [],
                    "passed": True,
                },
            },
            "dependencyAudit": {
                "admin": {"counts": {"high": 0, "critical": 0}, "directFindings": [], "gate": "PASSED"},
                "miniProgram": {"counts": {"high": 0, "critical": 0}, "directFindings": [], "gate": "PASSED"},
                "gate": "PASSED",
            },
        }
        evidence_path = evidence_directory / "artifact-evidence.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        return evidence_path

    def test_manifest_enumerates_exact_migration_order_and_dirty_overlays(self):
        (self.repositories["frontend"] / "frontend.txt").write_text("changed\n", encoding="utf-8")
        (self.repositories["backend"] / "new-service.txt").write_text("new\n", encoding="utf-8")

        manifest = self.module.build_manifest(self.root, "candidate-test")

        self.assertEqual(
            [item["fileName"] for item in manifest["migrations"]],
            list(self.module.MIGRATION_FILES),
        )
        self.assertTrue(all(item["gitTracked"] for item in manifest["migrations"]))
        overlay_keys = {(item["repository"], item["path"]) for item in manifest["overlays"]}
        self.assertIn(("frontend", "frontend.txt"), overlay_keys)
        self.assertIn(("backend", "new-service.txt"), overlay_keys)
        self.assertEqual(
            manifest["overlayPolicy"]["declaredOverlayCount"],
            len(manifest["overlays"]),
        )

    def test_untracked_final_migration_is_a_hard_blocker(self):
        final_relative_path = self.module.MIGRATION_RELATIVE_DIR / self.module.MIGRATION_FILES[-1]
        run_git(self.repositories["backend"], "rm", final_relative_path.as_posix())
        run_git(self.repositories["backend"], "commit", "-m", "remove final migration")
        final_path = self.repositories["backend"] / final_relative_path
        final_path.write_text("-- recreated but untracked\nSELECT 1;\n", encoding="utf-8")

        manifest = self.module.build_manifest(self.root, "candidate-untracked")

        blocker_codes = [item["code"] for item in manifest["blockers"]]
        self.assertIn("MIGRATION_UNTRACKED", blocker_codes)
        self.assertEqual(manifest["decision"], "NO-GO")
        self.assertEqual(manifest["status"], "DRAFT")

    def test_deleted_file_uses_a_stable_tombstone_hash(self):
        deleted_path = self.repositories["admin"] / "admin.txt"
        deleted_path.unlink()

        first = self.module.build_manifest(self.root, "candidate-delete")
        second = self.module.build_manifest(self.root, "candidate-delete")
        first_overlay = next(
            item for item in first["overlays"] if item["repository"] == "admin" and item["path"] == "admin.txt"
        )
        second_overlay = next(
            item for item in second["overlays"] if item["repository"] == "admin" and item["path"] == "admin.txt"
        )

        self.assertEqual(first_overlay["state"], "deleted")
        self.assertEqual(first_overlay["hashKind"], "deletion-tombstone")
        self.assertEqual(first_overlay["sha256"], second_overlay["sha256"])

    def test_verify_manifest_invalidates_candidate_after_input_change(self):
        manifest = self.module.build_manifest(self.root, "candidate-verification")
        manifest_path, _, _ = self.module.write_manifest(manifest, self.root / "records" / "candidate-verification")

        current = self.module.verify_manifest(manifest_path, self.root)
        (self.repositories["frontend"] / "frontend.txt").write_text("changed later\n", encoding="utf-8")
        invalidated = self.module.verify_manifest(manifest_path, self.root)

        self.assertEqual(current["verification"], "CURRENT")
        self.assertTrue(current["current"])
        self.assertEqual(invalidated["verification"], "INVALIDATED")
        self.assertFalse(invalidated["current"])
        self.assertNotEqual(
            invalidated["storedCandidateInputSha256"],
            invalidated["currentCandidateInputSha256"],
        )

    def test_valid_artifact_evidence_clears_artifact_and_api_blockers(self):
        initial = self.module.build_manifest(self.root, "candidate-artifacts")
        evidence_path = self.create_artifact_evidence(initial)

        with_artifacts = self.module.build_manifest(
            self.root,
            "candidate-artifacts",
            artifact_evidence_path=evidence_path,
        )

        blocker_codes = {item["code"] for item in with_artifacts["blockers"]}
        self.assertNotIn("ARTIFACTS_NOT_CAPTURED", blocker_codes)
        self.assertNotIn("API_TARGETS_NOT_PROVEN", blocker_codes)
        self.assertEqual(len(with_artifacts["artifacts"]), 4)
        self.assertTrue(with_artifacts["apiTargetProof"]["test"]["passed"])

    def test_artifact_evidence_rejects_changed_artifact_content(self):
        initial = self.module.build_manifest(self.root, "candidate-artifact-tamper")
        evidence_path = self.create_artifact_evidence(initial)
        changed_artifact = evidence_path.parent / "artifacts" / "admin-dist" / "app.js"
        changed_artifact.write_text("tampered\n", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "artifact directory"):
            self.module.build_manifest(
                self.root,
                "candidate-artifact-tamper",
                artifact_evidence_path=evidence_path,
            )


if __name__ == "__main__":
    unittest.main()
