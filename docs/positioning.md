# Positioning

Themis is a pre-upstream contribution readiness gate. It is not a general-purpose security scanner, linter, test runner, code review bot, or AI reviewer.

Its job is narrower: make contributors prove that a patch is ready for maintainer review before maintainer time is spent.

## Primary Niche

Themis is strongest when a project receives pull requests that may be:

- AI-assisted but weakly disclosed.
- Under-tested or vaguely tested.
- Missing upstream process requirements.
- Too broad for easy review.
- Mixed with generated, vendor, binary, or build-output noise.
- Missing accountability language.
- Hard for maintainers to triage quickly.

Themis turns those conditions into explicit blockers, warnings, and next actions.

## Compared To Linters And Formatters

Linters and formatters check code style and local quality rules. Themis checks contribution readiness and process evidence.

Use both. Themis can run project checks through `required_checks`, but it should not replace project-specific linters or formatters.

## Compared To Security Scanners

Security scanners look for vulnerabilities, dependency risks, secrets, or unsafe code patterns. Themis has a small set of secret-like and suspicious-diff blockers, but it is not a security scanner.

Use dedicated tools for dependency scanning, SAST, secret scanning, container scanning, and supply-chain analysis.

## Compared To CI

CI proves commands ran in a controlled environment. Themis asks whether the contributor supplied enough evidence and whether required commands passed.

Themis can run configured commands locally or in GitHub Actions, but CI remains the authoritative place to execute project test suites.

## Compared To DCO Or CLA Bots

DCO and CLA bots usually check one legal/process requirement. Themis infers DCO/signoff expectations from upstream docs and includes that as one part of a broader readiness gate.

Use dedicated DCO/CLA automation when a project requires it. Themis should complement it, not replace it.

## Compared To PR Template Enforcement

PR template bots check whether fields exist or checkboxes are marked. Themis also checks whether the PR body contains meaningful AI disclosure, accountability, test evidence, changelog decisions, issue references, and upstream checklist acknowledgements.

Themis is stricter because empty or placeholder answers are treated as blockers.

## Compared To AI Review Bots

AI review bots generate suggestions or summaries. Themis is deterministic for pass/fail decisions. AI providers, when enabled, are limited to assistant workflows and cannot change findings, severity, or exit codes.

Themis should never say that provider output certifies a patch.

## Compared To Maintainer Review

Themis does not replace maintainers. It reduces avoidable review load by blocking low-evidence submissions before deep review.

Maintainers still decide whether code is correct, maintainable, secure, legally acceptable, and aligned with the project.

## Commercial Shape

The open-source CLI and GitHub Action are useful as local and CI gates. Commercial value, if any, is more likely in managed workflow setup, organization policy packs, hosted reporting, private deployment, support, or maintainer-process consulting than in selling the CLI binary itself.

Themis should remain honest about that scope: it sells workflow confidence, not proof of correctness.
