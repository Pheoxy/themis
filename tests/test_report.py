from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.policy import BLOCKER, CheckResult, Finding, ValidationInput
from themis.report import check_output_snippet, render_markdown


class ReportTests(unittest.TestCase):
    def test_report_caveat_does_not_transfer_accountability(self) -> None:
        report = render_markdown(
            make_input(),
            [],
        )
        self.assertIn("does not certify", report)
        self.assertIn("Accountability remains with the submitter", report)

    def test_report_includes_changed_files_and_blocked_next_actions(self) -> None:
        report = render_markdown(
            make_input(changed_files=[ChangedFile("src/app.py", "M")]),
            [Finding(BLOCKER, "missing-test-evidence", "No passing test evidence was provided.", file="src/app.py")],
        )

        self.assertIn("Status: **BLOCKED**", report)
        self.assertIn("## Changed Files", report)
        self.assertIn("- `M` `src/app.py`", report)
        self.assertIn("missing-test-evidence", report)
        self.assertIn("Resolve every blocker", report)

    def test_report_includes_required_check_output_snippets(self) -> None:
        report = render_markdown(
            make_input(
                check_results=[
                    CheckResult(
                        command="nix flake check",
                        returncode=1,
                        output="unit test failed\ntraceback details",
                    )
                ]
            ),
            [],
        )

        self.assertIn("## Required Checks", report)
        self.assertIn("`nix flake check`: failed (1)", report)
        self.assertIn("```text\nunit test failed\ntraceback details\n```", report)
        self.assertIn("Continue normal human review", report)

    def test_check_output_snippet_is_bounded_and_safe_for_fences(self) -> None:
        snippet = check_output_snippet(f"before ``` after {'x' * 1300}")

        self.assertIn("` ` `", snippet)
        self.assertTrue(snippet.endswith("..."))
        self.assertLessEqual(len(snippet), 1210)


def make_input(
    *,
    changed_files: list[ChangedFile] | None = None,
    check_results: list[CheckResult] | None = None,
) -> ValidationInput:
    files = changed_files or []
    return ValidationInput(
        repo=Path("/repo"),
        base="origin/main",
        changed_files=files,
        numstat=[Numstat(item.path, 1, 0) for item in files],
        diff_text="",
        tracked_files=[],
        commits=[],
        pr_description="",
        test_evidence="",
        ai_assisted=True,
        check_results=check_results or [],
    )


if __name__ == "__main__":
    unittest.main()
