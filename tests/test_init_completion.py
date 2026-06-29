from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.completion import render_completion
from themis.init import init_repo


class InitAndCompletionTests(unittest.TestCase):
    def test_init_writes_default_files_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            result = init_repo(repo)
            self.assertEqual({path.name for path in result.written}, {".themis.toml", "pr-body.md"})
            self.assertEqual(result.skipped, [])

            second = init_repo(repo)
            self.assertEqual(second.written, [])
            self.assertEqual({path.name for path in second.skipped}, {".themis.toml", "pr-body.md"})

    def test_init_can_skip_body_template(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            result = init_repo(repo, include_pr_body=False)
            self.assertEqual([path.name for path in result.written], [".themis.toml"])
            self.assertFalse((repo / "pr-body.md").exists())

    def test_init_config_includes_safe_ai_provider_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            init_repo(repo, include_pr_body=False)
            config = (repo / ".themis.toml").read_text(encoding="utf-8")
            self.assertIn("[ai]", config)
            self.assertIn("enabled = false", config)
            self.assertIn('provider = "none"', config)
            self.assertIn('allowed_workflows = ["explain", "guide", "maintainer-packet", "rules"]', config)

    def test_completion_contains_expected_commands(self) -> None:
        for shell in ("bash", "zsh", "fish"):
            with self.subTest(shell=shell):
                output = render_completion(shell)
                self.assertIn("themis", output)
                self.assertIn("validate", output)
                self.assertIn("pull-request", output)
                self.assertIn("--body-file" if shell != "fish" else "body-file", output)


if __name__ == "__main__":
    unittest.main()
