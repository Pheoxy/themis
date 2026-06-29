from pathlib import Path
import unittest


class ActionMetadataTests(unittest.TestCase):
    def test_action_exposes_bot_friendly_outputs(self) -> None:
        action = (Path(__file__).resolve().parents[1] / "action.yml").read_text(encoding="utf-8")
        self.assertIn("outputs:", action)
        self.assertIn("status:", action)
        self.assertIn("exit-code:", action)
        self.assertIn("report:", action)
        self.assertIn("id: validate", action)
        self.assertIn("GITHUB_OUTPUT", action)
        self.assertIn("exit \"$exit_code\"", action)


if __name__ == "__main__":
    unittest.main()
