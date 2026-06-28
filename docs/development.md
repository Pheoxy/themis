# Development

Themis development is Nix-first.

## Setup

```bash
nix develop
```

## Test

```bash
nix flake check
```

`nix flake check` runs unit tests and checks that generated CLI documentation matches the parser code.

## CLI Documentation

After changing commands, flags, help text, or aliases, regenerate the CLI reference:

```bash
nix develop --command python -m themis docs cli --write
```

Then verify it:

```bash
nix develop --command python -m themis docs cli --check
```

## Self Validation

Themis should be run against its own changes before a pull request is drafted. The pull request body must include `AI assistance:` and `Human accountability:` sections when AI assistance was used.

Self-validation does not make Themis responsible for the change. It only checks whether the change satisfies Themis's configured gate. The submitter still owns correctness, security, licensing, and maintainability.
