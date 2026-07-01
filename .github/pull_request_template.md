## Summary

Describe the change and why it belongs in Themis.

## Change Type

- [ ] Gate/policy behavior
- [ ] CLI or GitHub Action behavior
- [ ] Configuration/schema behavior
- [ ] Documentation, release, or repository metadata
- [ ] Tests or fixtures only

## Validation

- [ ] I ran `nix flake check`.
- [ ] I updated tests for behavior changes.
- [ ] I regenerated `docs/cli.md` when CLI behavior changed.
- [ ] I updated `CHANGELOG.md` or explain why no changelog entry is needed below.
- [ ] I reviewed the target repository rules affected by this change.
- [ ] I ran `themis self-check` or explain why it does not apply below.
- [ ] I considered whether this changes pass/fail behavior, finding codes, or exit codes.

## Evidence

Paste exact command output or CI links. Include the relevant Themis report when behavior changes.

## Policy Impact

- Finding codes added/changed/removed:
- Output formats affected:
- GitHub Action inputs/outputs affected:
- `.themis.toml` schema fields affected:

## AI Assistance

AI assistance: State whether AI assistance was used and how the output was reviewed.

Human accountability: State that you, not Themis or any AI tool, take responsibility for every line, including tests, licensing, security, and project policy compliance.

## Changelog Decision

Changelog: Updated / not needed because ...

## Release Risk

State whether this is safe for a patch release, needs a minor release, or changes the 1.x compatibility surface.
