import importlib.util
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "build-release-candidate-artifacts.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_release_candidate_artifacts", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BuildReleaseCandidateArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.module.MINI_PROGRAM_BUILD_RISK_EXPIRY = '2099-11-05T23:59:59+08:00'
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        # Freeze policy evaluation time independently of wall-clock test execution.
        self.time_patch = patch.object(self.module, 'datetime', wraps=self.module.datetime)
        clock = self.time_patch.start()
        clock.now.return_value = self.module.datetime.fromisoformat('2026-10-22T00:00:00+00:00')

    def tearDown(self):
        self.temp_directory.cleanup()
        self.time_patch.stop()

    def test_api_target_scan_requires_expected_and_rejects_forbidden_urls(self):
        artifact = self.root / "artifact"
        artifact.mkdir()
        runtime = artifact / "app.js"
        runtime.write_text('const base="https://test-api.kplyyk.com";\n', encoding="utf-8")

        passed = self.module.scan_api_target(
            artifact,
            "https://test-api.kplyyk.com",
            ("https://api.kplyyk.com", "http://127.0.0.1"),
        )
        runtime.write_text(
            'const base="https://test-api.kplyyk.com";const local="http://127.0.0.1:8080";\n',
            encoding="utf-8",
        )
        failed = self.module.scan_api_target(
            artifact,
            "https://test-api.kplyyk.com",
            ("https://api.kplyyk.com", "http://127.0.0.1"),
        )

        self.assertTrue(passed["passed"])
        self.assertEqual(passed["matchedFiles"], ["app.js"])
        self.assertFalse(failed["passed"])
        self.assertEqual(failed["forbiddenMatches"][0]["baseUrl"], "http://127.0.0.1")

    def test_test_candidate_freezes_deterministic_private_project_config(self):
        output = self.root / "dist" / "build" / "mp-weixin"
        output.mkdir(parents=True)

        private_config = self.module.write_test_project_private_config(output)

        self.assertEqual(
            private_config.read_bytes(),
            b'{\n  "setting": {\n    "urlCheck": false\n  }\n}\n',
        )
        self.assertEqual(
            self.module.GENERATOR.sha256_file(private_config),
            "88b903ddaaebfd05316394e807c589b217c877a8192ead6a9e6970a8a037d898",
        )

    def test_apply_overlays_copies_present_files_and_removes_deletions(self):
        live = self.root / "live"
        snapshot = self.root / "build" / "repo"
        live.mkdir()
        snapshot.mkdir(parents=True)
        (live / "changed.txt").write_text("new\n", encoding="utf-8")
        (snapshot / "changed.txt").write_text("old\n", encoding="utf-8")
        (snapshot / "deleted.txt").write_text("delete me\n", encoding="utf-8")
        overlays = [
            {
                "repository": "frontend",
                "path": "changed.txt",
                "originalPath": None,
                "state": "present",
                "hashKind": "file-content",
                "sha256": self.module.GENERATOR.sha256_file(live / "changed.txt"),
            },
            {
                "repository": "frontend",
                "path": "deleted.txt",
                "originalPath": None,
                "state": "deleted",
                "hashKind": "deletion-tombstone",
                "sha256": self.module.GENERATOR.sha256_bytes(b"DELETE\0deleted.txt"),
            },
        ]

        self.module.apply_manifest_overlays("frontend", live, snapshot, overlays, self.root / "build")

        self.assertEqual((snapshot / "changed.txt").read_text(encoding="utf-8"), "new\n")
        self.assertFalse((snapshot / "deleted.txt").exists())

    def test_sanitized_environment_removes_secrets_and_unrelated_vite_values(self):
        original = dict(os.environ)
        try:
            os.environ["EXAMPLE_SECRET_TOKEN"] = "do-not-copy"
            os.environ["VITE_OTHER_VALUE"] = "do-not-copy"
            environment = self.module.sanitized_build_environment("https://api.kplyyk.com")
        finally:
            os.environ.clear()
            os.environ.update(original)

        self.assertNotIn("EXAMPLE_SECRET_TOKEN", environment)
        self.assertNotIn("VITE_OTHER_VALUE", environment)
        self.assertEqual(environment["VITE_API_BASE_URL"], "https://api.kplyyk.com")

    def test_npm_audit_summary_requires_review_for_high_findings(self):
        summary = self.module.summarize_npm_audit(
            {
                "metadata": {
                    "vulnerabilities": {
                        "info": 0,
                        "low": 0,
                        "moderate": 1,
                        "high": 2,
                        "critical": 0,
                        "total": 3,
                    }
                },
                "vulnerabilities": {
                    "axios": {
                        "severity": "high",
                        "isDirect": True,
                        "fixAvailable": True,
                    }
                },
            }
        )

        self.assertEqual(summary["gate"], "REVIEW_REQUIRED")
        self.assertEqual(summary["directFindings"][0]["name"], "axios")

    def write_miniprogram_lock(self, runtime_version="9.14.5"):
        lock = {
            "packages": {
                "node_modules/vue-i18n": {"version": runtime_version},
                "node_modules/vue-i18n/node_modules/@intlify/core-base": {
                    "version": runtime_version
                },
                "node_modules/@intlify/core-base": {"version": "9.1.9"},
            }
        }
        (self.root / "package-lock.json").write_text(
            json.dumps(lock), encoding="utf-8"
        )
        review = json.loads((SCRIPT_PATH.parent / 'miniprogram-reviewed-build-advisories.json').read_text(encoding='utf-8'))
        review['frontendLockfileSha256'] = self.module.GENERATOR.sha256_file(self.root / 'package-lock.json')
        self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH = self.root / 'review.json'
        self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH.write_text(json.dumps(review), encoding='utf-8')

    def test_miniprogram_build_tool_findings_pass_only_with_artifact_proof(self):
        self.write_miniprogram_lock()
        artifact = self.root / "artifact"
        artifact.mkdir()
        (artifact / "app.js").write_text("const runtime = 'wechat';\n", encoding="utf-8")
        audit = {
            "counts": {"critical": 0, "high": 3},
            "advisoryKeys": list(json.loads(self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH.read_text(encoding='utf-8'))['advisories']),
            "advisoryPackages": [
                "@intlify/core-base",
                "browserslist",
                "postcss-selector-parser",
                "vite",
                "ws",
            ],
            "directFindings": [],
            "vulnerablePackages": [
                "@dcloudio/uni-app",
                "browserslist",
                "postcss-selector-parser",
                "vite",
                "ws",
            ],
            "gate": "REVIEW_REQUIRED",
        }

        classified = self.module.classify_miniprogram_dependency_audit(
            audit, self.root, artifact
        )

        self.assertEqual(classified["gate"], "PASSED")
        self.assertEqual(
            classified["residualRiskDecision"], "RISK_ACCEPTED_WITH_EXPIRY"
        )
        self.assertEqual(classified["unreviewedAdvisoryPackages"], [])
        self.assertTrue(classified["artifactReachabilityProof"]["runtimeI18nSafe"])

    def test_miniprogram_unknown_advisory_remains_blocked(self):
        self.write_miniprogram_lock()
        artifact = self.root / "artifact"
        artifact.mkdir()
        (artifact / "app.js").write_text("const runtime = 'wechat';\n", encoding="utf-8")
        audit = {
            "counts": {"critical": 0, "high": 1},
            "advisoryPackages": ["unexpected-runtime-library"],
            "directFindings": [],
            "vulnerablePackages": ["unexpected-runtime-library"],
            "gate": "REVIEW_REQUIRED",
        }

        classified = self.module.classify_miniprogram_dependency_audit(
            audit, self.root, artifact
        )

        self.assertEqual(classified["gate"], "REVIEW_REQUIRED")
        self.assertEqual(
            classified["unreviewedAdvisoryPackages"],
            ["unexpected-runtime-library"],
        )

    def test_miniprogram_old_runtime_i18n_remains_blocked(self):
        self.write_miniprogram_lock(runtime_version="9.1.9")
        artifact = self.root / "artifact"
        artifact.mkdir()
        (artifact / "app.js").write_text("const runtime = 'wechat';\n", encoding="utf-8")
        audit = {
            "counts": {"critical": 0, "high": 1},
            "advisoryPackages": ["@intlify/core-base"],
            "directFindings": [],
            "vulnerablePackages": ["@intlify/core-base"],
            "gate": "REVIEW_REQUIRED",
        }

        classified = self.module.classify_miniprogram_dependency_audit(
            audit, self.root, artifact
        )

        self.assertEqual(classified["gate"], "REVIEW_REQUIRED")
        self.assertFalse(classified["artifactReachabilityProof"]["runtimeI18nSafe"])

    def test_expired_build_risk_acceptance_is_rejected(self):
        self.write_miniprogram_lock()
        artifact = self.root / 'artifact'
        artifact.mkdir()
        (artifact / 'app.js').write_text('const runtime = 1;')
        self.module.MINI_PROGRAM_BUILD_RISK_EXPIRY = '2000-01-01T00:00:00+00:00'
        result = self.module.classify_miniprogram_dependency_audit(
            {'counts': {'critical': 0}, 'advisoryPackages': ['vite'], 'advisoryKeys': ['vite|https://github.com/advisories/GHSA-9cwx-2883-4wfx']}, self.root, artifact)
        self.assertEqual(result['gate'], 'REVIEW_REQUIRED')
        self.assertFalse(result['reviewCurrent'])

    def test_ssr_or_source_map_code_in_runtime_is_rejected(self):
        self.write_miniprogram_lock()
        artifact = self.root / 'artifact'
        artifact.mkdir()
        for marker in ['ssrRenderAttrs', 'SourceMapConsumer', 'baseline-browser-mapping', 'braces/lib/parse']:
            with self.subTest(marker=marker):
                (artifact / 'app.js').write_text(marker)
                result = self.module.classify_miniprogram_dependency_audit(
                    {'counts': {'critical': 0}, 'advisoryPackages': ['vite'], 'advisoryKeys': list(json.loads(self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH.read_text(encoding='utf-8'))['advisories'])}, self.root, artifact)
                self.assertEqual(result['gate'], 'REVIEW_REQUIRED')
                self.assertTrue(result['artifactReachabilityProof']['forbiddenToolchainMarkerMatches'])

    def test_unknown_advisory_in_known_build_package_is_rejected(self):
        self.write_miniprogram_lock()
        artifact = self.root / 'artifact'
        artifact.mkdir()
        (artifact / 'app.js').write_text('const runtime = 1;')
        audit = self.module.summarize_npm_audit({
            'metadata': {'vulnerabilities': {'high': 1, 'critical': 0}},
            'vulnerabilities': {'vite': {'via': [{'name': 'vite', 'url': 'https://github.com/advisories/GHSA-unknown'}]}}})
        result = self.module.classify_miniprogram_dependency_audit(audit, self.root, artifact)
        self.assertEqual(result['gate'], 'REVIEW_REQUIRED')

    def test_changed_lockfile_or_critical_finding_remains_blocked(self):
        self.write_miniprogram_lock()
        artifact = self.root / 'artifact'
        artifact.mkdir()
        (artifact / 'app.js').write_text('const runtime = 1;')
        audit = {'counts': {'critical': 0}, 'advisoryPackages': ['vite'], 'advisoryKeys': list(json.loads(self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH.read_text(encoding='utf-8'))['advisories'])}
        self.assertEqual(self.module.classify_miniprogram_dependency_audit(audit, self.root, artifact)['gate'], 'PASSED')
        audit['counts']['critical'] = 1
        self.assertEqual(self.module.classify_miniprogram_dependency_audit(audit, self.root, artifact)['gate'], 'REVIEW_REQUIRED')
        audit['counts']['critical'] = 0
        with (self.root / 'package-lock.json').open('a') as f: f.write('\n')
        result = self.module.classify_miniprogram_dependency_audit(audit, self.root, artifact)
        self.assertEqual(result['gate'], 'REVIEW_REQUIRED')
        self.assertFalse(result['reviewedLockCurrent'])

    def test_high_findings_without_advisory_identity_are_rejected(self):
        self.write_miniprogram_lock()
        artifact = self.root / 'artifact'
        artifact.mkdir()
        (artifact / 'app.js').write_text('const runtime = 1;')
        audit = self.module.summarize_npm_audit({'metadata': {'vulnerabilities': {'high': 2, 'critical': 0}}, 'vulnerabilities': {}})
        self.assertEqual(self.module.classify_miniprogram_dependency_audit(audit, self.root, artifact)['gate'], 'REVIEW_REQUIRED')

    def test_audit_error_json_is_not_a_clean_audit(self):
        for payload in [{'error': {'code': 'ENOAUDIT'}}, {'message': 'registry unavailable'},
                        {'metadata': {}, 'vulnerabilities': {}}]:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(RuntimeError, 'audit'):
                    self.module.summarize_npm_audit(payload)

    def test_tool_code_in_wxs_is_rejected(self):
        self.write_miniprogram_lock()
        artifact = self.root / 'artifact'
        artifact.mkdir()
        (artifact / 'helpers.wxs').write_text('SourceMapConsumer')
        result = self.module.classify_miniprogram_dependency_audit(
            {'counts': {'critical': 0}, 'advisoryPackages': ['vite'], 'advisoryKeys': list(json.loads(self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH.read_text(encoding='utf-8'))['advisories'])}, self.root, artifact)
        self.assertEqual(result['gate'], 'REVIEW_REQUIRED')
        self.assertTrue(result['artifactReachabilityProof']['forbiddenToolchainMarkerMatches'])

    def test_marker_only_in_test_artifact_blocks_delivery(self):
        self.write_miniprogram_lock()
        test_dir, release_dir = self.root / 'test', self.root / 'release'
        test_dir.mkdir(); release_dir.mkdir()
        (test_dir / 'helper.wxs').write_text('SourceMapConsumer')
        (release_dir / 'app.js').write_text('const runtime = 1;')
        audit = {'counts': {'critical': 0}, 'advisoryPackages': ['vite'], 'advisoryKeys': list(json.loads(self.module.MINI_PROGRAM_ADVISORY_REVIEW_PATH.read_text(encoding='utf-8'))['advisories'])}
        result = self.module.classify_miniprogram_artifacts(audit, self.root, test_dir, release_dir)
        self.assertEqual(result['gate'], 'REVIEW_REQUIRED')
        self.assertEqual(result['artifactAuditByEnvironment']['release']['gate'], 'PASSED')
        self.assertEqual(result['artifactAuditByEnvironment']['test']['gate'], 'REVIEW_REQUIRED')


if __name__ == "__main__":
    unittest.main()
