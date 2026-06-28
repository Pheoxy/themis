from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile


class DraftPrError(RuntimeError):
    pass


@dataclass(frozen=True)
class DraftPrOptions:
    title: str
    base: str
    head: str | None
    body: str


def create_draft_pr(repo: Path, options: DraftPrOptions) -> str:
    if not options.title.strip():
        raise DraftPrError("draft PR title is required")
    if not options.base.strip():
        raise DraftPrError("draft PR base branch is required")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as body_file:
        body_file.write(options.body)
        body_path = body_file.name

    command = [
        "gh",
        "pr",
        "create",
        "--draft",
        "--base",
        options.base,
        "--title",
        options.title,
        "--body-file",
        body_path,
    ]
    if options.head:
        command.extend(["--head", options.head])

    result = subprocess.run(
        command,
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "gh pr create failed"
        raise DraftPrError(message)
    return result.stdout.strip()


def infer_pr_base(base_ref: str | None) -> str:
    if not base_ref:
        return ""
    ref = base_ref.split("...", 1)[0]
    for prefix in ("refs/remotes/", "remotes/", "origin/"):
        if ref.startswith(prefix):
            return ref.removeprefix(prefix)
    return ref


def build_pr_body(pr_description: str, report: str) -> str:
    intro = pr_description.strip()
    validation = f"## Upstream Validator Report\n\n{report.strip()}"
    if not intro:
        return validation + "\n"
    return f"{intro}\n\n---\n\n{validation}\n"
