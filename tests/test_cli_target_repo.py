from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_repo import create_example_target_repo, write
from themis.cli import main


class CliTargetRepoTests(unittest.TestCase):
    def test_validate_reports_real_target_repo_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / "src" / "app.py", "def value():\n    return 2\n")
            body = Path(raw) / "pr-body.md"
            body.write_text("Human-authored maintenance change.\n", encoding="utf-8")
            report = Path(raw) / "report.md"

            exit_code = main(
                [
                    "validate",
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD",
                    "--human",
                    "--body-file",
                    str(body),
                    "--evidence",
                    "pytest passed",
                    "--output",
                    str(report),
                ]
            )

            output = report.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 2)
            self.assertIn("Status: **BLOCKED**", output)
            self.assertIn("missing-test-changes", output)
            self.assertIn("- `M` `src/app.py`", output)


if __name__ == "__main__":
    unittest.main()
