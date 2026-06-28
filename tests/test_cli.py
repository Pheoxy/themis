from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.cli import build_parser
from themis.docs import GENERATED_HEADER, handle_cli_docs, render_cli_docs


class CliTests(unittest.TestCase):
    def test_validate_aliases_parse_to_validate_command(self) -> None:
        parser = build_parser()
        for command in ("validate", "check", "v"):
            with self.subTest(command=command):
                args = parser.parse_args([command, "--human", "--evidence", "tests passed"])
                self.assertEqual(args.command, command)
                self.assertFalse(args.ai_assisted)
                self.assertEqual(args.evidence, "tests passed")

    def test_pull_request_aliases_parse_to_draft_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["pr", "d", "--body-file", "pr-body.md", "--title", "Add feature"])
        self.assertEqual(args.command, "pr")
        self.assertEqual(args.pr_command, "d")
        self.assertEqual(args.body_file, Path("pr-body.md"))
        self.assertEqual(args.title, "Add feature")

    def test_generated_cli_docs_include_normal_and_short_forms(self) -> None:
        docs = render_cli_docs()
        self.assertIn(GENERATED_HEADER, docs)
        self.assertIn("themis pull-request draft", docs)
        self.assertIn("pull-request (pr)", docs)
        self.assertIn("-B BODY_FILE, --body-file BODY_FILE", docs)
        self.assertIn("--run-checks", docs)

    def test_generated_cli_docs_check_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "cli.md"
            path.write_text("stale\n", encoding="utf-8")
            args = type("Args", (), {"path": path, "write": False, "check": True})()
            self.assertEqual(handle_cli_docs(args), 2)


if __name__ == "__main__":
    unittest.main()
