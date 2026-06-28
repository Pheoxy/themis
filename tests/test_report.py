from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.policy import ValidationInput
from themis.report import render_markdown


class ReportTests(unittest.TestCase):
    def test_report_caveat_does_not_transfer_accountability(self) -> None:
        report = render_markdown(
            ValidationInput(
                repo=Path("/repo"),
                base="origin/main",
                changed_files=[],
                numstat=[],
                diff_text="",
                tracked_files=[],
                commits=[],
                pr_description="",
                test_evidence="",
                ai_assisted=True,
                check_results=[],
            ),
            [],
        )
        self.assertIn("does not certify", report)
        self.assertIn("Accountability remains with the submitter", report)


if __name__ == "__main__":
    unittest.main()
