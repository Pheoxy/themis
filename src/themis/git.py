from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


class GitError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChangedFile:
    path: str
    status: str


@dataclass(frozen=True)
class Numstat:
    path: str
    added: int | None
    deleted: int | None


@dataclass(frozen=True)
class CommitInfo:
    sha: str
    subject: str
    body: str


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise GitError(message)
    return result.stdout


def repo_root(repo: Path) -> Path:
    output = git(repo, "rev-parse", "--show-toplevel")
    return Path(output.strip()).resolve()


def diff_args(base: str | None) -> list[str]:
    if base:
        return [f"{base}...HEAD"]
    return ["HEAD"]


def parse_name_status(output: str) -> list[ChangedFile]:
    changed: list[ChangedFile] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]
        changed.append(ChangedFile(path=path, status=status))
    return changed


def changed_files(repo: Path, base: str | None) -> list[ChangedFile]:
    seen: dict[str, ChangedFile] = {}
    committed = git(repo, "diff", "--name-status", "--find-renames", *diff_args(base), check=False)
    for item in parse_name_status(committed):
        seen[item.path] = item

    staged = git(repo, "diff", "--name-status", "--find-renames", "--cached", check=False)
    unstaged = git(repo, "diff", "--name-status", "--find-renames", check=False)
    for output in (staged, unstaged):
        for item in parse_name_status(output):
            seen[item.path] = item

    untracked = git(repo, "ls-files", "--others", "--exclude-standard", check=False)
    for path in untracked.splitlines():
        if path.strip():
            seen[path] = ChangedFile(path=path, status="??")

    return sorted(seen.values(), key=lambda item: item.path)


def diff_text(repo: Path, base: str | None) -> str:
    chunks = [git(repo, "diff", "--unified=0", *diff_args(base), check=False)]
    staged = git(repo, "diff", "--unified=0", "--cached", check=False)
    unstaged = git(repo, "diff", "--unified=0", check=False)
    if staged:
        chunks.append(staged)
    if unstaged:
        chunks.append(unstaged)
    return "\n".join(chunk for chunk in chunks if chunk)


def numstat(repo: Path, base: str | None) -> list[Numstat]:
    output = git(repo, "diff", "--numstat", *diff_args(base), check=False)
    stats: list[Numstat] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added = None if parts[0] == "-" else int(parts[0])
        deleted = None if parts[1] == "-" else int(parts[1])
        stats.append(Numstat(path=parts[-1], added=added, deleted=deleted))
    return stats


def tracked_files(repo: Path) -> list[str]:
    return [line for line in git(repo, "ls-files", check=False).splitlines() if line.strip()]


def commits(repo: Path, base: str | None) -> list[CommitInfo]:
    if not base:
        return []
    fmt = "%H%x1f%s%x1f%b%x1e"
    output = git(repo, "log", f"{base}..HEAD", f"--pretty=format:{fmt}", check=False)
    parsed: list[CommitInfo] = []
    for record in output.strip("\x1e\n").split("\x1e"):
        if not record.strip():
            continue
        parts = record.strip("\n").split("\x1f", 2)
        if len(parts) != 3:
            continue
        parsed.append(CommitInfo(sha=parts[0], subject=parts[1], body=parts[2]))
    return parsed


def current_branch(repo: Path) -> str:
    return git(repo, "branch", "--show-current").strip()


def last_commit_subject(repo: Path) -> str:
    return git(repo, "log", "-1", "--pretty=%s").strip()
