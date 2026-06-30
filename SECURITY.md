# Security Policy

Themis is a validation gate, so security issues include ordinary vulnerabilities and validation bypasses that could let risky code pass as safe. Themis does not certify that passing code is secure; it only reports configured blockers and evidence gaps.

## Supported Versions

Security fixes target the latest `1.x` release and the default branch. Older releases may receive fixes at maintainer discretion until a formal long-term support policy exists.

## Reporting A Vulnerability

Report security issues privately to the maintainers before publishing details. If no private channel exists for the deployed repository, open a minimal public issue that states a private security report is needed without including exploit details.

For GitHub-hosted releases, use private vulnerability reporting or GitHub Security Advisories when available.

Include:

- Affected version or commit.
- Reproduction steps.
- Expected and actual validator behavior.
- Whether the issue can cause a false pass, secret exposure, command execution, or incorrect pull request creation.

## Security Expectations

- Themis must fail closed when it cannot inspect a repository safely.
- Themis must not silently ignore failed required checks.
- Themis must not create pull requests when blockers exist.
- Themis must treat secrets in diffs as hard blockers.
