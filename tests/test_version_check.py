from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.version_check import inspect_versions, render_version_check_json, render_version_check_markdown, version_check_exit_code


class VersionCheckTests(unittest.TestCase):
    def test_current_repo_versions_are_current_release(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        result = inspect_versions(repo)
        self.assertEqual(result.pyproject, "1.0.1")
        self.assertEqual(result.package, "1.0.1")
        self.assertEqual(result.flake, "1.0.1")

    def test_release_check_passes_with_matching_versions_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = make_release_repo(Path(raw))
            result = inspect_versions(repo)
            self.assertEqual(version_check_exit_code(result), 0)
            self.assertTrue(all(check.status == "PASS" for check in result.files))
            self.assertTrue(all(check.status == "PASS" for check in result.metadata))

    def test_release_check_blocks_missing_release_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = make_release_repo(Path(raw))
            (repo / "LICENSE").unlink()
            result = inspect_versions(repo)
            self.assertEqual(version_check_exit_code(result), 2)
            self.assertIn("LICENSE", {check.path for check in result.files if check.status == "FAIL"})

    def test_release_check_outputs_file_checks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = make_release_repo(Path(raw))
            result = inspect_versions(repo)
            markdown = render_version_check_markdown(result)
            payload = json.loads(render_version_check_json(result))
            self.assertIn("Release Files", markdown)
            self.assertIn("Project Metadata", markdown)
            self.assertEqual(payload["files"][0]["status"], "PASS")
            self.assertIn("files", payload)
            self.assertIn("metadata", payload)

    def test_current_project_urls_are_concrete(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        result = inspect_versions(repo)
        url_checks = [check for check in result.metadata if check.field.startswith("project.urls.")]
        self.assertGreaterEqual(len(url_checks), 4)
        self.assertTrue(all(check.status == "PASS" for check in url_checks))

    def test_release_check_blocks_placeholder_project_urls(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = make_release_repo(Path(raw))
            pyproject = repo / "pyproject.toml"
            pyproject.write_text(
                pyproject.read_text(encoding="utf-8").replace(
                    'Homepage = "https://github.com/Pheoxy/themis"',
                    'Homepage = "https://github.com/OWNER/themis"',
                ),
                encoding="utf-8",
            )
            result = inspect_versions(repo)
            self.assertEqual(version_check_exit_code(result), 2)
            self.assertIn("project.urls.Homepage", {check.field for check in result.metadata if check.status == "FAIL"})


def make_release_repo(parent: Path) -> Path:
    repo = parent / "repo"
    (repo / "src" / "themis").mkdir(parents=True)
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "themis"\nversion = "1.2.3"\ndescription = "Release test"\nreadme = "README.md"\nlicense = { text = "Apache-2.0" }\n\n[project.urls]\nHomepage = "https://github.com/Pheoxy/themis"\nSource = "https://github.com/Pheoxy/themis"\nIssues = "https://github.com/Pheoxy/themis/issues"\nDocumentation = "https://github.com/Pheoxy/themis/tree/main/docs"\n',
        encoding="utf-8",
    )
    (repo / "src" / "themis" / "__init__.py").write_text('__version__ = "1.2.3"\n', encoding="utf-8")
    (repo / "flake.nix").write_text('version = "1.2.3";\n', encoding="utf-8")
    (repo / "README.md").write_text("# Project\n", encoding="utf-8")
    (repo / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (repo / "LICENSE").write_text("Apache License\n", encoding="utf-8")
    return repo


if __name__ == "__main__":
    unittest.main()
