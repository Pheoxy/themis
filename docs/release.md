# Release Process

Themis releases are Nix-first and fail closed. Do not publish artifacts until every local gate below passes.

Use `.github/ISSUE_TEMPLATE/release-checklist.md` to track release work. Remote, push, and GitHub Actions smoke-test steps should happen last.

Use `docs/release-notes-template.md` for GitHub release notes and final `CHANGELOG.md` entries.

## Version Update

Update all version declarations together:

- `pyproject.toml`
- `src/themis/__init__.py`
- `flake.nix`

Then verify consistency:

```bash
nix run . -- release check
```

`themis release check` also verifies core release files and rejects unresolved package metadata such as template repository URLs.

## Generated Files

Regenerate CLI docs after command, flag, alias, or help-text changes:

```bash
nix develop --command python -m themis docs cli --write
```

## Required Gates

Run the full Nix gate:

```bash
nix flake check
```

Run the redacted pre-1.0 release audit, including reachable git history:

```bash
nix run . -- release audit --history
```

The audit checks for secret-like material, generated/cache files, unresolved template repository URLs, license metadata, and asset provenance. It reports locations, not secret values.

Run Themis against the committed release change before tagging:

```bash
nix run . -- self-check --repo . --base HEAD~1 --body-file examples/pr-body.md --evidence "nix flake check passed" --human --run-checks
```

The self-check result is a gate result only. It does not certify the release or transfer accountability away from the releaser.

## Tagging

Create a signed release commit before tagging. Tag only after the release commit passes the gates above.

Use a semantic version tag:

```bash
git tag -s vX.Y.Z -m "Themis vX.Y.Z"
```

Do not tag while the worktree is dirty.
