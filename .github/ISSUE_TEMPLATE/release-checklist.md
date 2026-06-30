---
name: Release checklist
about: Track local release gates before tagging or publishing Themis.
title: "Release vX.Y.Z"
labels: release
assignees: ""
---

# Themis Release Checklist

Remote, push, and GitHub Actions smoke-test work must happen last. Complete local gates first.

## Version And Generated Files

- [ ] Update `pyproject.toml` version.
- [ ] Update `src/themis/__init__.py` version.
- [ ] Update `flake.nix` version.
- [ ] Update `CHANGELOG.md` release notes.
- [ ] Regenerate CLI docs if parser/help changed: `nix develop --command python -m themis docs cli --write`.

## Local Required Gates

- [ ] `nix run . -- release check`
- [ ] `nix flake check`
- [ ] `nix run . -- release audit --history`
- [ ] `nix run . -- self-check --repo . --base HEAD~1 --body-file examples/pr-body.md --evidence "nix flake check passed" --human --run-checks`
- [ ] Confirm `git status --short` is clean.

## Security And Provenance Review

- [ ] Release audit has no blockers.
- [ ] Secret-like audit warnings are understood and limited to synthetic test fixtures.
- [ ] Asset provenance still matches tracked assets.
- [ ] No release-facing template repository URLs remain.
- [ ] Reachable history scan for removed third-party asset references remains clean.

## Remote Work Last

- [ ] Add or verify `origin` only when local gates are complete.
- [ ] Push to the private repository.
- [ ] Run a real GitHub Actions smoke test in `Pheoxy/themis`.
- [ ] Confirm action outputs, step summary, and annotations work in GitHub Actions.
- [ ] Tag only after the remote smoke test passes.

## Tagging

- [ ] Create signed release tag: `git tag -s vX.Y.Z -m "Themis vX.Y.Z"`.
- [ ] Push tag only after all local and remote gates pass.
