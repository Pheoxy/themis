# Stability Policy

Themis follows Semantic Versioning starting with `1.0.0`.

Version `1.0.0` defines the public compatibility surface described below. Backward-incompatible changes to that surface require a new major version unless the behavior is explicitly documented as experimental or internal.

## Stable Public Surface

The stable public surface includes:

- CLI command names and documented aliases in `docs/cli.md`.
- Documented CLI options and exit-code meanings.
- GitHub Action inputs and outputs documented in `docs/github-action.md`.
- `.themis.toml` configuration fields documented in `docs/configuration.md` and `docs/schema/themis.schema.json`.
- JSON output field names for documented workflows.
- SARIF output shape at the level required for standard SARIF consumers.
- Finding codes emitted by the deterministic gate.
- Release maintenance commands: `themis release check` and `themis release audit`.

## Compatibility Expectations

Patch releases may include:

- Bug fixes.
- False-positive/false-negative tuning that preserves documented command behavior.
- Documentation fixes.
- Additional tests.
- New finding explanations.

Minor releases may include:

- New commands.
- New output fields.
- New policy fields with safe defaults.
- New GitHub Action inputs with defaults.
- New finding codes.
- New assistant workflows that do not alter existing pass/fail semantics.

Major releases are required for:

- Removing or renaming documented commands, options, config fields, or action inputs/outputs.
- Changing documented exit-code meanings.
- Removing documented JSON/SARIF fields without replacement.
- Making existing safe defaults stricter in a way that breaks normal configured use.
- Allowing provider output to affect deterministic gate findings, severities, or exit codes.

## Not Stable

The following are not considered stable public API:

- Internal Python module layout.
- Internal helper function names.
- Exact prose wording in human-readable reports.
- Non-documented test fixtures.
- Visual assets, unless a future brand policy says otherwise.

## Provider Boundary

AI provider integrations remain non-authoritative. Provider-backed assistant output may improve over minor or patch releases, but provider output must not decide gate pass/fail status in any `1.x` release.

## Policy Tuning

Themis is intentionally strict. Patch and minor releases may improve detection patterns, reduce false positives, or add new blockers for newly documented unsafe behavior. Such changes should be documented in `CHANGELOG.md` when they affect user workflows.
