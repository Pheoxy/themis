from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.release_audit import audit_exit_code, inspect_release_audit, render_audit_json, render_audit_markdown
from themis.release_audit import approved_secret_fixtures


class ReleaseAuditTests(unittest.TestCase):
    def test_current_repo_audit_blocks_known_pre_1_0_gaps_without_secret_values(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        result = inspect_release_audit(repo)
        checks = {check.code: check for check in result.checks}
        self.assertEqual(audit_exit_code(result), 0)
        self.assertEqual(checks["template-references"].status, "PASS")
        self.assertEqual(checks["asset-provenance"].status, "PASS")
        self.assertEqual(checks["asset-size"].status, "PASS")
        self.assertEqual(checks["tracked-secret-fixtures"].status, "PASS")
        self.assertNotIn("supersecretvalue", render_audit_markdown(result))

    def test_approved_secret_fixtures_are_documented(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        fixtures = approved_secret_fixtures(repo)
        self.assertEqual(
            fixtures,
            {
                "generic-secret-assignment:tests/test_providers.py:122",
                "generic-secret-assignment:tests/test_providers.py:130",
                "generic-secret-assignment:tests/test_providers.py:141",
            },
        )

    def test_large_asset_without_explicit_approval_warns(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            run(repo, "git", "init")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "Test User")
            (repo / "docs" / "assets").mkdir(parents=True)
            (repo / "LICENSE").write_text("Apache License\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text('[project]\nlicense = { text = "Apache-2.0" }\n', encoding="utf-8")
            (repo / "docs" / "assets" / "large.png").write_bytes(b"0" * 1_000_001)
            (repo / "docs" / "assets" / "PROVENANCE.md").write_text(
                "Generated with ChatGPT and OpenAI. Distributed under the Apache License. "
                "These assets are not represented as human-created.\n",
                encoding="utf-8",
            )
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "init")
            result = inspect_release_audit(repo)
            checks = {check.code: check for check in result.checks}
            self.assertEqual(checks["asset-size"].status, "WARN")
            self.assertIn("large.png", checks["asset-size"].detail or "")

    def test_release_audit_passes_minimal_clean_repo(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            run(repo, "git", "init")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "Test User")
            (repo / "LICENSE").write_text("Apache License\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text('[project]\nlicense = { text = "Apache-2.0" }\n', encoding="utf-8")
            (repo / "README.md").write_text("# Clean\n", encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "init")
            result = inspect_release_audit(repo, include_history=True)
            self.assertEqual(audit_exit_code(result), 0)
            self.assertIn("Status: **PASS**", render_audit_markdown(result))
            self.assertEqual(json.loads(render_audit_json(result))["status"], "pass")

    def test_release_audit_blocks_tracked_secret_like_value(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            run(repo, "git", "init")
            run(repo, "git", "config", "user.email", "test@example.invalid")
            run(repo, "git", "config", "user.name", "Test User")
            (repo / "LICENSE").write_text("Apache License\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text('[project]\nlicense = { text = "Apache-2.0" }\n', encoding="utf-8")
            secret_fixture = "api_" + "key = " + "abcdefghijklmnopqrstuvwxyz" + "\n"
            (repo / "settings.txt").write_text(secret_fixture, encoding="utf-8")
            run(repo, "git", "add", ".")
            run(repo, "git", "commit", "-m", "init")
            result = inspect_release_audit(repo)
            checks = {check.code: check for check in result.checks}
            self.assertEqual(checks["tracked-secret-patterns"].status, "FAIL")
            self.assertNotIn("abcdefghijklmnopqrstuvwxyz", render_audit_markdown(result))

    def test_history_audit_fails_cleanly_outside_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "LICENSE").write_text("Apache License\n", encoding="utf-8")
            (repo / "pyproject.toml").write_text('[project]\nlicense = { text = "Apache-2.0" }\n', encoding="utf-8")
            result = inspect_release_audit(repo, include_history=True)
            checks = {check.code: check for check in result.checks}
            self.assertEqual(audit_exit_code(result), 2)
            self.assertEqual(checks["history-secret-scan"].status, "FAIL")
            self.assertIn("requires a git repository", checks["history-secret-scan"].message)


def run(repo: Path, *args: str) -> None:
    import subprocess

    subprocess.run(args, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)


if __name__ == "__main__":
    unittest.main()
