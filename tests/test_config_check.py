from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_repo import create_example_target_repo, write
from themis.config_check import config_exit_code, inspect_config, render_config_json, render_config_markdown


class ConfigCheckTests(unittest.TestCase):
    def test_missing_config_warns_but_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            inspection = inspect_config(repo)
            self.assertEqual(config_exit_code(inspection), 0)
            self.assertEqual(inspection.checks[0].status, "WARN")

    def test_valid_policy_and_ai_config_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[policy]\nmax_changed_files = 5\n\n[ai]\nenabled = false\nprovider = "none"\n')
            inspection = inspect_config(repo)
            self.assertEqual(config_exit_code(inspection), 0)
            self.assertEqual({check.code: check.status for check in inspection.checks}, {"policy-config": "PASS", "ai-config": "PASS"})

    def test_invalid_config_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[policy]\nunknown = true\n\n[ai]\nprovider = "bogus"\n')
            inspection = inspect_config(repo)
            self.assertEqual(config_exit_code(inspection), 2)
            self.assertEqual({check.code: check.status for check in inspection.checks}, {"policy-config": "FAIL", "ai-config": "FAIL"})

    def test_outputs_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            inspection = inspect_config(repo)
            markdown = render_config_markdown(inspection)
            payload = json.loads(render_config_json(inspection))
            self.assertIn("Themis Config Check", markdown)
            self.assertEqual(payload["workflow"], "config check")
            self.assertEqual(payload["status"], "pass")


if __name__ == "__main__":
    unittest.main()
