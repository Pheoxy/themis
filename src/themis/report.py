from __future__ import annotations

from collections import Counter

from .policy import BLOCKER, Finding, ValidationInput


MAX_CHECK_OUTPUT_CHARS = 1200


def render_markdown(data: ValidationInput, findings: list[Finding]) -> str:
    counts = Counter(item.severity for item in findings)
    status = "BLOCKED" if counts[BLOCKER] else "PASS"
    lines = [
        "# Themis Upstream Validation Report",
        "",
        f"Status: **{status}**",
        "",
        "## Summary",
        "",
        f"- Repository: `{data.repo}`",
        f"- Base ref: `{data.base or 'HEAD'}`",
        f"- AI-assisted mode: `{str(data.ai_assisted).lower()}`",
        f"- Changed files: `{len(data.changed_files)}`",
        f"- Blockers: `{counts['BLOCKER']}`",
        f"- Warnings: `{counts['WARNING']}`",
        f"- Info: `{counts['INFO']}`",
        "",
        "## Changed Files",
        "",
    ]
    if data.changed_files:
        for item in data.changed_files:
            lines.append(f"- `{item.status}` `{item.path}`")
    else:
        lines.append("- No changed files detected.")

    lines.extend(["", "## Findings", ""])
    if findings:
        for finding in findings:
            location = f" `{finding.file}`" if finding.file else ""
            lines.append(f"- **{finding.severity}** `{finding.code}`{location}: {finding.message}")
            if finding.detail:
                lines.append(f"  Detail: `{finding.detail}`")
    else:
        lines.append("- No findings.")
    if data.check_results:
        lines.extend(["", "## Required Checks", ""])
        for result in data.check_results:
            outcome = "passed" if result.returncode == 0 else f"failed ({result.returncode})"
            lines.append(f"- `{result.command}`: {outcome}")
            snippet = check_output_snippet(result.output)
            if snippet:
                lines.extend(["", "```text", snippet, "```", ""])

    lines.extend(["", "## Next Actions", ""])
    if counts[BLOCKER]:
        lines.extend(
            [
                "- Resolve every blocker before asking maintainers for deep review.",
                "- Re-run Themis with exact passing test/check evidence after updating the patch.",
                "- Keep submitter accountability in the PR body; this report does not transfer responsibility.",
            ]
        )
    else:
        lines.extend(
            [
                "- Continue normal human review for correctness, security, licensing, maintainability, and upstream fit.",
                "- Preserve exact evidence for the commands or CI checks that passed.",
                "- Treat this as a gate result, not proof that the patch should be accepted.",
            ]
        )

    lines.extend(
        [
            "",
            "## Validator Caveat",
            "",
            "This report is a gate, not a guarantee. Passing means Themis did not find configured hard blockers; it does not certify correctness, safety, licensing, maintainability, or upstream acceptance. Accountability remains with the submitter and the project's review process.",
            "",
        ]
    )
    return "\n".join(lines)


def check_output_snippet(output: str) -> str:
    snippet = output.strip()
    if not snippet:
        return ""
    if len(snippet) > MAX_CHECK_OUTPUT_CHARS:
        snippet = f"{snippet[:MAX_CHECK_OUTPUT_CHARS].rstrip()}\n..."
    return snippet.replace("```", "` ` `")
