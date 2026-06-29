from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FindingExplanation:
    code: str
    summary: str
    why: str
    fix: str


EXPLANATIONS = {
    "missing-ai-disclosure": FindingExplanation(
        "missing-ai-disclosure",
        "AI-assisted work did not disclose AI assistance.",
        "Many upstream projects require explicit AI-use disclosure so maintainers can judge provenance and review risk.",
        "Add an `AI assistance:` section that explains which tools were used and how the output was reviewed.",
    ),
    "weak-ai-disclosure": FindingExplanation(
        "weak-ai-disclosure",
        "AI disclosure is present but not specific enough.",
        "Placeholders such as `used` or `yes` do not help maintainers understand provenance or review effort.",
        "Replace it with a concrete explanation of tool use, manual review, edits, and checks performed.",
    ),
    "missing-human-accountability": FindingExplanation(
        "missing-human-accountability",
        "The PR body lacks a human accountability statement.",
        "Themis never takes responsibility for a change, and neither does an AI tool. A human submitter must own the work.",
        "Add `Human accountability:` stating that the submitter takes responsibility for tests, licensing, security, and maintainability.",
    ),
    "weak-human-accountability": FindingExplanation(
        "weak-human-accountability",
        "The accountability statement is too vague.",
        "Maintainers need explicit ownership, not a checkbox or token acknowledgement.",
        "State that the submitter, not Themis or an AI tool, takes responsibility for the submitted work.",
    ),
    "missing-test-evidence": FindingExplanation(
        "missing-test-evidence",
        "Code changed without passing test/check evidence.",
        "Unverified code shifts basic validation work onto maintainers.",
        "Run the relevant checks and include exact passing command output or CI links.",
    ),
    "weak-test-evidence": FindingExplanation(
        "weak-test-evidence",
        "Test evidence is vague or unverifiable.",
        "Claims like `looks good` do not prove what ran or whether it passed.",
        "Name the command or CI job and state that it passed, for example `nix flake check passed`.",
    ),
    "missing-test-changes": FindingExplanation(
        "missing-test-changes",
        "Code changed without test changes.",
        "Behavior changes need tests so future maintainers can keep the project stable.",
        "Add or update tests, or document a narrow upstream-approved reason tests are not needed.",
    ),
    "required-checks-not-run": FindingExplanation(
        "required-checks-not-run",
        "Configured required checks were not run by Themis.",
        "Project-required commands should not be replaced by vague claims.",
        "Use `themis validate --run-checks`, `themis guide --run-checks`, or `themis pull-request draft`.",
    ),
    "required-check-failed": FindingExplanation(
        "required-check-failed",
        "A configured required check failed.",
        "Failing upstream-required checks are hard blockers before maintainer review.",
        "Fix the failing command locally or in CI, then re-run Themis.",
    ),
    "missing-upstream-rules": FindingExplanation(
        "missing-upstream-rules",
        "No upstream rule documents were found.",
        "Themis fails closed instead of guessing a project's contribution process.",
        "Add or point Themis at contribution rules, or configure the target repository policy explicitly.",
    ),
    "cannot-verify-dco": FindingExplanation(
        "cannot-verify-dco",
        "DCO/signoff requirements could not be verified.",
        "When upstream requires signoff, Themis must prove the commit range satisfies it.",
        "Provide the correct base ref and ensure relevant commits include `Signed-off-by:` trailers.",
    ),
    "missing-signed-off-by": FindingExplanation(
        "missing-signed-off-by",
        "One or more commits lack required signoff trailers.",
        "DCO/signoff documents contributor responsibility for the submitted work.",
        "Add `Signed-off-by:` trailers according to the target project's process.",
    ),
    "generated-path": FindingExplanation(
        "generated-path",
        "Generated/build/minified output changed.",
        "Generated churn is hard to review and can hide unwanted changes.",
        "Remove generated output or add a narrow, project-approved allowlist entry.",
    ),
    "vendor-path": FindingExplanation(
        "vendor-path",
        "Vendored or third-party paths changed.",
        "Third-party code has provenance, licensing, and review implications.",
        "Remove vendor changes or document the upstream-approved vendor update process.",
    ),
    "secret-looking-value": FindingExplanation(
        "secret-looking-value",
        "The diff appears to contain a secret or credential.",
        "Secrets in PRs can cause immediate security incidents and require rotation.",
        "Remove the secret, rotate it if real, and use secure configuration or secret storage.",
    ),
    "placeholder-in-code": FindingExplanation(
        "placeholder-in-code",
        "Code contains placeholder or cleanup language.",
        "Placeholder code signals unfinished work and pushes cleanup onto maintainers.",
        "Finish the implementation or remove the placeholder before asking for review.",
    ),
    "debug-leftover": FindingExplanation(
        "debug-leftover",
        "Debugging code appears to be left in the patch.",
        "Debug leftovers can leak data, spam logs, or alter runtime behavior.",
        "Remove debugging statements unless the target project explicitly wants them.",
    ),
    "swallowed-exception": FindingExplanation(
        "swallowed-exception",
        "A broad exception appears to be swallowed.",
        "Silent failures hide bugs and make maintenance harder.",
        "Handle a specific exception, propagate it, or log/report the failure appropriately.",
    ),
}


def explain_code(code: str) -> FindingExplanation:
    if code in EXPLANATIONS:
        return EXPLANATIONS[code]
    if code.startswith("too-many") or code.endswith("too-large"):
        return FindingExplanation(
            code,
            "The patch is too broad for the configured review limits.",
            "Large patches are harder to review and more likely to hide unrelated changes.",
            "Split the change into smaller upstreamable pieces or adjust policy with maintainer approval.",
        )
    return FindingExplanation(
        code,
        "No specific explanation is registered for this finding code.",
        "The finding still came from the active Themis gate and should be resolved before review.",
        "Read the finding message, inspect target repository rules, fix the issue, and re-run Themis.",
    )


def remediation_for(code: str, severity: str) -> str:
    if severity == "INFO":
        return "No action required unless normal human review finds a concern."
    if severity == "WARNING":
        return "Review this warning against the target repository rules before approval."
    return explain_code(code).fix


def render_explanation(code: str | None = None) -> str:
    if code:
        item = explain_code(code)
        return "\n".join(
            [
                f"# Themis Finding: `{item.code}`",
                "",
                f"Summary: {item.summary}",
                "",
                f"Why it matters: {item.why}",
                "",
                f"What to do: {item.fix}",
                "",
                "Themis explains the gate result, but the submitter remains accountable for the change.",
                "",
            ]
        )
    lines = ["# Themis Finding Catalog", ""]
    for item in sorted(EXPLANATIONS.values(), key=lambda value: value.code):
        lines.append(f"- `{item.code}`: {item.summary}")
    lines.append("")
    return "\n".join(lines)
