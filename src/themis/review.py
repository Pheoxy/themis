from __future__ import annotations

from pathlib import Path

from .git import ChangedFile, Numstat
from .policy import BLOCKER, WARNING, Finding, PolicyConfig, is_source_path, is_test_path, load_rule_docs


def render_review_packet(
    repo: Path,
    *,
    base: str | None,
    changed: list[ChangedFile],
    stats: list[Numstat],
    config: PolicyConfig,
    findings: list[Finding],
) -> str:
    blockers = [finding for finding in findings if finding.severity == BLOCKER]
    warnings = [finding for finding in findings if finding.severity == WARNING]
    status = "BLOCKED" if blockers else "PASS"
    code_changes = [item.path for item in changed if is_source_path(item.path) and not is_test_path(item.path)]
    test_changes = [item.path for item in changed if is_test_path(item.path)]
    total_added = sum(item.added or 0 for item in stats)
    total_deleted = sum(item.deleted or 0 for item in stats)
    rule_docs = load_rule_docs(repo)

    lines = [
        "# Themis Reviewer Packet",
        "",
        "Themis helps reviewers and maintainers reduce repeat process work. This packet is still a pass/fail gate result, not a substitute for human review or contributor accountability.",
        "",
        "## Gate Result",
        "",
        f"- Status: **{status}**",
        f"- Blockers: `{len(blockers)}`",
        f"- Warnings: `{len(warnings)}`",
        f"- Base ref: `{base or 'HEAD'}`",
        "",
        "## Review Load Snapshot",
        "",
        f"- Changed files: `{len(changed)}`",
        f"- Added lines: `{total_added}`",
        f"- Deleted lines: `{total_deleted}`",
        f"- Code files changed: `{len(code_changes)}`",
        f"- Test files changed: `{len(test_changes)}`",
        f"- Rule documents detected: `{len(rule_docs)}`",
        "",
    ]

    lines.extend(render_action_section(blockers, warnings))
    lines.extend(render_feedback_section(findings))
    lines.extend(render_reviewer_questions(code_changes, test_changes, config))
    return "\n".join(lines)


def render_action_section(blockers: list[Finding], warnings: list[Finding]) -> list[str]:
    if blockers:
        return [
            "## Maintainer Action",
            "",
            "- Do not spend deep review time yet; send the blocker list back to the contributor.",
            "- Ask for exact evidence, rule compliance, and ownership statements before reviewing implementation details.",
            "- Re-run Themis after the contributor updates the PR.",
            "",
        ]
    if warnings:
        return [
            "## Maintainer Action",
            "",
            "- Gate blockers are clear, but review the warnings before approval.",
            "- Continue normal project review for correctness, design, security, and maintainability.",
            "",
        ]
    return [
        "## Maintainer Action",
        "",
        "- Gate blockers are clear; proceed with normal project review.",
        "- Passing Themis does not certify the patch or transfer accountability.",
        "",
    ]


def render_feedback_section(findings: list[Finding]) -> list[str]:
    lines = ["## Contributor Feedback", ""]
    if not findings:
        lines.append("- No Themis findings. Continue normal review.")
        lines.append("")
        return lines
    for finding in findings:
        location = f" `{finding.file}`" if finding.file else ""
        lines.append(f"- **{finding.severity}** `{finding.code}`{location}: {finding.message}")
        lines.append(f"  Ask: {feedback_for(finding.code, finding.severity)}")
    lines.append("")
    return lines


def render_reviewer_questions(code_changes: list[str], test_changes: list[str], config: PolicyConfig) -> list[str]:
    lines = ["## Suggested Reviewer Questions", ""]
    lines.append("- Does the change match the target project's documented scope and style?")
    lines.append("- Is the contributor's test/check evidence exact enough to reproduce?")
    if code_changes and not test_changes:
        lines.append("- Why are there code changes without matching test changes?")
    if config.required_checks:
        lines.append("- Did every configured required check run in the same context as the submitted patch?")
    lines.append("- Are there licensing, security, generated-code, or vendored-code concerns that Themis cannot prove automatically?")
    lines.append("")
    return lines


def feedback_for(code: str, severity: str = BLOCKER) -> str:
    if code.startswith("missing-ai") or code.startswith("weak-ai"):
        return "Add a specific AI assistance disclosure explaining tool use and human review."
    if "accountability" in code:
        return "State that the submitter owns the work; Themis and AI tools do not."
    if "test" in code or "check" in code:
        return "Provide exact passing command output or CI evidence."
    if "changelog" in code:
        return "Update release notes or explain why no entry is needed."
    if "signed-off" in code or "dco" in code:
        return "Add required Signed-off-by trailers or fix the commit range."
    if "generated" in code or "vendor" in code:
        return "Remove generated/vendor noise or provide an explicit project-approved exception."
    if severity == WARNING:
        return "Review this warning against the target repository rules before approval."
    return "Resolve this blocker according to the target repository rules, then re-run Themis."
