import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "sync-release-helper-baseline.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_release_helper_baseline_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


class SyncReleaseHelperBaselineTests(unittest.TestCase):
    def test_repository_contains_no_connection_or_password_fallback(self):
        with patch.dict(
            os.environ,
            {
                "KAIPAI_RELEASE_HOST": "",
                "KAIPAI_RELEASE_USER": "",
                "KAIPAI_RELEASE_PASSWORD": "",
                "KAIPAI_RELEASE_KNOWN_HOSTS_FILE": "",
            },
            clear=False,
        ):
            module = load_module()

        self.assertEqual(module.DEFAULT_HOST, "")
        self.assertEqual(module.DEFAULT_USER, "")
        self.assertEqual(module.DEFAULT_PASSWORD, "")

    def test_missing_connection_inputs_fail_before_local_or_remote_mutation(self):
        with patch.dict(
            os.environ,
            {
                "KAIPAI_RELEASE_HOST": "",
                "KAIPAI_RELEASE_USER": "",
                "KAIPAI_RELEASE_PASSWORD": "",
                "KAIPAI_RELEASE_KNOWN_HOSTS_FILE": "",
            },
            clear=False,
        ):
            module = load_module()
        with patch.object(module, "ensure_keypair") as ensure_keypair, patch.object(
            module, "sync_helper_baseline"
        ) as sync_helper:
            with patch.object(sys, "argv", [str(SCRIPT_PATH)]):
                with self.assertRaisesRegex(RuntimeError, "missing required helper sync input"):
                    module.main()

        ensure_keypair.assert_not_called()
        sync_helper.assert_not_called()

    def test_explicit_environment_inputs_build_context_without_repository_defaults(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            known_hosts = Path(temporary_directory) / "known_hosts"
            known_hosts.write_text("release.example ssh-ed25519 test-key\n", encoding="utf-8")
            environment = {
                "KAIPAI_RELEASE_HOST": "release.example",
                "KAIPAI_RELEASE_USER": "release-user",
                "KAIPAI_RELEASE_PASSWORD": "test-only-password",
                "KAIPAI_RELEASE_KNOWN_HOSTS_FILE": str(known_hosts),
            }
            with patch.dict(os.environ, environment, clear=False):
                module = load_module()
                context = module.build_context(module.parse_args([]))

        self.assertEqual(context.host, "release.example")
        self.assertEqual(context.user, "release-user")
        self.assertEqual(context.password, "test-only-password")
        self.assertEqual(context.known_hosts_file, known_hosts)

    def test_unknown_host_keys_are_rejected_for_paramiko_and_native_ssh(self):
        module = load_module()
        context = module.HelperSyncContext(
            host="release.example",
            user="release-user",
            password="test-only-password",
            operator="test",
            identity_file=Path("release-key"),
            known_hosts_file=Path("pinned-known-hosts"),
        )
        client = MagicMock()

        with patch.object(module.paramiko, "SSHClient", return_value=client), patch.object(
            module, "resolve_executable", return_value="ssh"
        ):
            created_client = module.create_ssh_client(context)
            command = module.ssh_base(context)

        self.assertIs(created_client, client)
        client.load_host_keys.assert_called_once_with(str(context.known_hosts_file))
        policy = client.set_missing_host_key_policy.call_args.args[0]
        self.assertIsInstance(policy, module.paramiko.RejectPolicy)
        self.assertIn("StrictHostKeyChecking=yes", command)
        self.assertIn(f"UserKnownHostsFile={context.known_hosts_file}", command)
        self.assertNotIn("StrictHostKeyChecking=accept-new", command)

    def test_source_does_not_use_auto_add_policy(self):
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertNotIn("AutoAddPolicy", source)
        self.assertIn("RejectPolicy", source)


if __name__ == "__main__":
    unittest.main()
