from pathlib import Path
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_repo import create_example_target_repo, write
from themis.providers import FAIL, PASS, WARN, inspect_providers, providers_exit_code, render_providers_json, render_providers_markdown


class ProviderTests(unittest.TestCase):
    def test_providers_are_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            diagnostics = inspect_providers(repo)
            self.assertFalse(diagnostics.config.enabled)
            self.assertEqual(providers_exit_code(diagnostics), 0)
            self.assertIn(PASS, {check.status for check in diagnostics.checks})

    def test_external_provider_requires_api_key_env(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "openai"\nmodel = "gpt-test"\napi_key_env = "THEMIS_TEST_KEY"\n')
            with patch.dict(os.environ, {}, clear=True):
                diagnostics = inspect_providers(repo)
            statuses = {check.code: check.status for check in diagnostics.checks}
            self.assertEqual(statuses["provider-api-key-env"], FAIL)
            self.assertEqual(providers_exit_code(diagnostics), 2)

    def test_external_provider_passes_when_api_key_env_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "anthropic"\nmodel = "claude-test"\napi_key_env = "THEMIS_TEST_KEY"\n')
            with patch.dict(os.environ, {"THEMIS_TEST_KEY": "secret-value"}, clear=True):
                diagnostics = inspect_providers(repo)
            statuses = {check.code: check.status for check in diagnostics.checks}
            self.assertEqual(statuses["provider-api-key-env"], PASS)
            self.assertEqual(providers_exit_code(diagnostics), 0)

    def test_provider_workflows_cannot_include_gate_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "ollama"\nmodel = "local"\nallowed_workflows = ["validate"]\n')
            diagnostics = inspect_providers(repo)
            statuses = {check.code: check.status for check in diagnostics.checks}
            self.assertEqual(statuses["provider-workflows"], FAIL)
            self.assertIn(WARN, {check.status for check in diagnostics.checks})

    def test_provider_outputs_markdown_and_json_without_secret_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "openai"\nmodel = "gpt-test"\napi_key_env = "THEMIS_TEST_KEY"\n')
            with patch.dict(os.environ, {"THEMIS_TEST_KEY": "secret-value"}, clear=True):
                diagnostics = inspect_providers(repo)
            markdown = render_providers_markdown(diagnostics)
            payload = json.loads(render_providers_json(diagnostics))
            self.assertIn("Themis AI Providers", markdown)
            self.assertEqual(payload["workflow"], "providers")
            self.assertNotIn("secret-value", markdown)
            self.assertNotIn("secret-value", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
