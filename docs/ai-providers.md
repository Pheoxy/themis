# AI Providers

Themis is allowed to use AI assistance for assistant workflows, but provider use must be explicit, auditable, and unable to override the hard gate.

Current status:

- Provider configuration and diagnostics exist.
- Provider adapter interfaces exist.
- Built-in fake provider preview exists for tests and demos.
- Custom command provider preview exists for local experimentation.
- Network providers are not implemented yet.
- The deterministic gate remains the authority for pass/fail results.

## Safety Contract

- Providers are disabled by default.
- Themis must never make hidden AI calls.
- API key values must never be printed in diagnostics, reports, annotations, JSON, or SARIF.
- Prompt/context text is redacted for secret-looking values before provider preview execution.
- Provider output may assist workflows such as `guide`, `maintainer-packet`, `rules`, and `explain`.
- Provider output must not decide `validate` pass/fail status.
- Provider-backed output must disclose that an AI provider was used.
- Hard blockers always win over provider suggestions.
- The user remains accountable for submitted work.

## Configuration

Provider settings live under `[ai]` in `.themis.toml`.

```toml
[ai]
enabled = false
provider = "none"
model = ""
api_key_env = ""
endpoint_env = ""
command_env = ""
allowed_workflows = ["explain", "guide", "maintainer-packet", "rules"]
```

Supported provider names for configuration diagnostics:

- `none`
- `openai`
- `anthropic`
- `ollama`
- `custom`

External providers require an environment variable name in `api_key_env`. Themis checks that the variable is present, but never prints the secret value.

## Diagnostics

```bash
themis providers --repo .
themis providers preview --repo . --workflow guide --prompt "Summarize what to fix next."
themis providers --repo . --format json
themis doctor --repo .
```

`themis doctor` includes provider diagnostics so a project can see provider readiness alongside git, policy, rule-doc, and required-check readiness.

## Fake Provider

The fake provider is deterministic and makes no network calls. It exists for tests, demos, and integration development.

```toml
[ai]
enabled = true
provider = "fake"
model = "fake-test-model"
allowed_workflows = ["guide"]
```

## Custom Command Provider

The custom provider runs an explicit local command read from `command_env`. The command receives a JSON provider request on stdin and should write assistant text to stdout.

```toml
[ai]
enabled = true
provider = "custom"
model = "local-script"
command_env = "THEMIS_PROVIDER_COMMAND"
allowed_workflows = ["guide", "explain"]
```

The command is never inferred by Themis. It must be explicitly configured through the named environment variable. Provider stdout and error output are redacted for secret-looking values before Themis prints them.

Provider request shape:

```json
{
  "workflow": "guide",
  "prompt": "Summarize what to fix next.",
  "context": {
    "repo": "/path/to/repo"
  }
}
```

Provider preview output includes audit metadata:

- provider name
- model
- assisted workflow
- disclosure text
- SHA-256 hash of the redacted prompt
- number of redactions applied

## Implementation Roadmap

1. Keep provider configuration and diagnostics stable.
2. Add provider-backed summaries only for assistant workflows.
3. Expand provider context packets for assistant workflows without exposing secrets.
4. Add tests proving provider output cannot suppress or downgrade hard blockers.
5. Add network providers only after adapter safety tests are mature.
