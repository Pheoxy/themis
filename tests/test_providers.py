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
from themis.providers import (
    FAIL,
    PASS,
    WARN,
    inspect_providers,
    preview_provider,
    providers_exit_code,
    render_provider_preview_json,
    render_provider_preview_markdown,
    render_providers_json,
    render_providers_markdown,
)


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

    def test_fake_provider_preview_makes_no_network_call(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "fake"\nmodel = "fake-model"\nallowed_workflows = ["guide"]\n')
            result = preview_provider(repo, workflow="guide", prompt="help")
            self.assertEqual(result.provider, "fake")
            self.assertIn("Fake provider preview", result.text)
            self.assertIn("no network call", result.disclosure)

    def test_custom_provider_preview_uses_explicit_command_env(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "custom"\nmodel = "custom-model"\ncommand_env = "THEMIS_PROVIDER_COMMAND"\nallowed_workflows = ["explain"]\n')
            command = f"{sys.executable} -c \"import sys; sys.stdin.read(); print('custom provider output')\""
            with patch.dict(os.environ, {"THEMIS_PROVIDER_COMMAND": command}, clear=True):
                result = preview_provider(repo, workflow="explain", prompt="explain")
            self.assertEqual(result.provider, "custom")
            self.assertEqual(result.text, "custom provider output")
            self.assertIn("THEMIS_PROVIDER_COMMAND", result.disclosure)

    def test_provider_preview_refuses_gate_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "fake"\nmodel = "fake-model"\n')
            with self.assertRaises(ValueError):
                preview_provider(repo, workflow="validate", prompt="decide")

    def test_provider_preview_outputs_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[ai]\nenabled = true\nprovider = "fake"\nmodel = "fake-model"\n')
            result = preview_provider(repo, workflow="guide", prompt="help")
            markdown = render_provider_preview_markdown(result)
            payload = json.loads(render_provider_preview_json(result))
            self.assertIn("Themis Provider Preview", markdown)
            self.assertEqual(payload["workflow"], "providers preview")
            self.assertIn("cannot change gate", payload["safety"])


if __name__ == "__main__":
    unittest.main()
