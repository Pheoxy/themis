# Threat Model

Themis is a pre-upstream readiness gate. It reduces avoidable maintainer load before review; it does not certify code, transfer accountability, or replace human judgment.

## Assets Protected

- Maintainer review time.
- Upstream contribution process integrity.
- Contributor accountability and disclosure quality.
- CI/check evidence quality.
- Repository hygiene around generated files, vendor files, secrets, binaries, and broad patches.
- Release readiness for Themis itself.

## In Scope

Themis is designed to catch common low-confidence contribution risks before a maintainer spends deep review time:

- Missing upstream contribution rules.
- Missing or weak AI disclosure.
- Missing or weak human accountability language.
- Missing, weak, or unproven test/check evidence.
- Missing test changes for code changes, unless explicitly configured otherwise.
- Missing DCO/signoff when upstream requires it.
- Missing upstream process acknowledgements such as changelog, issue links, PR checklists, or Conventional Commit subjects.
- Generated, build, minified, vendor, binary, secret-like, placeholder, debug, or sloppy-code changes.
- Oversized patches that need decomposition before review.
- Misconfigured Themis policy and unsafe AI provider configuration.
- Themis release hygiene checks, including license metadata, template URLs, generated/cache files, asset provenance, and redacted secret-pattern scans.

## Out Of Scope

Themis does not prove:

- Code correctness.
- Security correctness.
- License compliance for all dependencies or generated content.
- Copyright, trademark, patent, export-control, privacy, or regulatory compliance.
- Absence of all secrets, credentials, malware, vulnerabilities, or supply-chain risks.
- That AI-generated output is copyrightable, unique, or free of third-party claims.
- That upstream maintainers will accept a PR.
- That provider-backed assistant output is true.

Themis output is a gate result, not legal advice, professional advice, or maintainer approval.

## Adversary Model

Themis assumes contributors may accidentally or intentionally submit:

- AI-generated code with weak disclosure.
- Code they did not read, test, or understand.
- PRs that ignore upstream rules.
- Large noisy patches that hide risky changes.
- Generated/vendor/build artifacts mixed with source changes.
- Placeholder/debug code.
- Secret-like strings.
- Weak claims such as "tests pass" without naming a command or CI check.

Themis does not assume it can defeat a dedicated adversary with repository write access, malicious history rewriting, compromised CI, malicious dependencies, or custom content crafted to evade regex/static checks.

## AI Provider Boundary

AI providers are disabled by default. When enabled, provider output is allowed only for assistant workflows such as guidance, explanations, or maintainer-facing summaries.

Provider output must not:

- Create gate findings.
- Change finding severity.
- Change exit codes.
- Override deterministic policy checks.
- Certify safety or correctness.

Provider prompts and outputs are redacted for common secret patterns before display. Redaction is defense-in-depth, not a guarantee that sensitive information cannot appear.

## Release Audit Boundary

`themis release audit` is a deterministic pre-release hygiene check. It reports locations for secret-like patterns and avoids printing matched values.

`themis release audit --history` scans reachable git history and should be run before pushing or tagging. It cannot inspect objects that are absent from the local repository, external forks, already-pushed remote refs, private package registries, or third-party systems.

## Human Responsibilities

Contributors remain responsible for:

- Reading and understanding every submitted line.
- Accurate AI disclosure.
- Accurate human accountability statements.
- Running and reporting real checks.
- Following upstream rules.
- Security, licensing, privacy, and legal review.

Maintainers remain responsible for:

- Reviewing design and correctness.
- Deciding whether Themis policy matches project norms.
- Approving exceptions.
- Accepting or rejecting PRs.

Themis should make those responsibilities explicit; it should never claim to take them over.
