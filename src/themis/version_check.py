from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import tomllib


@dataclass(frozen=True)
class ReleaseFileCheck:
    path: str
    status: str
    message: str


@dataclass(frozen=True)
class ReleaseMetadataCheck:
    field: str
    status: str
    message: str


@dataclass(frozen=True)
class VersionCheckResult:
    pyproject: str
    package: str
    flake: str
    files: list[ReleaseFileCheck]
    metadata: list[ReleaseMetadataCheck]


def inspect_versions(repo: Path) -> VersionCheckResult:
    pyproject_data = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    pyproject = pyproject_data["project"]["version"]
    package_match = re.search(r'__version__\s*=\s*"([^"]+)"', (repo / "src" / "themis" / "__init__.py").read_text(encoding="utf-8"))
    if not package_match:
        raise ValueError("could not find package __version__")
    flake_match = re.search(r'version\s*=\s*"([^"]+)";', (repo / "flake.nix").read_text(encoding="utf-8"))
    if not flake_match:
        raise ValueError("could not find flake package version")
    return VersionCheckResult(
        pyproject=pyproject,
        package=package_match.group(1),
        flake=flake_match.group(1),
        files=inspect_release_files(repo),
        metadata=inspect_release_metadata(pyproject_data),
    )


def inspect_release_files(repo: Path) -> list[ReleaseFileCheck]:
    checks: list[ReleaseFileCheck] = []
    for relative in ("README.md", "CHANGELOG.md", "LICENSE"):
        path = repo / relative
        if path.exists() and path.read_text(encoding="utf-8", errors="replace").strip():
            checks.append(ReleaseFileCheck(relative, "PASS", "Release file is present."))
        else:
            checks.append(ReleaseFileCheck(relative, "FAIL", "Release file is missing or empty."))
    return checks


def inspect_release_metadata(pyproject_data: dict) -> list[ReleaseMetadataCheck]:
    project = pyproject_data.get("project", {})
    checks: list[ReleaseMetadataCheck] = []
    for field in ("name", "description", "readme", "license"):
        if project.get(field):
            checks.append(ReleaseMetadataCheck(field, "PASS", "Project metadata field is set."))
        else:
            checks.append(ReleaseMetadataCheck(field, "FAIL", "Project metadata field is missing."))
    for name, url in project.get("urls", {}).items():
        text = str(url)
        if "OWNER/" in text or "example.com" in text:
            checks.append(ReleaseMetadataCheck(f"project.urls.{name}", "FAIL", "Project URL still contains an unresolved template value."))
        else:
            checks.append(ReleaseMetadataCheck(f"project.urls.{name}", "PASS", "Project URL is concrete."))
    return checks


def version_check_exit_code(result: VersionCheckResult) -> int:
    versions_match = len({result.pyproject, result.package, result.flake}) == 1
    files_pass = all(check.status == "PASS" for check in result.files)
    metadata_pass = all(check.status == "PASS" for check in result.metadata)
    return 0 if versions_match and files_pass and metadata_pass else 2


def render_version_check_markdown(result: VersionCheckResult) -> str:
    status = "PASS" if version_check_exit_code(result) == 0 else "BLOCKED"
    lines = [
        "# Themis Release Check",
        "",
        f"Status: **{status}**",
        "",
        "## Versions",
        "",
        f"- `pyproject.toml`: `{result.pyproject}`",
        f"- `src/themis/__init__.py`: `{result.package}`",
        f"- `flake.nix`: `{result.flake}`",
        "",
        "## Release Files",
        "",
    ]
    for check in result.files:
        lines.append(f"- **{check.status}** `{check.path}`: {check.message}")
    lines.extend(["", "## Project Metadata", ""])
    for check in result.metadata:
        lines.append(f"- **{check.status}** `{check.field}`: {check.message}")
    lines.append("")
    if version_check_exit_code(result):
        lines.extend(
            [
                "## Next",
                "",
                "- Update all version declarations to the same value before release.",
                "- Add any missing release files before publishing artifacts.",
                "- Replace unresolved package metadata before publishing artifacts.",
                "",
            ]
        )
    return "\n".join(lines)


def render_version_check_json(result: VersionCheckResult) -> str:
    payload = {
        "tool": "themis",
        "workflow": "release check",
        "status": "pass" if version_check_exit_code(result) == 0 else "blocked",
        "exit_code": version_check_exit_code(result),
        "files": [asdict(check) for check in result.files],
        "metadata": [asdict(check) for check in result.metadata],
        "versions": {
            "pyproject": result.pyproject,
            "package": result.package,
            "flake": result.flake,
        },
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
