from __future__ import annotations

from pathlib import Path
import subprocess


def create_example_target_repo(parent: Path) -> Path:
    repo = parent / "target"
    repo.mkdir()
    run_git(repo, "init")
    write(repo / "CONTRIBUTING.md", "Run tests before submitting code changes.\n")
    write(repo / "src" / "app.py", "def value():\n    return 1\n")
    write(repo / "tests" / "test_app.py", "from src.app import value\n\n\ndef test_value():\n    assert value() == 1\n")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "Initial target repo")
    return repo


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Themis Tests",
            "-c",
            "user.email=themis@example.invalid",
            *args,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
