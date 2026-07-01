from pathlib import Path
import unittest


class ActionMetadataTests(unittest.TestCase):
    def test_action_exposes_bot_friendly_outputs(self) -> None:
        action = (Path(__file__).resolve().parents[1] / "action.yml").read_text(encoding="utf-8")
        self.assertIn("outputs:", action)
        self.assertIn("branding:", action)
        self.assertIn("icon: shield", action)
        self.assertIn("color: blue", action)
        self.assertIn("status:", action)
        self.assertIn("exit-code:", action)
        self.assertIn("report:", action)
        self.assertIn("workflow:", action)
        self.assertIn("comment-pr:", action)
        self.assertIn("pr-number:", action)
        self.assertIn("INPUT_WORKFLOW", action)
        self.assertIn("gh pr comment", action)
        self.assertIn("pull-requests: write", (Path(__file__).resolve().parents[1] / "docs" / "github-action.md").read_text(encoding="utf-8"))
        self.assertIn("maintainer-packet", action)
        self.assertIn("self-check", action)
        self.assertIn("config-check", action)
        self.assertIn("command=(config check)", action)
        self.assertIn("draft-pr requires body-file", action)
        self.assertIn('"${command[0]}" != "config"', action)
        self.assertIn("id: validate", action)
        self.assertIn("GITHUB_OUTPUT", action)
        self.assertIn("exit \"$exit_code\"", action)

    def test_action_docs_cover_draft_body_file_requirement(self) -> None:
        docs = (Path(__file__).resolve().parents[1] / "docs" / "github-action.md").read_text(encoding="utf-8")
        self.assertIn("Required when `draft-pr` is `true`", docs)
        self.assertIn("Draft PR mode requires `body-file`", docs)
        self.assertIn("Marketplace", docs)
        self.assertIn("Do not move an existing public release tag", docs)


if __name__ == "__main__":
    unittest.main()
