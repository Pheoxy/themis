# Changelog

All notable changes to Themis will be documented in this file.

The format follows Keep a Changelog conventions, and this project uses semantic versioning until a stronger release policy is adopted.

## [Unreleased]

### Added

- Initial Themis scaffold with Nix packaging, CLI validation, generated CLI docs, GitHub Action support, and draft pull request creation.
- `themis guide` assistant command that runs the gate and produces upstream readiness checklists.
- `themis review` command that runs the gate and produces maintainer-focused feedback packets.
- Configuration, GitHub Action, and development documentation.
- Direct CLI parser tests for normal and shorthand command forms.
- `themis init` setup command for target repositories.
- Shell completion generation for Bash, Zsh, and Fish.

### Changed

- AI disclosure, human accountability, and test evidence now reject placeholder or vague text.
- Documentation and reports now state explicitly that Themis does not take accountability for users or certify passing code.
