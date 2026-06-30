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
    "deleted-test": FindingExplanation(
        "deleted-test",
        "A test file was deleted.",
        "Removing tests can reduce future regression coverage even when the current patch seems small.",
        "Restore the test, replace it with equivalent coverage, or document the upstream-approved reason it was removed.",
    ),
    "upstream-tests-not-proven": FindingExplanation(
        "upstream-tests-not-proven",
        "Upstream asks for tests, but the evidence does not prove a passing test/check command.",
        "Maintainers should not have to infer whether required validation ran and passed.",
        "Include a concrete passing command or CI job, such as `pytest passed` or `nix flake check passed`.",
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
    "upstream-forbids-ai": FindingExplanation(
        "upstream-forbids-ai",
        "Upstream docs appear to forbid AI-generated contributions.",
        "Themis fails closed when upstream policy appears stricter than the submitter's declared workflow.",
        "Do not submit AI-assisted work to that project unless maintainers explicitly approve an exception.",
    ),
    "upstream-ai-policy-present": FindingExplanation(
        "upstream-ai-policy-present",
        "Upstream docs mention AI disclosure policy.",
        "The submitter must make sure any human-authored or AI-assisted declaration is accurate for that upstream policy.",
        "Review the upstream AI policy and ensure the PR body truthfully discloses AI use or human authorship.",
    ),
    "missing-changelog-decision": FindingExplanation(
        "missing-changelog-decision",
        "Upstream appears to require changelog or release-note handling.",
        "Maintainers need to know whether user-visible changes are documented or intentionally exempt.",
        "Add/update the changelog or include an explicit PR note such as `Release notes: not needed` with the reason.",
    ),
    "missing-issue-link": FindingExplanation(
        "missing-issue-link",
        "Upstream appears to require an issue or reference link.",
        "Issue links preserve review context and help maintainers connect changes to accepted work.",
        "Add `Fixes #123`, `Refs #123`, or the upstream-approved issue/reference URL to the PR body.",
    ),
    "pr-template-not-acknowledged": FindingExplanation(
        "pr-template-not-acknowledged",
        "The upstream PR checklist was not acknowledged.",
        "Unchecked template items can hide missing tests, release notes, or contributor attestations.",
        "Complete the upstream PR template and check the relevant boxes truthfully before requesting review.",
    ),
    "cannot-verify-commit-style": FindingExplanation(
        "cannot-verify-commit-style",
        "Required commit style could not be verified.",
        "When upstream requires a commit convention, Themis needs the commit range to inspect subjects.",
        "Provide a correct base ref and ensure the relevant commits are present in the comparison range.",
    ),
    "invalid-commit-style": FindingExplanation(
        "invalid-commit-style",
        "One or more commits do not match the upstream commit style.",
        "Projects that require Conventional Commits rely on consistent subjects for changelog and release automation.",
        "Rewrite commit subjects to the required style, for example `fix(parser): handle empty input`.",
    ),
    "no-changes": FindingExplanation(
        "no-changes",
        "No changes were found to validate.",
        "A gate result without a patch cannot prove upstream readiness.",
        "Run Themis from the target repo with the intended commits, staged files, or working tree changes present.",
    ),
    "binary-change": FindingExplanation(
        "binary-change",
        "The patch contains a binary file change.",
        "Binary changes cannot be reviewed through normal textual diff inspection and may carry licensing or security risk.",
        "Remove the binary change or get explicit maintainer approval with provenance and verification details.",
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
    "ai-marker-in-diff": FindingExplanation(
        "ai-marker-in-diff",
        "The diff contains AI-tool marker text.",
        "Markers such as generated-by comments or assistant boilerplate suggest unreviewed output may have been copied directly.",
        "Remove tool marker text and ensure the submitted code is human-reviewed, project-appropriate, and disclosed accurately.",
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
    "clean-static-gate": FindingExplanation(
        "clean-static-gate",
        "No hard blockers were found by configured static checks.",
        "This is useful signal, but it is not a correctness guarantee or maintainer approval.",
        "Continue normal human review for correctness, design, security, licensing, and maintainability.",
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
