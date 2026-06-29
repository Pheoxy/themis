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
- Configuration, GitHub Action, and development documentation.
- Direct CLI parser tests for command forms.
- `themis init` setup command for target repositories.
- Shell completion generation for Bash, Zsh, and Fish.
- CLI style documentation covering command naming, output shape, status language, and machine-output rules.

### Changed

- AI disclosure, human accountability, and test evidence now reject placeholder or vague text.
- Documentation and reports now state explicitly that Themis does not take accountability for users or certify passing code.
