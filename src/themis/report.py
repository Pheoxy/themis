from __future__ import annotations

from collections import Counter

from .policy import BLOCKER, Finding, ValidationInput


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
        "## Findings",
        "",
    ]
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
