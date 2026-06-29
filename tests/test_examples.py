from pathlib import Path
import unittest


class ExampleWorkflowTests(unittest.TestCase):
    def test_github_action_examples_cover_core_workflows(self) -> None:
        root = Path(__file__).resolve().parents[1]
        validate = (root / "examples" / "github-actions" / "validate.yml").read_text(encoding="utf-8")
        comment = (root / "examples" / "github-actions" / "comment.yml").read_text(encoding="utf-8")
        self_check = (root / "examples" / "github-actions" / "self-check.yml").read_text(encoding="utf-8")

        self.assertIn("workflow: validate", validate)
        self.assertIn("pull-requests: read", validate)
        self.assertIn("workflow: maintainer-packet", comment)
        self.assertIn("format: comment", comment)
        self.assertIn("comment-pr: \"true\"", comment)
        self.assertIn("pull-requests: write", comment)
        self.assertIn("GH_TOKEN", comment)
        self.assertIn("workflow: self-check", self_check)


if __name__ == "__main__":
    unittest.main()
