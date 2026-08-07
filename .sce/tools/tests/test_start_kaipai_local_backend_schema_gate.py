import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "start-kaipai-local-backend.ps1"


class LocalBackendSchemaGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_gate_compares_repository_migration_names_and_checksums(self):
        self.assertIn("function Assert-LocalSchemaCompatible", self.source)
        self.assertIn("Get-ChildItem -LiteralPath $MigrationDirectory -File -Filter 'V*.sql'", self.source)
        self.assertIn("schema_release_history", self.source)
        self.assertIn("Get-FileHash -LiteralPath $migration.FullName -Algorithm SHA256", self.source)
        self.assertIn('"migration:$($migration.Name)"', self.source)
        self.assertIn('"checksum:$($migration.Name)"', self.source)
        self.assertIn(
            'SELECT script, UPPER(checksum) FROM schema_release_history ORDER BY script;',
            self.source,
        )
        self.assertNotIn("CONCAT(script, CHAR(9), UPPER(checksum))", self.source)

    def test_gate_checks_runtime_critical_objects(self):
        for required_fragment in (
            "actor_profile.avatar_asset_id",
            "actor_profile.weight",
            "actor_profile.work_library_version",
            "actor_experience.dedupe_key",
            "actor_media_asset",
            "ai_profile_import_prompt_template",
        ):
            self.assertIn(required_fragment, self.source)

    def test_gate_runs_before_validation_success_or_java_start(self):
        service_check = self.source.index("Assert-LocalServicesReady -MySqlName")
        schema_check = self.source.index("Assert-LocalSchemaCompatible -MySqlName", service_check)
        java_lookup = self.source.index("$java = (Get-Command java", schema_check)
        validate_success = self.source.index("if ($ValidateOnly)", java_lookup)

        self.assertLess(service_check, schema_check)
        self.assertLess(schema_check, java_lookup)
        self.assertLess(java_lookup, validate_success)


if __name__ == "__main__":
    unittest.main()
