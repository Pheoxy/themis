from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shutil

from .git import GitError, current_branch, repo_root
from .policy import PolicyConfig, load_rule_docs
from .providers import inspect_providers


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


@dataclass(frozen=True)
class DoctorCheck:
    status: str
    code: str
    message: str
    detail: str | None = None


@dataclass(frozen=True)
class DoctorResult:
    repo: Path
    checks: list[DoctorCheck]


def run_doctor(repo: Path) -> DoctorResult:
    checks: list[DoctorCheck] = []
    try:
        root = repo_root(repo)
        checks.append(DoctorCheck(PASS, "git-repository", "Target path is inside a git repository.", str(root)))
    except GitError as exc:
        return DoctorResult(
            repo=repo,
            checks=[DoctorCheck(FAIL, "git-repository", "Target path is not a usable git repository.", str(exc))],
        )

    config_path = root / ".themis.toml"
    try:
        config = PolicyConfig.load(root)
        if config_path.exists():
            checks.append(DoctorCheck(PASS, "policy-config", "Loaded `.themis.toml` policy.", str(config_path)))
        else:
            checks.append(DoctorCheck(WARN, "policy-config", "No `.themis.toml` found; Themis will use built-in defaults."))
    except ValueError as exc:
        checks.append(DoctorCheck(FAIL, "policy-config", "Themis policy configuration is invalid.", str(exc)))
        config = PolicyConfig()

    rule_docs = load_rule_docs(root)
    if rule_docs:
        checks.append(DoctorCheck(PASS, "upstream-rules", f"Detected {len(rule_docs)} upstream rule document(s)."))
    elif config.require_upstream_rules:
        checks.append(DoctorCheck(FAIL, "upstream-rules", "No upstream rule documents detected and policy requires them."))
    else:
        checks.append(DoctorCheck(WARN, "upstream-rules", "No upstream rule documents detected."))

    checks.extend(tool_checks(config))
    checks.extend(provider_checks(root))
    checks.extend(repo_state_checks(root))
    if config.required_checks:
        checks.append(DoctorCheck(PASS, "required-checks", f"Configured required checks: {', '.join(config.required_checks)}"))
    else:
        checks.append(DoctorCheck(WARN, "required-checks", "No required checks are configured in `.themis.toml`."))
    return DoctorResult(repo=root, checks=checks)


def tool_checks(config: PolicyConfig) -> list[DoctorCheck]:
    checks = [tool_check("git", required=True), tool_check("gh", required=False)]
    if any("nix" in command.split()[:1] for command in config.required_checks):
        checks.append(tool_check("nix", required=True))
    return checks


def tool_check(name: str, *, required: bool) -> DoctorCheck:
    path = shutil.which(name)
    if path:
        return DoctorCheck(PASS, f"tool-{name}", f"Found `{name}`.", path)
    status = FAIL if required else WARN
    requirement = "required" if required else "optional"
    return DoctorCheck(status, f"tool-{name}", f"Missing {requirement} tool `{name}`.")


def provider_checks(root: Path) -> list[DoctorCheck]:
    try:
        diagnostics = inspect_providers(root)
    except ValueError as exc:
        return [DoctorCheck(FAIL, "ai-provider-config", "AI provider configuration is invalid.", str(exc))]
    output: list[DoctorCheck] = []
    for check in diagnostics.checks:
        output.append(DoctorCheck(check.status, f"ai-{check.code}", check.message, check.detail))
    return output


def repo_state_checks(root: Path) -> list[DoctorCheck]:
    try:
        branch = current_branch(root)
    except GitError as exc:
        return [DoctorCheck(WARN, "git-branch", "Could not determine current branch.", str(exc))]
    if branch:
        return [DoctorCheck(PASS, "git-branch", "Current branch detected.", branch)]
    return [DoctorCheck(WARN, "git-branch", "Repository appears to be in detached HEAD state.")]


def doctor_exit_code(result: DoctorResult) -> int:
    return 2 if any(check.status == FAIL for check in result.checks) else 0


def render_doctor_markdown(result: DoctorResult) -> str:
    status = "BLOCKED" if doctor_exit_code(result) else "PASS"
    lines = [
        "# Themis Doctor",
        "",
        f"Status: **{status}**",
        "",
        f"Repository: `{result.repo}`",
        "",
        "## Checks",
        "",
    ]
    for check in result.checks:
        lines.append(f"- **{check.status}** `{check.code}`: {check.message}")
        if check.detail:
            lines.append(f"  Detail: `{check.detail}`")
    lines.extend(
        [
            "",
            "## Next",
            "",
            "- Fix every `FAIL` before relying on Themis automation.",
            "- Review `WARN` entries before drafting or reviewing a PR.",
            "- Run `themis guide` or `themis validate` after diagnostics are clean.",
            "",
        ]
    )
    return "\n".join(lines)


def render_doctor_json(result: DoctorResult) -> str:
    payload = {
        "tool": "themis",
        "workflow": "doctor",
        "status": "blocked" if doctor_exit_code(result) else "pass",
        "exit_code": doctor_exit_code(result),
        "repository": str(result.repo),
        "checks": [asdict(check) for check in result.checks],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
