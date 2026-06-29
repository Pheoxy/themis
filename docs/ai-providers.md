# AI Providers

Themis is allowed to use AI assistance for assistant workflows, but provider use must be explicit, auditable, and unable to override the hard gate.

Current status:

- Provider configuration and diagnostics exist.
- Provider-backed assistant calls are not implemented yet.
- The deterministic gate remains the authority for pass/fail results.

## Safety Contract

- Providers are disabled by default.
- Themis must never make hidden AI calls.
- API key values must never be printed in diagnostics, reports, annotations, JSON, or SARIF.
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
themis providers --repo . --format json
themis doctor --repo .
```

`themis doctor` includes provider diagnostics so a project can see provider readiness alongside git, policy, rule-doc, and required-check readiness.

## Implementation Roadmap

1. Keep provider configuration and diagnostics stable.
2. Add provider adapter interfaces with strict request/response logging that excludes secrets.
3. Add provider-backed summaries only for assistant workflows.
4. Add explicit disclosure markers to provider-backed output.
5. Add tests proving provider output cannot suppress or downgrade hard blockers.
