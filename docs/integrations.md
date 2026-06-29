# Ecosystem Integrations

Themis does not know whether a project is correct. It checks whether a contribution gives maintainers enough deterministic evidence to review it safely. Configure required checks to match the upstream project, then provide exact passing evidence in PR bodies and CI.

## Nix

Use `nix flake check` as the primary required check when the target project has a flake:

```toml
[policy]
required_checks = [
  "nix flake check",
]
```

Evidence example:

```text
nix flake check passed
```

## Python

Use the command the upstream project documents. Common choices are:

```toml
[policy]
required_checks = [
  "python -m unittest",
]
```

or:

```toml
[policy]
required_checks = [
  "pytest",
]
```

Evidence examples:

```text
python -m unittest passed
pytest passed
```

If code changes are made, keep `require_test_changes_for_code = true` unless the upstream project explicitly accepts evidence-only changes.

## Rust

Rust projects commonly use `cargo test` and may require Conventional Commits or DCO signoff in `CONTRIBUTING.md`:

```toml
[policy]
required_checks = [
  "cargo test",
]
```

Evidence example:

```text
cargo test passed
```

When upstream docs require Conventional Commits, Themis checks commit subjects in the base range.

## Node

Use the package manager documented upstream:

```toml
[policy]
required_checks = [
  "npm test",
]
```

Other common choices include `yarn test`, `pnpm test`, or a project-specific CI command.

Evidence examples:

```text
npm test passed
pnpm test passed
```

## Go

For Go projects, prefer the broad package test command unless upstream documents a narrower command:

```toml
[policy]
required_checks = [
  "go test ./...",
]
```

Evidence example:

```text
go test ./... passed
```

## GitHub Actions

The action should run after checkout with full history when commit trailers or commit style need verification:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
- uses: OWNER/themis@main
  with:
    base: origin/${{ github.base_ref }}
    body-file: pr-body.md
    evidence: "nix flake check passed"
    run-checks: "true"
```

Use `workflow: config-check` for lightweight `.themis.toml` validation on configuration-only pull requests.

## AI Disclosure

If upstream docs mention AI, LLMs, or generated contributions, include explicit disclosure in the PR body. If the change is human-authored, pass `--human` or `human-authored: "true"` only when that statement is accurate.

Themis never transfers accountability. The submitter remains responsible for correctness, security, licensing, and maintainability.
