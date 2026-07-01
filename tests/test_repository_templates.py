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

    def test_github_sponsors_metadata_exists(self) -> None:
        funding = (self.root / ".github" / "FUNDING.yml").read_text(encoding="utf-8")
        self.assertIn("github: [Pheoxy]", funding)

    def test_renovate_version_updates_are_configured(self) -> None:
        renovate = (self.root / "renovate.json").read_text(encoding="utf-8")
        self.assertIn('"github-actions"', renovate)
        self.assertIn('"nix"', renovate)
        self.assertIn('"enabled": true', renovate)
        self.assertIn("lockFileMaintenance", renovate)
        self.assertIn("Nix flake inputs", renovate)
        self.assertIn("Signed-off-by: renovate[bot]", renovate)
        self.assertIn("Human accountability:", renovate)
        self.assertFalse((self.root / ".github" / "dependabot.yml").exists())

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
            "bug_report.yml": ("Themis Status", "Finding Codes", "Target Repository Context"),
            "feature_request.md": ("Themis Surface", ".themis.toml", "1.x compatibility surface"),
            "feature_request.yml": ("Themis Surface", "GitHub Action input/output", "major release / 1.x compatibility change"),
            "policy_false_positive.md": ("Policy False Positive", "Proposed Adjustment", "themis validate"),
            "policy_false_positive.yml": ("Policy False Positive", "Proposed Adjustment", "Command And Output"),
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
        self.assertNotIn("contact_links:", config)


if __name__ == "__main__":
    unittest.main()
