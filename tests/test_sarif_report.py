from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.policy import BLOCKER, WARNING, Finding, ValidationInput
from themis.sarif_report import render_sarif


class SarifReportTests(unittest.TestCase):
    def test_sarif_report_contains_rules_results_and_locations(self) -> None:
        output = render_sarif(
            ValidationInput(
                repo=Path("/repo"),
                base="origin/main",
                changed_files=[ChangedFile("src/app.py", "M")],
                numstat=[Numstat("src/app.py", 3, 1)],
                diff_text="",
                tracked_files=[],
                commits=[],
                pr_description="",
                test_evidence="",
                ai_assisted=True,
                check_results=[],
            ),
            [
                Finding(BLOCKER, "missing-test-evidence", "No test evidence.", file="src/app.py"),
                Finding(WARNING, "upstream-ai-policy-present", "AI policy present."),
            ],
        )

        payload = json.loads(output)
        run = payload["runs"][0]
        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(run["tool"]["driver"]["name"], "Themis")
        self.assertFalse(run["invocations"][0]["executionSuccessful"])
        self.assertEqual(run["results"][0]["level"], "error")
        self.assertEqual(run["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "src/app.py")
        self.assertEqual(run["results"][1]["level"], "warning")


if __name__ == "__main__":
    unittest.main()
