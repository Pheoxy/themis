# Themis CLI Style

Themis is a strict CLI tool first. The mascot and visual assets belong in README/docs/artwork. Runtime output should feel like a real upstream gate that can be copied into logs, CI artifacts, issue comments, or a maintainer handoff.

The style goal is restrained identity, not decoration.

## Core Rule

Use Themis branding only in human-facing output.

Do not put decorative branding into machine-readable output.

Human output may identify the tool and workflow:

```text
Themis / VALIDATE
Pre-upstream PR validation

Context:
  Repo:   /path/to/repo
  Base:   origin/main
  Mode:   ai-assisted

Checks:
  [ OK ] Upstream rules detected
  [FAIL] AI disclosure missing
  [FAIL] Test evidence missing
  [WARN] Generated file changed

Result:
  BLOCKED

Next:
  Add AI assistance and human accountability sections.
  Provide exact passing test/check evidence.
```

Machine output should be plain data with no mascot language, no logo text, and no decorative header:

```json
{
  "tool": "themis",
  "workflow": "validate",
  "result": "blocked",
  "exit_code": 2,
  "findings": [
    {
      "severity": "blocker",
      "code": "missing-ai-disclosure",
      "message": "AI-assisted submissions require disclosure."
    }
  ]
}
```

## Command Model

The commands are intentionally separated by audience and output, not by different validator logic.

| Command | Short Form | Audience | Purpose |
| --- | --- | --- | --- |
| `themis validate` | `themis v` | contributor / CI | Run the hard gate and produce the base validation report. |
| `themis guide` | `themis g` | contributor | Run the same gate and produce preparation guidance for fixing the submission. |
| `themis maintainer-packet` | `themis mp` | maintainer | Run the same gate and produce maintainer-facing feedback and triage notes. |
| `themis explain` | none | contributor / maintainer | Explain a finding code and expected remediation. |
| `themis doctor` | none | contributor / maintainer / CI | Diagnose repository and tool readiness before gate workflows. |
| `themis rules` | none | contributor / maintainer / CI | Show effective policy and inferred upstream rules. |
| `themis pull-request draft` | `themis pr d` | contributor | Run the gate, run configured checks by default, and create a GitHub draft PR only if clean. |
| `themis init` | none | setup | Create starter Themis policy/template files in a target repo. |
| `themis docs cli` | none | project maintenance | Generate/check parser-derived CLI docs. |
| `themis completion` | none | shell setup | Print completion scripts. |

Do not add `themis check` as a validation alias. It is less clear than `validate`, conflicts mentally with required checks and `--check`, and does not add useful ergonomics.

Do not use `themis review` as a public command. Themis is not doing code review. It prepares a maintainer packet so humans can review more efficiently.

## Naming Rules

Use long command names for concepts and short aliases for speed.

Good:

```text
themis validate
themis v
themis guide
themis g
themis maintainer-packet
themis mp
themis explain missing-test-evidence
themis doctor
themis rules
themis pull-request draft
themis pr d
```

Avoid duplicate concept names:

```text
themis check
themis review
themis audit
```

`validate`, `guide`, and `maintainer-packet` all run the same gate. The difference is the report shape:

```text
validate           gate result
guide              contributor preparation output
maintainer-packet  maintainer handoff output
pull-request draft validate + required checks + draft PR creation
```

## Output Shape

Human output should use the same basic structure everywhere:

```text
Themis / WORKFLOW
Short workflow description

Context:
  Repo:  /path/to/repo
  Base:  origin/main
  Mode:  ai-assisted

Checks:
  [ OK ] Finding category passed
  [WARN] Finding category needs attention
  [FAIL] Finding category blocks submission

Result:
  BLOCKED

Next:
  Specific next action.
```

Markdown reports may use headings, but they should preserve the same information architecture:

```text
Summary
Changed Files
Findings
Required Checks
Next Actions
Validator Caveat
```

Avoid full-screen TUI layouts, ASCII logos, large banners, mascots, or playful framing in terminal output.

## Status Language

Use legal/gate language rather than toy branding.

Allowed result/status terms:

- `PASS`
- `BLOCKED`
- `ACTION REQUIRED`
- `GATE CLEAR`
- `DRAFT READY`
- `DRAFT CREATED`
- `CONFIG ERROR`
- `FAILED`

Use severity labels consistently:

- `[ OK ]`: a category passed or no issue was found.
- `[INFO]`: informational context.
- `[WARN]`: not a hard blocker, but worth maintainer/contributor attention.
- `[FAIL]`: a hard blocker or failed required check.

For Markdown reports, use the policy severity words already used by the validator:

- `BLOCKER`
- `WARNING`
- `INFO`

## Exit Codes

The CLI should stay predictable for scripts and CI.

Current exit codes:

| Code | Meaning |
| --- | --- |
| `0` | No hard blockers. |
| `2` | One or more hard blockers. |
| `3` | Themis execution/configuration error. |

Future CLI additions should preserve those meanings. If more exit codes are added later, document them before release.

## Output Modes

Current behavior:

- Human/Markdown output is the primary output.
- `--output` writes gate output to a file.
- `--format json` writes machine-readable JSON.
- `--format sarif` writes SARIF 2.1.0 for code scanning or review tooling.
- No color mode exists yet.

Future modes should follow this contract:

```text
--format json  machine-readable JSON only
--plain     no header, no decoration, stable line-oriented text
--quiet     only serious errors
--verbose   extra diagnostic context
--no-color  disable color
```

Machine-readable output must not include decorative headers, mascot text, ANSI color, Markdown formatting, or prose-only status.

## Branding Rules

Use branding through structure and consistency:

- Command names.
- Stable status language.
- Gate/result terminology.
- Report section order.
- Clear exit codes.
- The same concise header in human output.

Do not use branding through terminal gimmicks:

- No ASCII art.
- No mascot in terminal output.
- No emoji status icons.
- No huge box drawings.
- No theme jokes in error messages.
- No decorative prose in JSON or logs.

Good human header:

```text
Themis / VALIDATE
Pre-upstream PR validation
```

Bad human header:

```text
████████╗██╗  ██╗███████╗███╗   ███╗██╗███████╗
THEMIS SUPER JUSTICE BOT ACTIVATED
```

## Logs

If structured logs are added later, keep them boring and parseable:

```text
2026-06-29T14:22:11+08:00 level=info tool=themis workflow=validate repo=/repo msg="loading policy"
2026-06-29T14:22:12+08:00 level=fail tool=themis workflow=validate code=missing-test-evidence msg="test evidence missing"
```

The tool identity belongs in fields such as `tool=themis` and `workflow=validate`, not in decorative prefixes.

## Design Principle

Themis CLI output should be:

- Plain by default.
- Scriptable.
- Auditable.
- Strict without being theatrical.
- Branded through consistent procedure.
- Clear about what is a gate result versus what remains human review.

The brand is not ASCII art. The brand is that every workflow feels like the same disciplined pre-upstream gate.
