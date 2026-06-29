from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.version_check import VersionCheckResult, inspect_versions, render_version_check_json, render_version_check_markdown, version_check_exit_code


class VersionCheckTests(unittest.TestCase):
    def test_version_check_passes_current_repo(self) -> None:
        result = inspect_versions(Path(__file__).resolve().parents[1])
        self.assertEqual(result.pyproject, result.package)
        self.assertEqual(result.pyproject, result.flake)
        self.assertEqual(version_check_exit_code(result), 0)

    def test_version_check_blocks_mismatched_versions(self) -> None:
        result = VersionCheckResult(pyproject="1.0.0", package="1.0.1", flake="1.0.0")
        self.assertEqual(version_check_exit_code(result), 2)
        self.assertIn("BLOCKED", render_version_check_markdown(result))

    def test_version_check_json_output(self) -> None:
        payload = json.loads(render_version_check_json(VersionCheckResult("1.0.0", "1.0.0", "1.0.0")))
        self.assertEqual(payload["workflow"], "release check")
        self.assertEqual(payload["status"], "pass")

    def test_inspect_versions_reads_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "src" / "themis").mkdir(parents=True)
            (repo / "pyproject.toml").write_text('[project]\nversion = "2.0.0"\n', encoding="utf-8")
            (repo / "src" / "themis" / "__init__.py").write_text('__version__ = "2.0.0"\n', encoding="utf-8")
            (repo / "flake.nix").write_text('version = "2.0.0";\n', encoding="utf-8")
            self.assertEqual(inspect_versions(repo), VersionCheckResult("2.0.0", "2.0.0", "2.0.0"))


if __name__ == "__main__":
    unittest.main()
