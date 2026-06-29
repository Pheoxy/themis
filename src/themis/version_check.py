from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import tomllib


@dataclass(frozen=True)
class VersionCheckResult:
    pyproject: str
    package: str
    flake: str


def inspect_versions(repo: Path) -> VersionCheckResult:
    pyproject = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    package_match = re.search(r'__version__\s*=\s*"([^"]+)"', (repo / "src" / "themis" / "__init__.py").read_text(encoding="utf-8"))
    if not package_match:
        raise ValueError("could not find package __version__")
    flake_match = re.search(r'version\s*=\s*"([^"]+)";', (repo / "flake.nix").read_text(encoding="utf-8"))
    if not flake_match:
        raise ValueError("could not find flake package version")
    return VersionCheckResult(pyproject=pyproject, package=package_match.group(1), flake=flake_match.group(1))


def version_check_exit_code(result: VersionCheckResult) -> int:
    return 0 if len({result.pyproject, result.package, result.flake}) == 1 else 2


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
    ]
    if version_check_exit_code(result):
        lines.extend(
            [
                "## Next",
                "",
                "- Update all version declarations to the same value before release.",
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
        "versions": asdict(result),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
