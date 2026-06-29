from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .doctor import DoctorResult, doctor_exit_code
from .policy import BLOCKER, Finding
from .providers import ProviderDiagnostics, providers_exit_code
from .rules import RulesInspection, rules_exit_code


@dataclass(frozen=True)
class SelfCheckResult:
    doctor: DoctorResult
    rules: RulesInspection
    providers: ProviderDiagnostics
    findings: list[Finding]


def self_check_exit_code(result: SelfCheckResult) -> int:
    if doctor_exit_code(result.doctor):
        return 2
    if rules_exit_code(result.rules):
        return 2
    if providers_exit_code(result.providers):
        return 2
    if any(finding.severity == BLOCKER for finding in result.findings):
        return 2
    return 0


def render_self_check_markdown(result: SelfCheckResult) -> str:
    status = "BLOCKED" if self_check_exit_code(result) else "PASS"
    blockers = [finding for finding in result.findings if finding.severity == BLOCKER]
    lines = [
        "# Themis Self-Check",
        "",
        f"Status: **{status}**",
        "",
        f"Repository: `{result.doctor.repo}`",
        "",
        "## Stage Summary",
        "",
        f"- Doctor: `{stage_status(doctor_exit_code(result.doctor))}`",
        f"- Rules: `{stage_status(rules_exit_code(result.rules))}`",
        f"- Providers: `{stage_status(providers_exit_code(result.providers))}`",
        f"- Gate: `{stage_status(2 if blockers else 0)}`",
        f"- Gate blockers: `{len(blockers)}`",
        "",
        "## Doctor Checks",
        "",
    ]
    for check in result.doctor.checks:
        lines.append(f"- **{check.status}** `{check.code}`: {check.message}")
    lines.extend(["", "## Inferred Rules", ""])
    for key, value in asdict(result.rules.inferred).items():
        lines.append(f"- `{key}`: `{str(value).lower()}`")
    lines.extend(["", "## Provider Checks", ""])
    for check in result.providers.checks:
        lines.append(f"- **{check.status}** `{check.code}`: {check.message}")
    lines.extend(["", "## Gate Findings", ""])
    if result.findings:
        for finding in result.findings:
            location = f" `{finding.file}`" if finding.file else ""
            lines.append(f"- **{finding.severity}** `{finding.code}`{location}: {finding.message}")
    else:
        lines.append("- No gate findings.")
    lines.extend(
        [
            "",
            "## Next",
            "",
            "- Fix every blocked stage before asking maintainers for deep review.",
            "- Treat self-check as a gate result, not a certification or transfer of accountability.",
            "",
        ]
    )
    return "\n".join(lines)


def render_self_check_json(result: SelfCheckResult) -> str:
    payload = {
        "tool": "themis",
        "workflow": "self-check",
        "status": "blocked" if self_check_exit_code(result) else "pass",
        "exit_code": self_check_exit_code(result),
        "repository": str(result.doctor.repo),
        "stages": {
            "doctor": stage_status(doctor_exit_code(result.doctor)),
            "rules": stage_status(rules_exit_code(result.rules)),
            "providers": stage_status(providers_exit_code(result.providers)),
            "gate": stage_status(2 if any(finding.severity == BLOCKER for finding in result.findings) else 0),
        },
        "doctor_checks": [asdict(check) for check in result.doctor.checks],
        "rule_docs": result.rules.rule_docs,
        "inferred_rules": asdict(result.rules.inferred),
        "provider_checks": [asdict(check) for check in result.providers.checks],
        "findings": [asdict(finding) for finding in result.findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def stage_status(exit_code: int) -> str:
    return "blocked" if exit_code else "pass"
