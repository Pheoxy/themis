from __future__ import annotations

from .policy import BLOCKER, INFO, WARNING, Finding


def render_annotations(findings: list[Finding], mode: str) -> str:
    if mode == "none":
        return ""
    if mode != "github":
        raise ValueError(f"unsupported annotation mode: {mode}")
    return "\n".join(render_github_annotation(finding) for finding in findings) + ("\n" if findings else "")


def render_github_annotation(finding: Finding) -> str:
    command = github_command(finding.severity)
    properties = [f"title={escape_property(finding.code)}"]
    if finding.file:
        properties.append(f"file={escape_property(finding.file)}")
    message = finding.message
    if finding.detail:
        message = f"{message}\n{finding.detail}"
    return f"::{command} {','.join(properties)}::{escape_message(message)}"


def github_command(severity: str) -> str:
    if severity == BLOCKER:
        return "error"
    if severity == WARNING:
        return "warning"
    if severity == INFO:
        return "notice"
    return "notice"


def escape_message(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escape_property(value: str) -> str:
    return escape_message(value).replace(":", "%3A").replace(",", "%2C")
