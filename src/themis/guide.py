from __future__ import annotations

from pathlib import Path
import re

from .git import ChangedFile, Numstat
from .policy import (
    BLOCKER,
    Finding,
    PolicyConfig,
    docs_require_changelog,
    docs_require_conventional_commits,
    docs_require_dco_or_signoff,
    docs_require_issue_link,
    is_process_rule_doc,
    is_source_path,
    is_test_path,
    load_rule_docs,
)


def render_guide(
    repo: Path,
    *,
    base: str | None,
    changed: list[ChangedFile],
    stats: list[Numstat],
    config: PolicyConfig,
    findings: list[Finding],
) -> str:
    rule_docs = load_rule_docs(repo)
    process_text = "\n".join(content for name, content in rule_docs if is_process_rule_doc(name))
    code_changes = [item.path for item in changed if is_source_path(item.path) and not is_test_path(item.path)]
    test_changes = [item.path for item in changed if is_test_path(item.path)]
    total_added = sum(item.added or 0 for item in stats)
    total_deleted = sum(item.deleted or 0 for item in stats)
    blockers = [finding for finding in findings if finding.severity == BLOCKER]
    status = "BLOCKED" if blockers else "PASS"

    lines = [
        "# Themis Upstream Assistant Guide",
        "",
        "Themis helps organize upstream procedure and still acts as a pass/fail gate. It does not take accountability for the change. The submitter still owns correctness, tests, security, licensing, and maintainability.",
        "",
        "## Gate Status",
        "",
        f"- Status: **{status}**",
        f"- Blockers: `{len(blockers)}`",
        f"- Warnings: `{sum(1 for finding in findings if finding.severity == 'WARNING')}`",
        "",
        "## Change Snapshot",
        "",
        f"- Repository: `{repo}`",
        f"- Base ref: `{base or 'HEAD'}`",
        f"- Changed files: `{len(changed)}`",
        f"- Added lines: `{total_added}`",
        f"- Deleted lines: `{total_deleted}`",
        f"- Code files changed: `{len(code_changes)}`",
        f"- Test files changed: `{len(test_changes)}`",
        "",
        "## Detected Rule Sources",
        "",
    ]

    if rule_docs:
        for name, _ in rule_docs:
            lines.append(f"- `{name}`")
    else:
        lines.append("- No contribution/rule documents detected. Themis validation will fail closed unless policy is changed.")

    if findings:
        lines.extend(["", "## Gate Findings", ""])
        for finding in findings:
            location = f" `{finding.file}`" if finding.file else ""
            lines.append(f"- **{finding.severity}** `{finding.code}`{location}: {finding.message}")

    lines.extend(["", "## Upstream Readiness Checklist", ""])
    for item in readiness_items(process_text, code_changes, test_changes, config):
        lines.append(f"- [ ] {item}")

    lines.extend(
        [
            "",
            "## Suggested Commands",
            "",
            "```bash",
            "themis validate --repo . --base origin/main --body-file pr-body.md --evidence \"nix flake check passed\" --run-checks",
            "themis pull-request draft --repo . --base origin/main --body-file pr-body.md --evidence \"nix flake check passed\"",
            "```",
            "",
            "## PR Body Sections To Prepare",
            "",
            "- Summary of the change and why it belongs upstream.",
            "- Exact test/check evidence with passing status.",
            "- `AI assistance:` disclosure when AI assistance was used.",
            "- `Human accountability:` statement from the submitter.",
            "- Changelog/release-note decision when relevant.",
            "",
        ]
    )
    return "\n".join(lines)


def readiness_items(process_text: str, code_changes: list[str], test_changes: list[str], config: PolicyConfig) -> list[str]:
    items = [
        "Read the detected upstream rule documents before submitting.",
        "Prepare a PR body with specific `AI assistance:` and `Human accountability:` sections when AI assistance was used.",
        "Collect exact passing evidence for checks and tests.",
    ]
    if config.required_checks:
        checks = ", ".join(f"`{command}`" for command in config.required_checks)
        items.append(f"Run configured required checks: {checks}.")
    if code_changes:
        items.append("Review every code change for maintainability, security, licensing, and project style.")
        if not test_changes:
            items.append("Add or update tests, or document a narrow project-approved reason tests are not changed.")
    if docs_require_dco_or_signoff(process_text):
        items.append("Ensure commits include `Signed-off-by:` trailers required by DCO/signoff policy.")
    if docs_require_changelog(process_text):
        items.append("Update changelog/release notes or document why no entry is needed.")
    if docs_require_issue_link(process_text):
        items.append("Link the required issue, ticket, or upstream reference in the PR body.")
    if docs_require_conventional_commits(process_text):
        items.append("Use the commit message format required by upstream, such as conventional commits.")
    return items
