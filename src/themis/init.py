from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG = """[policy]
max_changed_files = 25
max_added_lines = 800
max_deleted_lines = 500
max_file_added_lines = 300
require_upstream_rules = true
require_tests_for_code = true
require_test_changes_for_code = true
block_generated_paths = true
block_vendor_paths = true
block_ai_markers = true
block_placeholders = true

required_checks = [
  "nix flake check",
]
"""

DEFAULT_BODY = """## Summary

Describe the change and why it belongs upstream.

## Evidence

Tests/checks run:

- `nix flake check`

AI assistance: State whether AI assistance was used and how all generated output was reviewed.

Human accountability: State that you take responsibility for every line, including tests, licensing, security, and project policy compliance.

Changelog: Updated / not needed because ...
"""


@dataclass(frozen=True)
class InitResult:
    written: list[Path]
    skipped: list[Path]


def init_repo(repo: Path, *, force: bool = False, include_pr_body: bool = True) -> InitResult:
    targets = [(repo / ".themis.toml", DEFAULT_CONFIG)]
    if include_pr_body:
        targets.append((repo / "pr-body.md", DEFAULT_BODY))

    written: list[Path] = []
    skipped: list[Path] = []
    for path, content in targets:
        if path.exists() and not force:
            skipped.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return InitResult(written=written, skipped=skipped)
