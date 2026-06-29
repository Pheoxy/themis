from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.cli import build_parser, main
from themis.docs import GENERATED_HEADER, handle_cli_docs, render_cli_docs
from themis.policy import BLOCKER, Finding


class CliTests(unittest.TestCase):
    def test_validate_command_parses(self) -> None:
        parser = build_parser()
        for command in ("validate", "v"):
            with self.subTest(command=command):
                args = parser.parse_args([command, "--human", "--evidence", "tests passed"])
                self.assertEqual(args.command, command)
                self.assertFalse(args.ai_assisted)
                self.assertEqual(args.evidence, "tests passed")

    def test_pull_request_draft_command_parses(self) -> None:
        parser = build_parser()
        cases = (
            (["pull-request", "draft", "--body-file", "pr-body.md", "--title", "Add feature"], "pull-request", "draft"),
            (["pr", "d", "--body-file", "pr-body.md", "--title", "Add feature"], "pr", "d"),
        )
        for argv, command, pr_command in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertEqual(args.command, command)
                self.assertEqual(args.pr_command, pr_command)
                self.assertEqual(args.body_file, Path("pr-body.md"))
                self.assertEqual(args.title, "Add feature")

    def test_confusing_pre_release_aliases_are_not_supported(self) -> None:
        parser = build_parser()
        aliases = (
            ["check"],
            ["review"],
        )
        for argv in aliases:
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    parser.parse_args(argv)

    def test_explain_command_parses_optional_code(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["explain", "missing-test-evidence"])
        self.assertEqual(args.command, "explain")
        self.assertEqual(args.code, "missing-test-evidence")

    def test_generated_cli_docs_include_canonical_commands(self) -> None:
        docs = render_cli_docs()
        self.assertIn(GENERATED_HEADER, docs)
        self.assertIn("themis pull-request draft", docs)
        self.assertIn("validate (v)", docs)
        self.assertIn("guide (g)", docs)
        self.assertIn("maintainer-packet (mp)", docs)
        self.assertIn("explain", docs)
        self.assertIn("pull-request (pr)", docs)
        self.assertIn("draft (d)", docs)
        self.assertNotIn("validate (check", docs)
        self.assertNotIn("{validate,check", docs)
        self.assertNotIn("review", docs)
        self.assertIn("-B BODY_FILE, --body-file BODY_FILE", docs)
        self.assertIn("--run-checks", docs)
        self.assertIn("--format", docs)
        self.assertIn("--annotations", docs)

    def test_generated_cli_docs_check_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "cli.md"
            path.write_text("stale\n", encoding="utf-8")
            args = type("Args", (), {"path": path, "write": False, "check": True})()
            self.assertEqual(handle_cli_docs(args), 2)

    def test_validate_runs_gate_without_pr_draft_flags(self) -> None:
        for command in ("validate", "v"):
            with self.subTest(command=command):
                run = fake_validation_run()
                with tempfile.TemporaryDirectory() as raw:
                    output = Path(raw) / "report.md"
                    with (
                        patch("themis.cli.build_validation_run", return_value=run) as build_run,
                        patch("themis.cli.validate", return_value=[]),
                        patch("themis.cli.render_markdown", return_value="# report\n"),
                    ):
                        self.assertEqual(main([command, "--human", "--output", str(output)]), 0)

                    self.assertEqual(output.read_text(encoding="utf-8"), "# report\n")
                    self.assertFalse(build_run.call_args.kwargs["run_checks"])

    def test_guide_renders_readiness_guide(self) -> None:
        for command in ("guide", "g"):
            with self.subTest(command=command):
                run = fake_validation_run()
                with tempfile.TemporaryDirectory() as raw:
                    output = Path(raw) / "guide.md"
                    with (
                        patch("themis.cli.build_validation_run", return_value=run),
                        patch("themis.cli.validate", return_value=[]),
                        patch("themis.guide.render_guide", return_value="# guide\n") as render_guide,
                    ):
                        self.assertEqual(main([command, "--output", str(output)]), 0)

                    self.assertEqual(output.read_text(encoding="utf-8"), "# guide\n")
                    render_guide.assert_called_once()

    def test_maintainer_packet_renders_packet_and_returns_blocker_status(self) -> None:
        for command in ("maintainer-packet", "mp"):
            with self.subTest(command=command):
                run = fake_validation_run()
                findings = [Finding(BLOCKER, "blocked", "Blocked for test.")]
                with tempfile.TemporaryDirectory() as raw:
                    output = Path(raw) / "maintainer-packet.md"
                    with (
                        patch("themis.cli.build_validation_run", return_value=run),
                        patch("themis.cli.validate", return_value=findings),
                        patch("themis.review.render_review_packet", return_value="# packet\n") as render_packet,
                    ):
                        self.assertEqual(main([command, "--output", str(output)]), 2)

                    self.assertEqual(output.read_text(encoding="utf-8"), "# packet\n")
                    render_packet.assert_called_once()

    def test_validate_annotations_go_to_stderr_not_report_file(self) -> None:
        run = fake_validation_run()
        findings = [Finding(BLOCKER, "blocked", "Blocked for test.", file="src/app.py")]
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "report.md"
            stderr = io.StringIO()
            with (
                patch("themis.cli.build_validation_run", return_value=run),
                patch("themis.cli.validate", return_value=findings),
                patch("themis.cli.render_markdown", return_value="# report\n"),
                contextlib.redirect_stderr(stderr),
            ):
                self.assertEqual(main(["validate", "--output", str(output), "--annotations", "github"]), 2)

            self.assertEqual(output.read_text(encoding="utf-8"), "# report\n")
            self.assertIn("::error title=blocked,file=src/app.py::Blocked for test.", stderr.getvalue())

    def test_validate_can_write_json_output(self) -> None:
        run = fake_validation_run()
        findings = [Finding(BLOCKER, "blocked", "Blocked for test.", file="src/app.py")]
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "report.json"
            with (
                patch("themis.cli.build_validation_run", return_value=run),
                patch("themis.cli.validate", return_value=findings),
            ):
                self.assertEqual(main(["validate", "--output", str(output), "--format", "json"]), 2)

            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["workflow"], "validate")
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["findings"][0]["code"], "blocked")


def fake_validation_run() -> SimpleNamespace:
    data = SimpleNamespace(
        repo=Path("/tmp/repo"),
        base="origin/main",
        ai_assisted=True,
        changed_files=[],
        numstat=[],
        check_results=[],
    )
    return SimpleNamespace(
        root=Path("/tmp/repo"),
        config=SimpleNamespace(),
        pr_description="AI assistance: none",
        changed=[],
        stats=[],
        data=data,
    )


if __name__ == "__main__":
    unittest.main()
