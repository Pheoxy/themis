# GitHub Action

Themis can run as a composite GitHub Action. The action installs Nix by default, runs the flake-packaged CLI, and uploads the Markdown validation report.

## Pull Request Gate

```yaml
name: Themis

on: pull_request

permissions:
  contents: read
  pull-requests: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Write PR body
        env:
          PR_BODY: ${{ github.event.pull_request.body }}
        run: printf '%s' "$PR_BODY" > pr-body.md
      - uses: OWNER/themis@main
        with:
          base: origin/${{ github.base_ref }}
          body-file: pr-body.md
          run-checks: "true"
```

## Inputs

- `repo`: repository path to validate. Default: `.`.
- `base`: base ref for the diff. Required.
- `body-file`: file containing the pull request body.
- `evidence`: inline test/check evidence.
- `evidence-file`: file containing test/check evidence.
- `human-authored`: set to `true` only when no AI assistance was used.
- `run-checks`: run `.themis.toml` required checks. Default: `true`.
- `output`: report path. Default: `upstream-validation-report.md`.
- `draft-pr`: create a draft PR after validation passes. Default: `false`.
- `title`: draft PR title override.
- `base-branch`: draft PR target branch override.
- `head-branch`: draft PR source branch override.
- `install-nix`: install Nix before running. Default: `true`.

Draft PR creation from CI requires write permissions and GitHub CLI authentication. Keep it opt-in.
