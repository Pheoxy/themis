from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.explain import explain_code, remediation_for, render_explanation


class ExplainTests(unittest.TestCase):
    def test_explains_known_finding_code(self) -> None:
        item = explain_code("missing-test-evidence")
        self.assertIn("Code changed", item.summary)
        self.assertIn("exact passing", item.fix)

    def test_unknown_code_gets_safe_generic_explanation(self) -> None:
        item = explain_code("new-finding")
        self.assertEqual(item.code, "new-finding")
        self.assertIn("No specific explanation", item.summary)

    def test_remediation_respects_warning_and_info(self) -> None:
        self.assertIn("warning", remediation_for("upstream-ai-policy-present", "WARNING"))
        self.assertIn("No action required", remediation_for("clean-static-gate", "INFO"))

    def test_render_catalog_and_single_explanation(self) -> None:
        self.assertIn("missing-test-evidence", render_explanation())
        single = render_explanation("missing-test-evidence")
        self.assertIn("Themis Finding", single)
        self.assertIn("What to do", single)

    def test_process_gate_codes_have_specific_explanations(self) -> None:
        codes = [
            "upstream-forbids-ai",
            "missing-changelog-decision",
            "missing-issue-link",
            "pr-template-not-acknowledged",
            "cannot-verify-commit-style",
            "invalid-commit-style",
            "no-changes",
            "binary-change",
        ]
        for code in codes:
            with self.subTest(code=code):
                item = explain_code(code)
                self.assertNotIn("No specific explanation", item.summary)
                self.assertIn(code, render_explanation())

    def test_active_policy_finding_codes_have_explanations(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "src" / "themis" / "policy.py").read_text(encoding="utf-8")
        codes = sorted(set(re.findall(r'Finding\(\s*(?:BLOCKER|WARNING|INFO),\s*"([a-z0-9-]+)"', source)))
        pattern_explained = {code for code in codes if code.startswith("too-many") or code.endswith("too-large")}
        missing = [
            code
            for code in codes
            if code not in pattern_explained and "No specific explanation" in explain_code(code).summary
        ]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
