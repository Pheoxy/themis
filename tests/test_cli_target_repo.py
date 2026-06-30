from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

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

    def test_validate_does_not_call_enabled_provider(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(
                repo / ".themis.toml",
                '[policy]\nrequire_test_changes_for_code = false\n\n[ai]\nenabled = true\nprovider = "custom"\nmodel = "must-not-run"\ncommand_env = "THEMIS_PROVIDER_COMMAND"\nallowed_workflows = ["guide"]\n',
            )
            write(repo / "src" / "app.py", "def value():\n    return 2\n")
            body = Path(raw) / "pr-body.md"
            body.write_text("Human-authored maintenance change.\n", encoding="utf-8")
            report = Path(raw) / "report.json"
            command = f"{sys.executable} -c \"raise SystemExit('provider must not run')\""

            with patch.dict(os.environ, {"THEMIS_PROVIDER_COMMAND": command}, clear=False):
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
                        "--format",
                        "json",
                        "--output",
                        str(report),
                    ]
                )

            output = report.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('"status": "pass"', output)
            self.assertNotIn("provider must not run", output)


if __name__ == "__main__":
    unittest.main()
