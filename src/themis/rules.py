from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from pathlib import Path

from .policy import (
    PolicyConfig,
    docs_require_changelog,
    docs_require_conventional_commits,
    docs_forbid_ai,
    docs_require_issue_link,
    is_process_rule_doc,
    load_rule_docs,
)


@dataclass(frozen=True)
class InferredRules:
    ai_disclosure_policy: bool
    ai_appears_forbidden: bool
    dco_or_signoff: bool
    changelog_or_release_notes: bool
    issue_or_reference_link: bool
    conventional_commits: bool
    pull_request_checklist: bool
    tests_mentioned: bool


@dataclass(frozen=True)
class RulesInspection:
    repo: Path
    config: PolicyConfig
    rule_docs: list[str]
    inferred: InferredRules


def inspect_rules(repo: Path, config: PolicyConfig) -> RulesInspection:
    docs = load_rule_docs(repo)
    docs_text = "\n".join(content for _, content in docs)
    process_text = "\n".join(content for name, content in docs if is_process_rule_doc(name))
    inferred = InferredRules(
        ai_disclosure_policy=bool(re.search(r"(?is)\b(ai|llm|generative|generated).{0,120}\b(disclos|indicat|mention|declare)", docs_text)),
        ai_appears_forbidden=docs_forbid_ai(docs_text),
        dco_or_signoff=bool(re.search(r"(?i)\b(dco|signed-off-by|developer certificate of origin)\b", docs_text)),
        changelog_or_release_notes=docs_require_changelog(process_text),
        issue_or_reference_link=docs_require_issue_link(process_text),
        conventional_commits=docs_require_conventional_commits(process_text),
        pull_request_checklist=any("pull_request_template" in name.lower() and "[ ]" in content for name, content in docs),
        tests_mentioned=bool(re.search(r"(?i)\b(test|tests|tested|pytest|unit test|integration test|ci)\b", docs_text)),
    )
    return RulesInspection(repo=repo, config=config, rule_docs=[name for name, _ in docs], inferred=inferred)


def rules_exit_code(inspection: RulesInspection) -> int:
    if inspection.config.require_upstream_rules and not inspection.rule_docs:
        return 2
    return 0


def render_rules_markdown(inspection: RulesInspection) -> str:
    status = "BLOCKED" if rules_exit_code(inspection) else "PASS"
    lines = [
        "# Themis Rules Inspection",
        "",
        f"Status: **{status}**",
        "",
        f"Repository: `{inspection.repo}`",
        "",
        "## Policy",
        "",
    ]
    for key, value in asdict(inspection.config).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Detected Rule Documents", ""])
    if inspection.rule_docs:
        for name in inspection.rule_docs:
            lines.append(f"- `{name}`")
    else:
        lines.append("- No rule documents detected.")
    lines.extend(["", "## Inferred Requirements", ""])
    for key, value in asdict(inspection.inferred).items():
        lines.append(f"- `{key}`: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            "These are inferred rules. Themis uses them to reduce process ambiguity, but the submitter and maintainers remain responsible for interpreting upstream requirements.",
            "",
        ]
    )
    return "\n".join(lines)


def render_rules_json(inspection: RulesInspection) -> str:
    payload = {
        "tool": "themis",
        "workflow": "rules",
        "status": "blocked" if rules_exit_code(inspection) else "pass",
        "exit_code": rules_exit_code(inspection),
        "repository": str(inspection.repo),
        "policy": asdict(inspection.config),
        "rule_docs": inspection.rule_docs,
        "inferred": asdict(inspection.inferred),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
