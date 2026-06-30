from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.policy import BLOCKER, INFO, WARNING, Finding, ValidationInput
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
                Finding(BLOCKER, "missing-test-evidence", "No test evidence.", file="src/app.py", detail="Run pytest."),
                Finding(WARNING, "upstream-ai-policy-present", "AI policy present."),
                Finding(INFO, "clean-static-gate", "Clean."),
                Finding(BLOCKER, "missing-test-evidence", "No test evidence.", file="tests/test_app.py"),
            ],
        )

        payload = json.loads(output)
        run = payload["runs"][0]
        text = json.dumps(payload)
        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(run["tool"]["driver"]["name"], "Themis")
        self.assertNotIn("OWNER/themis", text)
        self.assertFalse(run["invocations"][0]["executionSuccessful"])
        self.assertEqual([rule["id"] for rule in run["tool"]["driver"]["rules"]], ["missing-test-evidence", "upstream-ai-policy-present", "clean-static-gate"])
        self.assertEqual(run["results"][0]["level"], "error")
        self.assertIn("Run pytest.", run["results"][0]["message"]["text"])
        self.assertRegex(run["results"][0]["partialFingerprints"]["themis/v1"], r"^[0-9a-f]{64}$")
        self.assertEqual(run["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "src/app.py")
        self.assertEqual(run["results"][1]["level"], "warning")
        self.assertEqual(run["results"][2]["level"], "note")
        self.assertNotEqual(run["results"][0]["partialFingerprints"], run["results"][3]["partialFingerprints"])


if __name__ == "__main__":
    unittest.main()
