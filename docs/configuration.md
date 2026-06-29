# Configuration

Themis reads `.themis.toml` from the target repository root. The built-in paranoid rules always apply first; configuration can tune thresholds and required commands, but should not be used to hide missing evidence.

A JSON Schema is available at `docs/schema/themis.schema.json` for editors and tooling.

Run `themis config check --repo .` to validate policy and AI provider configuration without running a PR gate.

## Example

```toml
[policy]
max_changed_files = 25
max_added_lines = 800
max_deleted_lines = 500
max_file_added_lines = 300
require_upstream_rules = true
require_tests_for_code = true
require_test_changes_for_code = true
block_generated_paths = true
block_vendor_paths = true
block_ai_markers = true
block_placeholders = true

allow_paths = [
  "docs/generated/",
]

required_checks = [
  "nix flake check",
]

[ai]
enabled = false
provider = "none"
model = ""
api_key_env = ""
endpoint_env = ""
command_env = ""
allowed_workflows = ["explain", "guide", "maintainer-packet", "rules"]
```

## Policy Fields

- `max_changed_files`: blocks broad patches that are hard to review.
- `max_added_lines`: blocks large additions that need human breakdown.
- `max_deleted_lines`: blocks large removals that need explicit review.
- `max_file_added_lines`: blocks oversized single-file changes.
- `require_upstream_rules`: blocks when Themis cannot find contribution rules.
- `require_tests_for_code`: blocks code changes without passing test/check evidence.
- `require_test_changes_for_code`: blocks code changes without test file changes.
- `block_generated_paths`: blocks generated, build, and minified outputs.
- `block_vendor_paths`: blocks vendored or third-party changes.
- `block_ai_markers`: blocks AI-tool marker text in code diffs.
- `block_placeholders`: blocks placeholder, cleanup, or speculative language in code diffs.
- `allow_paths`: path prefixes or glob patterns exempt from generated/vendor path blockers.
- `required_checks`: commands Themis runs only when `--run-checks` is used, or by default during `themis pull-request draft`.

Keep exceptions narrow. If a project needs a broad allowlist, that usually means Themis needs a better rule instead of a weaker policy.

## AI Provider Fields

AI providers are disabled by default. Provider configuration is for explicit assistant workflows only; it must not decide gate pass/fail status.

- `enabled`: opt in to provider-backed assistant preview behavior.
- `provider`: provider name for diagnostics and adapters. Supported diagnostic names are `none`, `fake`, `openai`, `anthropic`, `ollama`, and `custom`.
- `model`: provider model name.
- `api_key_env`: environment variable name containing an API key. The value is never printed.
- `endpoint_env`: optional environment variable name containing a provider endpoint.
- `command_env`: environment variable name containing the custom provider command.
- `allowed_workflows`: assistant workflows allowed to use provider output. Gate workflows such as `validate` are not allowed.

See `docs/ai-providers.md` for the provider safety contract and roadmap.

## JSON Schema

Editors and CI tools can use the schema file to validate supported keys and value shapes:

```text
docs/schema/themis.schema.json
```

The schema is checked by unit tests to stay aligned with Themis's policy and AI provider config dataclasses.
