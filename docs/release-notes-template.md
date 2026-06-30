# Themis vX.Y.Z Release Notes

Use this template for GitHub releases and final `CHANGELOG.md` entries. Keep claims specific and do not imply certification, legal advice, or maintainer approval.

## Summary

- Release type: 1.0 / patch / minor / major
- Target audience: contributors, maintainers, CI users, GitHub Action users
- One-sentence release summary:

## Highlights

- TODO
- TODO
- TODO

## Added

- TODO

## Changed

- TODO

## Fixed

- TODO

## Removed

- TODO

## Security And Provenance

- License: Apache-2.0.
- Asset provenance: documented in `docs/assets/PROVENANCE.md`.
- Release audit: `nix run . -- release audit --history` passed before tagging.
- Secret scan note: release audit prints locations only and does not print matched secret-like values.
- Known audit warnings, if any:
  - TODO

## Verification

Record exact commands and outcomes:

```bash
nix run . -- release check
nix flake check
nix run . -- release audit --history
nix run . -- self-check --repo . --base HEAD~1 --body-file examples/pr-body.md --evidence "nix flake check passed" --human --run-checks
```

Results:

- `release check`: pass/fail
- `nix flake check`: pass/fail
- `release audit --history`: pass/fail
- `self-check`: pass/fail
- `git status --short`: clean/not clean

## GitHub Action Smoke Test

Remote work happens last. Fill this section only after the private repository smoke test passes.

- Repository: `https://github.com/Pheoxy/themis`
- Workflow tested:
- Result:
- Outputs verified:
- Step Summary verified:
- Annotations verified:

## Non-Guarantees

Themis is a pre-upstream readiness gate. Passing this release's checks does not certify code correctness, security, licensing, legal compliance, or upstream acceptance.

## Upgrade Notes

- TODO

## Links

- Changelog:
- Documentation:
- Release tag:
