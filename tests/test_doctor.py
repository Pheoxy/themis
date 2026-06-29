from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_repo import create_example_target_repo, write
from themis.doctor import FAIL, PASS, WARN, doctor_exit_code, render_doctor_json, render_doctor_markdown, run_doctor


class DoctorTests(unittest.TestCase):
    def test_doctor_passes_ready_repo_with_required_tools(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            write(repo / ".themis.toml", '[policy]\nrequired_checks = ["nix flake check"]\n')
            with patch("themis.doctor.shutil.which", return_value="/bin/tool"):
                result = run_doctor(repo)

            statuses = {check.code: check.status for check in result.checks}
            self.assertEqual(statuses["git-repository"], PASS)
            self.assertEqual(statuses["policy-config"], PASS)
            self.assertEqual(statuses["upstream-rules"], PASS)
            self.assertEqual(statuses["tool-git"], PASS)
            self.assertEqual(statuses["tool-nix"], PASS)
            self.assertEqual(doctor_exit_code(result), 0)

    def test_doctor_fails_non_repo(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            result = run_doctor(Path(raw))
            self.assertEqual(result.checks[0].status, FAIL)
            self.assertEqual(doctor_exit_code(result), 2)

    def test_doctor_warns_when_config_missing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            with patch("themis.doctor.shutil.which", return_value="/bin/tool"):
                result = run_doctor(repo)
            statuses = {check.code: check.status for check in result.checks}
            self.assertEqual(statuses["policy-config"], WARN)

    def test_doctor_outputs_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            with patch("themis.doctor.shutil.which", return_value="/bin/tool"):
                result = run_doctor(repo)
            markdown = render_doctor_markdown(result)
            payload = json.loads(render_doctor_json(result))
            self.assertIn("Themis Doctor", markdown)
            self.assertEqual(payload["tool"], "themis")
            self.assertEqual(payload["workflow"], "doctor")

    def test_doctor_includes_provider_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            with patch("themis.doctor.shutil.which", return_value="/bin/tool"):
                result = run_doctor(repo)
            codes = {check.code for check in result.checks}
            self.assertIn("ai-provider-config", codes)
            self.assertIn("ai-provider-disabled", codes)


if __name__ == "__main__":
    unittest.main()
