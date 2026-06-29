from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import tomllib


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

SUPPORTED_PROVIDERS = {"none", "openai", "anthropic", "ollama", "custom"}
EXTERNAL_API_KEY_PROVIDERS = {"openai", "anthropic", "custom"}
ASSISTANT_WORKFLOWS = {"guide", "maintainer-packet", "explain", "rules"}


@dataclass
class AIProviderConfig:
    enabled: bool = False
    provider: str = "none"
    model: str = ""
    api_key_env: str = ""
    endpoint_env: str = ""
    allowed_workflows: list[str] = field(default_factory=lambda: sorted(ASSISTANT_WORKFLOWS))


@dataclass(frozen=True)
class ProviderCheck:
    status: str
    code: str
    message: str
    detail: str | None = None


@dataclass(frozen=True)
class ProviderDiagnostics:
    repo: Path
    config: AIProviderConfig
    checks: list[ProviderCheck]


def load_provider_config(repo: Path) -> AIProviderConfig:
    path = repo / ".themis.toml"
    if not path.exists():
        return AIProviderConfig()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    raw = data.get("ai", {})
    allowed = set(AIProviderConfig.__dataclass_fields__)  # type: ignore[attr-defined]
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"unknown ai provider keys in {path}: {', '.join(unknown)}")
    config = AIProviderConfig(**raw)
    if config.provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"unsupported ai provider `{config.provider}` in {path}")
    return config


def inspect_providers(repo: Path) -> ProviderDiagnostics:
    config = load_provider_config(repo)
    checks: list[ProviderCheck] = [
        ProviderCheck(PASS, "provider-config", "Loaded AI provider configuration."),
    ]
    if not config.enabled:
        checks.append(ProviderCheck(PASS, "provider-disabled", "AI provider use is disabled; Themis will run deterministic workflows only."))
        return ProviderDiagnostics(repo=repo, config=config, checks=checks)

    if config.provider == "none":
        checks.append(ProviderCheck(FAIL, "provider-selected", "AI provider is enabled but provider is `none`."))
    else:
        checks.append(ProviderCheck(PASS, "provider-selected", f"Configured provider `{config.provider}`."))

    if not config.model.strip():
        checks.append(ProviderCheck(FAIL, "provider-model", "AI provider is enabled but no model is configured."))
    else:
        checks.append(ProviderCheck(PASS, "provider-model", "AI model is configured.", config.model))

    invalid_workflows = sorted(set(config.allowed_workflows) - ASSISTANT_WORKFLOWS)
    if invalid_workflows:
        checks.append(
            ProviderCheck(
                FAIL,
                "provider-workflows",
                "AI providers may only be used for assistant workflows, not gate decisions.",
                ", ".join(invalid_workflows),
            )
        )
    else:
        checks.append(ProviderCheck(PASS, "provider-workflows", "Configured AI workflows are assistant-only."))

    if config.provider in EXTERNAL_API_KEY_PROVIDERS:
        if not config.api_key_env:
            checks.append(ProviderCheck(FAIL, "provider-api-key-env", "External AI provider requires an API key environment variable name."))
        elif os.environ.get(config.api_key_env):
            checks.append(ProviderCheck(PASS, "provider-api-key-env", "API key environment variable is set.", config.api_key_env))
        else:
            checks.append(ProviderCheck(FAIL, "provider-api-key-env", "API key environment variable is not set.", config.api_key_env))
    elif config.provider == "ollama":
        checks.append(ProviderCheck(WARN, "provider-local", "Local Ollama provider configured; ensure the daemon is running before assistant workflows."))

    if config.endpoint_env:
        if os.environ.get(config.endpoint_env):
            checks.append(ProviderCheck(PASS, "provider-endpoint-env", "Endpoint environment variable is set.", config.endpoint_env))
        else:
            checks.append(ProviderCheck(WARN, "provider-endpoint-env", "Endpoint environment variable is not set.", config.endpoint_env))

    return ProviderDiagnostics(repo=repo, config=config, checks=checks)


def providers_exit_code(diagnostics: ProviderDiagnostics) -> int:
    return 2 if any(check.status == FAIL for check in diagnostics.checks) else 0


def render_providers_markdown(diagnostics: ProviderDiagnostics) -> str:
    status = "BLOCKED" if providers_exit_code(diagnostics) else "PASS"
    lines = [
        "# Themis AI Providers",
        "",
        f"Status: **{status}**",
        "",
        f"Repository: `{diagnostics.repo}`",
        "",
        "## Configuration",
        "",
    ]
    for key, value in asdict(diagnostics.config).items():
        if key == "api_key_env" and value:
            lines.append(f"- `{key}`: `{value}` (environment variable name only; value is never printed)")
        else:
            lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Checks", ""])
    for check in diagnostics.checks:
        lines.append(f"- **{check.status}** `{check.code}`: {check.message}")
        if check.detail:
            lines.append(f"  Detail: `{check.detail}`")
    lines.extend(
        [
            "",
            "## Safety Contract",
            "",
            "- AI providers are opt-in and disabled by default.",
            "- Provider output may assist contributor/maintainer workflows, but must not override hard blockers.",
            "- Themis must disclose provider use in generated assistant output when provider-backed workflows are implemented.",
            "- API key values are never printed by Themis diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def render_providers_json(diagnostics: ProviderDiagnostics) -> str:
    payload = {
        "tool": "themis",
        "workflow": "providers",
        "status": "blocked" if providers_exit_code(diagnostics) else "pass",
        "exit_code": providers_exit_code(diagnostics),
        "repository": str(diagnostics.repo),
        "config": asdict(diagnostics.config),
        "checks": [asdict(check) for check in diagnostics.checks],
        "safety_contract": [
            "providers are opt-in and disabled by default",
            "provider output may not override hard blockers",
            "provider use must be disclosed in provider-backed assistant output",
            "api key values are never printed",
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
