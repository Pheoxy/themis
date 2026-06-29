# GitHub Action

Themis can run as a composite GitHub Action. The action installs Nix by default, runs the flake-packaged CLI, writes the gate output to the GitHub Step Summary, and uploads the report artifact.

![Themis validation card](assets/themis-validation-card.png)

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
- `workflow`: Themis workflow to run. Use `validate`, `guide`, `maintainer-packet`, or `self-check`. Default: `validate`.
- `output`: report path. Default: `upstream-validation-report.md`.
- `format`: gate output format. Use `markdown`, `comment`, `json`, or `sarif`. Default: `markdown`.
- `annotations`: CI annotation mode. Use `github` or `none`. Default: `github`.
- `step-summary`: write gate output to the GitHub Step Summary when possible. Default: `true`.
- `draft-pr`: create a draft PR after validation passes. Default: `false`.
- `title`: draft PR title override.
- `base-branch`: draft PR target branch override.
- `head-branch`: draft PR source branch override.
- `install-nix`: install Nix before running. Default: `true`.

## Outputs

- `status`: `pass` when Themis exits `0`, otherwise `blocked`.
- `exit-code`: Themis CLI exit code.
- `report`: path to the generated gate output artifact.

Draft PR creation from CI requires write permissions and GitHub CLI authentication. Keep it opt-in.
When `draft-pr` is `true`, the action runs `themis pull-request draft` regardless of `workflow`.

Markdown and comment reports are appended directly to the summary. JSON and SARIF are wrapped in fenced code blocks so the check summary remains readable.

## Maintainer Packet Workflow

Use the maintainer packet workflow when the action should produce contributor-facing feedback instead of the default validation report:

```yaml
- uses: OWNER/themis@main
  with:
    base: origin/${{ github.base_ref }}
    body-file: pr-body.md
    workflow: maintainer-packet
    run-checks: "true"
```
