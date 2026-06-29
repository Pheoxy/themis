from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_repo import create_example_target_repo, write
from themis.policy import PolicyConfig
from themis.rules import inspect_rules, render_rules_json, render_rules_markdown, rules_exit_code


class RulesTests(unittest.TestCase):
    def test_rules_inspection_detects_docs_and_inferred_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / "CONTRIBUTING.md", "Run tests. Add release notes. Use Signed-off-by.\n")
            inspection = inspect_rules(repo, PolicyConfig(required_checks=["nix flake check"]))

            self.assertIn("CONTRIBUTING.md", inspection.rule_docs)
            self.assertTrue(inspection.inferred.dco_or_signoff)
            self.assertTrue(inspection.inferred.changelog_or_release_notes)
            self.assertTrue(inspection.inferred.tests_mentioned)
            self.assertEqual(rules_exit_code(inspection), 0)

    def test_rules_inspection_fails_closed_when_rules_missing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            inspection = inspect_rules(repo, PolicyConfig(require_upstream_rules=True))
            self.assertEqual(inspection.rule_docs, [])
            self.assertEqual(rules_exit_code(inspection), 2)

    def test_rules_outputs_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            inspection = inspect_rules(repo, PolicyConfig())
            markdown = render_rules_markdown(inspection)
            payload = json.loads(render_rules_json(inspection))
            self.assertIn("Themis Rules Inspection", markdown)
            self.assertEqual(payload["tool"], "themis")
            self.assertEqual(payload["workflow"], "rules")
            self.assertIn("rule_docs", payload)

    def test_accountability_language_does_not_infer_ai_forbidden(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".github" / "pull_request_template.md", "Human accountability: State that you, not Themis or any AI tool, take responsibility.\n")
            inspection = inspect_rules(repo, PolicyConfig())
            self.assertFalse(inspection.inferred.ai_appears_forbidden)

    def test_common_upstream_rule_styles_are_inferred(self) -> None:
        cases = [
            (
                "python",
                {
                    "CONTRIBUTING.md": "Before opening a pull request, run pytest and update changelog fragments in news/. Reference the issue this closes.\n",
                    ".github/pull_request_template.md": "- [ ] I ran the test suite\n- [ ] I added release notes\n",
                },
                {
                    "changelog_or_release_notes": True,
                    "issue_or_reference_link": True,
                    "pull_request_checklist": True,
                    "tests_mentioned": True,
                },
            ),
            (
                "rust",
                {
                    "CONTRIBUTING.md": "Commits must follow Conventional Commits. Run cargo test. Developer Certificate of Origin sign-off is required.\n",
                },
                {
                    "conventional_commits": True,
                    "dco_or_signoff": True,
                    "tests_mentioned": True,
                },
            ),
            (
                "node",
                {
                    ".github/CONTRIBUTING.md": "Use npm test, mention generated code, and disclose AI generated contributions in the PR description.\n",
                },
                {
                    "ai_disclosure_policy": True,
                    "tests_mentioned": True,
                },
            ),
        ]

        for name, files, expected in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as raw:
                    repo = create_example_target_repo(Path(raw))
                    for relative, content in files.items():
                        write(repo / relative, content)
                    inferred = inspect_rules(repo, PolicyConfig()).inferred
                    for field, value in expected.items():
                        self.assertEqual(getattr(inferred, field), value, field)


if __name__ == "__main__":
    unittest.main()
