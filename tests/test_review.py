from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.policy import BLOCKER, Finding, PolicyConfig
from themis.review import feedback_for, render_review_packet


class ReviewPacketTests(unittest.TestCase):
    def test_review_packet_groups_blockers_for_maintainers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "CONTRIBUTING.md").write_text("Run tests before review.\n", encoding="utf-8")
            packet = render_review_packet(
                repo,
                base="origin/main",
                changed=[ChangedFile("src/app.py", "M")],
                stats=[Numstat("src/app.py", 10, 2)],
                config=PolicyConfig(required_checks=["nix flake check"]),
                findings=[Finding(BLOCKER, "missing-test-evidence", "No tests were provided.")],
            )
            self.assertIn("Themis Reviewer Packet", packet)
            self.assertIn("Status: **BLOCKED**", packet)
            self.assertIn("Do not spend deep review time yet", packet)
            self.assertIn("missing-test-evidence", packet)
            self.assertIn("exact passing command output", packet)

    def test_feedback_for_common_blockers(self) -> None:
        self.assertIn("AI assistance disclosure", feedback_for("missing-ai-disclosure"))
        self.assertIn("Signed-off-by", feedback_for("missing-signed-off-by"))
        self.assertIn("warning", feedback_for("upstream-ai-policy-present", "WARNING"))
        self.assertIn("No action required", feedback_for("clean-static-gate", "INFO"))


if __name__ == "__main__":
    unittest.main()
