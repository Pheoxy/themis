from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from example_repo import create_example_target_repo
from themis.doctor import run_doctor
from themis.policy import BLOCKER, Finding, PolicyConfig
from themis.providers import inspect_providers
from themis.rules import inspect_rules
from themis.self_check import SelfCheckResult, render_self_check_json, render_self_check_markdown, self_check_exit_code


class SelfCheckTests(unittest.TestCase):
    def test_self_check_passes_when_all_stages_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            with patch("themis.doctor.shutil.which", return_value="/bin/tool"):
                result = SelfCheckResult(
                    doctor=run_doctor(repo),
                    rules=inspect_rules(repo, PolicyConfig()),
                    providers=inspect_providers(repo),
                    findings=[],
                )
            self.assertEqual(self_check_exit_code(result), 0)
            self.assertIn("Status: **PASS**", render_self_check_markdown(result))

    def test_self_check_blocks_on_gate_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = create_example_target_repo(Path(raw))
            with patch("themis.doctor.shutil.which", return_value="/bin/tool"):
                result = SelfCheckResult(
                    doctor=run_doctor(repo),
                    rules=inspect_rules(repo, PolicyConfig()),
                    providers=inspect_providers(repo),
                    findings=[Finding(BLOCKER, "blocked", "Blocked for test.")],
                )
            payload = json.loads(render_self_check_json(result))
            self.assertEqual(self_check_exit_code(result), 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["stages"]["gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
