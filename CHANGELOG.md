# Changelog

All notable changes to Themis will be documented in this file.

The format follows Keep a Changelog conventions, and this project uses semantic versioning until a stronger release policy is adopted.

## [Unreleased]

### Added

- Initial Themis scaffold with Nix packaging, CLI validation, generated CLI docs, GitHub Action support, and draft pull request creation.
- `themis guide` assistant command that runs the gate and produces upstream readiness checklists.
- `themis maintainer-packet` command that runs the gate and produces maintainer-focused feedback packets.
- Optional GitHub workflow annotations for blockers, warnings, and informational findings.
- Richer validation reports with changed files, bounded check output snippets, and next actions.
- CLI style guidance and target-repository CLI integration tests.
- Machine-readable JSON gate output through `--format json`.
- `themis explain` finding-code remediation catalog for contributor/maintainer back-and-forth.
- SARIF gate output through `--format sarif`.
- `themis doctor` repository and local-tool readiness diagnostics.
- `themis rules` effective policy and inferred upstream rule inspection.
- Explicit AI provider configuration diagnostics through `themis providers`.
- Provider adapter interface with fake and custom command preview adapters.
- Provider preview redaction and audit metadata for prompts and custom command output.
- GitHub Action step-summary output for Themis reports.
- `themis self-check` combined diagnostics/rules/providers/gate workflow.
- `themis init` now writes safe disabled-by-default AI provider configuration.
- `themis release check` version consistency workflow enforced by `nix flake check`.
- GitHub Action outputs for gate status, exit code, and report path.
- GitHub Action `workflow` input for `validate`, `guide`, `maintainer-packet`, and `self-check`.
- Concise PR-comment output through `--format comment`.
- Optional GitHub Action PR comments through `comment-pr`.
- Copyable GitHub Action examples for validation, PR comments, and self-check workflows.
- JSON Schema for `.themis.toml` configuration.
- Fail-closed handling for unknown top-level `.themis.toml` tables while allowing `[ai]`-only configs.
- `themis config check` for validating `.themis.toml` without running a gate workflow.
- GitHub Action `config-check` workflow support and copyable example.
- Executable tests for GitHub Action workflow argument routing.
- JSON Schema alignment for top-level policy-key shorthand.
- Shell completion coverage for the `config` command.
- README command table coverage for diagnostics and config validation workflows.
- Fail-closed rejection for configs that mix `[policy]` with top-level policy-key shorthand.
- Release checks now verify core release files are present and non-empty.
- Release checks now reject placeholder package metadata URLs.
- `nix flake check` now validates the repository `.themis.toml` with `themis config check`.
- `themis config check` now works on plain directories, not only git repositories.
- Rule inference fixture coverage for common Python, Rust, and Node upstream contribution styles.
- Gate fixture coverage for inferred issue-link and Conventional Commits requirements.
- Executable tests for GitHub Action PR comment step behavior.
- Executable tests for GitHub Action Step Summary rendering behavior.
- Release process documentation covering version updates, gates, and tagging.
- Ecosystem integration documentation for Nix, Python, Rust, Node, Go, and GitHub Actions.
- Specific `themis explain` entries for inferred upstream process blockers and common gate blockers.
- Regression coverage requiring active policy finding codes to have remediation explanations.
- CLI safety coverage proving `validate` does not call configured AI providers.
- `themis config check` now rejects AI provider workflow lists that include gate workflows.
- GitHub Action `config-check` now rejects incompatible output formats before invoking Themis.
- `self-check` now rejects unsupported `comment` and `sarif` output formats consistently in CLI and action routing.
- Generated CLI docs now advertise only `markdown` and `json` for `self-check` output.
- GitHub Action now ignores draft PR-only inputs unless `draft-pr` is enabled.
- GitHub Action now fails early when `draft-pr` is enabled without `body-file`.
- GitHub Action docs now state the draft PR `body-file` requirement.
- SARIF results now include stable Themis fingerprints and stronger output coverage.
- `themis release audit` for redacted pre-1.0 secret, template URL, generated-file, license, and asset-provenance checks.
- GitHub Action examples now reference `Pheoxy/themis@main` instead of template owner placeholders.
- Project license changed from MIT to Apache-2.0.
- Documented ChatGPT/OpenAI provenance and Apache-2.0 license intent for generated PNG assets.
- Package metadata and JSON Schema ID now use the reserved `Pheoxy/themis` repository.
- `nix flake check` now enforces the non-history release audit.
- Rule inference and gate fixtures now cover Go and Java/Maven/Gradle test workflows.
- Monorepo contribution docs are discovered outside generated/vendor trees, with generated/vendor allowlist fixture coverage.
- `themis release audit --history` now fails cleanly outside git repositories.
- Threat model documentation covering scope, adversary model, provider boundaries, and non-guarantees.
- Positioning documentation comparing Themis with scanners, CI, PR bots, AI reviewers, and maintainer review.
- Executable GitHub Action tests now cover `GITHUB_OUTPUT` status, exit-code, and report outputs.
- Removed obsolete concept PNG assets from `docs/assets/concepts/`.
- Configuration, GitHub Action, and development documentation.
- Direct CLI parser tests for command forms.
- `themis init` setup command for target repositories.
- Shell completion generation for Bash, Zsh, and Fish.
- CLI style documentation covering command naming, output shape, status language, and machine-output rules.

### Changed

- AI disclosure, human accountability, and test evidence now reject placeholder or vague text.
- Documentation and reports now state explicitly that Themis does not take accountability for users or certify passing code.
