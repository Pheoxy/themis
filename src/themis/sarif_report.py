from __future__ import annotations

import json
from typing import Any

from . import __version__
from .policy import BLOCKER, INFO, WARNING, Finding, ValidationInput


def render_sarif(data: ValidationInput, findings: list[Finding]) -> str:
    payload: dict[str, Any] = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Themis",
                        "informationUri": "https://github.com/OWNER/themis",
                        "version": __version__,
                        "rules": rules(findings),
                    }
                },
                "automationDetails": {"id": "themis/upstream-gate"},
                "invocations": [
                    {
                        "executionSuccessful": not any(finding.severity == BLOCKER for finding in findings),
                        "workingDirectory": {"uri": str(data.repo)},
                    }
                ],
                "results": [result(finding) for finding in findings],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def rules(findings: list[Finding]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for finding in findings:
        if finding.code in seen:
            continue
        seen.add(finding.code)
        output.append(
            {
                "id": finding.code,
                "name": finding.code,
                "shortDescription": {"text": finding.message},
                "defaultConfiguration": {"level": level(finding.severity)},
            }
        )
    return output


def result(finding: Finding) -> dict[str, Any]:
    item: dict[str, Any] = {
        "ruleId": finding.code,
        "level": level(finding.severity),
        "message": {"text": message(finding)},
    }
    if finding.file:
        item["locations"] = [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.file},
                    "region": {"startLine": 1},
                }
            }
        ]
    return item


def level(severity: str) -> str:
    if severity == BLOCKER:
        return "error"
    if severity == WARNING:
        return "warning"
    if severity == INFO:
        return "note"
    return "note"


def message(finding: Finding) -> str:
    if finding.detail:
        return f"{finding.message}\n{finding.detail}"
    return finding.message
