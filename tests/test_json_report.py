from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.policy import BLOCKER, CheckResult, Finding, ValidationInput
from themis.json_report import render_json


class JsonReportTests(unittest.TestCase):
    def test_json_report_is_machine_readable_gate_result(self) -> None:
        output = render_json(
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
                check_results=[CheckResult("nix flake check", 0, "passed")],
            ),
            [Finding(BLOCKER, "missing-test-evidence", "No test evidence.", file="src/app.py")],
            workflow="validate",
            exit_code=2,
        )

        payload = json.loads(output)
        self.assertEqual(payload["tool"], "themis")
        self.assertEqual(payload["workflow"], "validate")
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["exit_code"], 2)
        self.assertEqual(payload["changed_files"][0]["path"], "src/app.py")
        self.assertEqual(payload["line_stats"][0]["added"], 3)
        self.assertEqual(payload["findings"][0]["code"], "missing-test-evidence")
        self.assertTrue(payload["required_checks"][0]["passed"])
        self.assertIn("not a certification", payload["accountability"])


if __name__ == "__main__":
    unittest.main()
