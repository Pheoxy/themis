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

More complete copyable examples live in `examples/github-actions/`:

- `validate.yml`: default hard gate with read-only pull request permissions.
- `comment.yml`: maintainer-facing comment workflow with `format: comment` and `comment-pr: "true"`.
- `self-check.yml`: combined doctor/rules/providers/gate workflow.
- `config-check.yml`: lightweight `.themis.toml` validation workflow.

## Inputs

- `repo`: repository path to validate. Default: `.`.
- `base`: base ref for the diff. Optional for `config-check`; recommended for PR gate workflows.
- `body-file`: file containing the pull request body.
- `evidence`: inline test/check evidence.
- `evidence-file`: file containing test/check evidence.
- `human-authored`: set to `true` only when no AI assistance was used.
- `run-checks`: run `.themis.toml` required checks. Default: `true`.
- `workflow`: Themis workflow to run. Use `validate`, `guide`, `maintainer-packet`, `self-check`, or `config-check`. Default: `validate`.
- `output`: report path. Default: `upstream-validation-report.md`.
- `format`: Themis output format. Use `markdown`, `comment`, `json`, or `sarif`. `self-check` and `config-check` support only `markdown` and `json`. Default: `markdown`.
- `annotations`: CI annotation mode. Use `github` or `none`. Default: `github`.
- `step-summary`: write gate output to the GitHub Step Summary when possible. Default: `true`.
- `comment-pr`: post the generated gate output as a pull request comment using `gh`. Default: `false`.
- `pr-number`: pull request number for `comment-pr`. Defaults to `github.event.pull_request.number` when available.
- `draft-pr`: create a draft PR after validation passes. Default: `false`.
- `title`: draft PR title override.
- `base-branch`: draft PR target branch override.
- `head-branch`: draft PR source branch override.
- `install-nix`: install Nix before running. Default: `true`.

## Outputs

- `status`: `pass` when Themis exits `0`, otherwise `blocked`.
- `exit-code`: Themis CLI exit code.
- `report`: path to the generated Themis output artifact.

Draft PR creation from CI requires write permissions and GitHub CLI authentication. Keep it opt-in.
When `draft-pr` is `true`, the action runs `themis pull-request draft` regardless of `workflow`.

Markdown reports are appended directly to the summary. Comment, JSON, and SARIF reports are wrapped in fenced code blocks so the check summary remains readable.

PR commenting requires `pull-requests: write` and a valid `GH_TOKEN`. Comment failures emit a warning instead of replacing the gate result. Use `format: comment` for concise comment bodies.

The `self-check` and `config-check` workflows reject output formats other than `markdown` and `json`.

The `config-check` workflow ignores gate-only inputs such as `base`, `body-file`, `evidence`, and `annotations`.

The examples in `examples/github-actions/` show the expected permission split:

- validation and self-check use `pull-requests: read`.
- config-check uses `contents: read` only.
- PR comments use `pull-requests: write` and `GH_TOKEN`.

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

## PR Comment Workflow

```yaml
permissions:
  contents: read
  pull-requests: write

steps:
  - uses: OWNER/themis@main
    env:
      GH_TOKEN: ${{ github.token }}
    with:
      base: origin/${{ github.base_ref }}
      body-file: pr-body.md
      format: comment
      comment-pr: "true"
```
