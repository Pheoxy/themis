from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from .git import ChangedFile, Numstat
from .policy import BLOCKER, CheckResult, Finding, ValidationInput


def render_json(
    data: ValidationInput,
    findings: list[Finding],
    *,
    workflow: str,
    exit_code: int,
    draft_pr_url: str | None = None,
) -> str:
    blockers = [finding for finding in findings if finding.severity == BLOCKER]
    payload: dict[str, Any] = {
        "tool": "themis",
        "workflow": workflow,
        "status": "blocked" if blockers else "pass",
        "exit_code": exit_code,
        "accountability": "Themis is a gate result, not a certification. Accountability remains with the submitter and project review process.",
        "repository": str(data.repo),
        "base": data.base or "HEAD",
        "ai_assisted": data.ai_assisted,
        "changed_files": [changed_file_json(item) for item in data.changed_files],
        "line_stats": [numstat_json(item) for item in data.numstat],
        "findings": [finding_json(item) for item in findings],
        "required_checks": [check_json(item) for item in data.check_results],
    }
    if draft_pr_url:
        payload["draft_pr_url"] = draft_pr_url
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def changed_file_json(item: ChangedFile) -> dict[str, str]:
    return asdict(item)


def numstat_json(item: Numstat) -> dict[str, int | str | None]:
    return asdict(item)


def finding_json(item: Finding) -> dict[str, str | None]:
    return asdict(item)


def check_json(item: CheckResult) -> dict[str, bool | int | str]:
    return {
        "command": item.command,
        "returncode": item.returncode,
        "passed": item.returncode == 0,
        "output": item.output,
    }
