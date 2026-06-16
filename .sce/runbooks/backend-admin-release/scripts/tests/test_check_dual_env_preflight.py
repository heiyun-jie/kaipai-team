import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "check-dual-env-preflight.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_dual_env_preflight", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DualEnvPreflightTests(unittest.TestCase):
    def test_parse_sectioned_output_extracts_helper_sections(self):
        module = load_module()
        output = """
__FINAL_STATUS_BEGIN__
passed
__FINAL_STATUS_END__
__FAIL_REASON_BEGIN__

__FAIL_REASON_END__
"""

        sections = module.parse_sectioned_output(output, ["FINAL_STATUS", "FAIL_REASON"])

        self.assertEqual(sections["FINAL_STATUS"], "passed")
        self.assertEqual(sections["FAIL_REASON"], "")

    def test_summarize_nacos_config_checks_required_fragments_and_database(self):
        module = load_module()
        raw = """
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/kaipai_test
  data:
    redis:
      host: 127.0.0.1
"""

        summary = module.summarize_nacos_config(raw, "kaipai_test")

        self.assertTrue(summary["readable"])
        self.assertTrue(summary["containsExpectedDatabase"])
        self.assertEqual(summary["missingFragments"], [])

    def test_preflight_exit_code_fails_when_any_gate_fails(self):
        module = load_module()
        gates = {
            "dns": {"passed": False},
            "nacos": {"passed": True},
            "database": {"passed": True},
        }

        self.assertEqual(module.preflight_exit_code(gates), 1)

    def test_parse_table_count_result_requires_all_core_tables(self):
        module = load_module()
        mysql_result = """
+---------------+
| result        |
+---------------+
| TABLE_COUNT=5 |
+---------------+
"""

        summary = module.parse_table_count_result(mysql_result, expected_count=6)

        self.assertFalse(summary["schemaReady"])
        self.assertEqual(summary["foundTableCount"], 5)
        self.assertEqual(summary["expectedTableCount"], 6)


if __name__ == "__main__":
    unittest.main()
