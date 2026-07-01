from pathlib import Path
import unittest


class RepositoryTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_themis_self_policy_exists(self) -> None:
        config = (self.root / ".themis.toml").read_text(encoding="utf-8")
        self.assertIn("[policy]", config)
        self.assertIn("require_upstream_rules = true", config)
        self.assertIn("require_test_changes_for_code = true", config)
        self.assertIn('"nix flake check"', config)
        self.assertIn("[ai]", config)
        self.assertIn("enabled = false", config)

    def test_pull_request_template_is_themis_specific(self) -> None:
        template = (self.root / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        required = (
            "themis self-check",
            "Finding codes added/changed/removed",
            "GitHub Action inputs/outputs affected",
            "Human accountability:",
            "Release Risk",
        )
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, template)

    def test_issue_templates_are_themis_specific(self) -> None:
        issue_dir = self.root / ".github" / "ISSUE_TEMPLATE"
        templates = {
            "bug_report.md": ("Themis Result", "Finding code(s)", "Target Repository Context"),
            "feature_request.md": ("Themis Surface", ".themis.toml", "1.x compatibility surface"),
            "policy_false_positive.md": ("Policy False Positive", "Proposed Adjustment", "themis validate"),
            "release-checklist.md": ("Themis Release Checklist", "nix flake check", "Remote Work Last"),
        }
        for filename, required in templates.items():
            text = (issue_dir / filename).read_text(encoding="utf-8")
            for phrase in required:
                with self.subTest(filename=filename, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_issue_template_config_points_to_security_policy(self) -> None:
        config = (self.root / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")
        self.assertIn("blank_issues_enabled: false", config)
        self.assertIn("https://github.com/Pheoxy/themis/security/policy", config)


if __name__ == "__main__":
    unittest.main()
