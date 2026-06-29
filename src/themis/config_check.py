from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .policy import PolicyConfig
from .providers import load_provider_config


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


@dataclass(frozen=True)
class ConfigCheck:
    status: str
    code: str
    message: str
    detail: str | None = None


@dataclass(frozen=True)
class ConfigInspection:
    repo: Path
    path: Path
    checks: list[ConfigCheck]


def inspect_config(repo: Path) -> ConfigInspection:
    path = repo / ".themis.toml"
    checks: list[ConfigCheck] = []
    if not path.exists():
        checks.append(ConfigCheck(WARN, "config-missing", "No `.themis.toml` found; built-in defaults will be used."))
        return ConfigInspection(repo=repo, path=path, checks=checks)

    try:
        PolicyConfig.load(repo)
        checks.append(ConfigCheck(PASS, "policy-config", "Policy configuration is valid.", str(path)))
    except ValueError as exc:
        checks.append(ConfigCheck(FAIL, "policy-config", "Policy configuration is invalid.", str(exc)))

    try:
        load_provider_config(repo)
        checks.append(ConfigCheck(PASS, "ai-config", "AI provider configuration is valid.", str(path)))
    except ValueError as exc:
        checks.append(ConfigCheck(FAIL, "ai-config", "AI provider configuration is invalid.", str(exc)))

    return ConfigInspection(repo=repo, path=path, checks=checks)


def config_exit_code(inspection: ConfigInspection) -> int:
    return 2 if any(check.status == FAIL for check in inspection.checks) else 0


def render_config_markdown(inspection: ConfigInspection) -> str:
    status = "BLOCKED" if config_exit_code(inspection) else "PASS"
    lines = [
        "# Themis Config Check",
        "",
        f"Status: **{status}**",
        "",
        f"Repository: `{inspection.repo}`",
        f"Config: `{inspection.path}`",
        "",
        "## Checks",
        "",
    ]
    for check in inspection.checks:
        lines.append(f"- **{check.status}** `{check.code}`: {check.message}")
        if check.detail:
            lines.append(f"  Detail: `{check.detail}`")
    lines.extend(
        [
            "",
            "## Schema",
            "",
            "Use `docs/schema/themis.schema.json` for editor and CI validation of supported keys.",
            "",
        ]
    )
    return "\n".join(lines)


def render_config_json(inspection: ConfigInspection) -> str:
    payload = {
        "tool": "themis",
        "workflow": "config check",
        "status": "blocked" if config_exit_code(inspection) else "pass",
        "exit_code": config_exit_code(inspection),
        "repository": str(inspection.repo),
        "config": str(inspection.path),
        "checks": [asdict(check) for check in inspection.checks],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
