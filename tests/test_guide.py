from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.guide import render_guide
from themis.policy import BLOCKER, Finding, PolicyConfig


class GuideTests(unittest.TestCase):
    def test_guide_includes_assistant_caveat_and_detected_rules(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "CONTRIBUTING.md").write_text("Run tests and add a changelog entry.\n", encoding="utf-8")
            guide = render_guide(
                repo,
                base="origin/main",
                changed=[ChangedFile("src/app.py", "M")],
                stats=[Numstat("src/app.py", 5, 1)],
                config=PolicyConfig(required_checks=["nix flake check"]),
                findings=[Finding(BLOCKER, "missing-test-changes", "Code changed, but no test files changed.")],
            )
            self.assertIn("Themis Upstream Assistant Guide", guide)
            self.assertIn("does not take accountability", guide)
            self.assertIn("Status: **BLOCKED**", guide)
            self.assertIn("missing-test-changes", guide)
            self.assertIn("CONTRIBUTING.md", guide)
            self.assertIn("Run configured required checks", guide)
            self.assertIn("Add or update tests", guide)

    def test_guide_handles_missing_rule_docs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            guide = render_guide(repo, base=None, changed=[], stats=[], config=PolicyConfig(), findings=[])
            self.assertIn("No contribution/rule documents detected", guide)


if __name__ == "__main__":
    unittest.main()
