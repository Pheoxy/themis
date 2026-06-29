from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

from . import __version__
from .annotations import render_annotations
from .git import (
    ChangedFile,
    GitError,
    Numstat,
    changed_files,
    commits,
    current_branch,
    diff_text,
    last_commit_subject,
    numstat,
    repo_root,
    tracked_files,
)
from .policy import (
    BLOCKER,
    Finding,
    PolicyConfig,
    ValidationInput,
    run_required_checks,
    validate,
)
from .json_report import render_json
from .pr import DraftPrError, DraftPrOptions, build_pr_body, create_draft_pr, infer_pr_base
from .report import render_markdown
from .sarif_report import render_sarif


@dataclass(frozen=True)
class ValidationRun:
    root: Path
    config: PolicyConfig
    pr_description: str
    changed: list[ChangedFile]
    stats: list[Numstat]
    data: ValidationInput


@dataclass(frozen=True)
class GateRun:
    validation: ValidationRun
    findings: list[Finding]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="themis",
        description="Paranoid upstream PR validator for AI-assisted code.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate_parser = subcommands.add_parser("validate", aliases=["v"], help="Run the hard upstream-readiness gate.")
    add_validation_args(validate_parser)
    validate_parser.add_argument("--run-checks", action="store_true", help="Run required checks from .themis.toml in the target repo.")

    guide_parser = subcommands.add_parser("guide", aliases=["g"], help="Run the gate and generate an upstream readiness guide.")
    add_validation_args(guide_parser, base_default="origin/main")
    guide_parser.add_argument("--run-checks", action="store_true", help="Run required checks from .themis.toml in the target repo.")

    packet_parser = subcommands.add_parser(
        "maintainer-packet",
        aliases=["mp"],
        help="Run the gate and generate a maintainer-facing packet.",
    )
    add_validation_args(packet_parser, base_default="origin/main")
    packet_parser.add_argument("--run-checks", action="store_true", help="Run required checks from .themis.toml in the target repo.")

    pr_parser = subcommands.add_parser("pull-request", aliases=["pr"], help="Pull request workflows.")
    pr_subcommands = pr_parser.add_subparsers(dest="pr_command", required=True)
    draft_parser = pr_subcommands.add_parser("draft", aliases=["d"], help="Validate, run required checks, then create a draft PR.")
    add_validation_args(draft_parser, base_default="origin/main", require_pr_description=True)
    draft_parser.add_argument("--skip-checks", action="store_true", help="Do not run configured required checks. This usually causes a blocker when checks are configured.")
    draft_parser.add_argument("--title", help="Draft PR title. Defaults to the latest commit subject.")
    draft_parser.add_argument("--base-branch", help="Draft PR target branch. Defaults to --base with origin/ stripped.")
    draft_parser.add_argument("--head-branch", help="Draft PR source branch. Defaults to the current branch selected by gh.")

    docs_parser = subcommands.add_parser("docs", help="Documentation workflows.")
    docs_subcommands = docs_parser.add_subparsers(dest="docs_command", required=True)
    cli_docs_parser = docs_subcommands.add_parser("cli", help="Generate or check code-derived CLI reference docs.")
    cli_docs_mode = cli_docs_parser.add_mutually_exclusive_group()
    cli_docs_mode.add_argument("--write", action="store_true", help="Write generated CLI docs to disk.")
    cli_docs_mode.add_argument("--check", action="store_true", help="Fail if generated CLI docs differ from disk.")
    cli_docs_parser.add_argument("-p", "--path", type=Path, default=Path("docs/cli.md"), help="Generated docs path.")

    explain_parser = subcommands.add_parser("explain", help="Explain a Themis finding code and how to fix it.")
    explain_parser.add_argument("code", nargs="?", help="Finding code to explain. Omit to list known codes.")

    doctor_parser = subcommands.add_parser("doctor", help="Diagnose target repository and local Themis readiness.")
    doctor_parser.add_argument("-r", "--repo", type=Path, default=Path.cwd(), help="Target git repository to diagnose.")
    doctor_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Doctor output format.")
    doctor_parser.add_argument("-o", "--output", type=Path, help="Write doctor output to this path.")

    rules_parser = subcommands.add_parser("rules", help="Show effective policy and inferred upstream rules.")
    rules_parser.add_argument("-r", "--repo", type=Path, default=Path.cwd(), help="Target git repository to inspect.")
    rules_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Rules output format.")
    rules_parser.add_argument("-o", "--output", type=Path, help="Write rules output to this path.")

    providers_parser = subcommands.add_parser("providers", help="Inspect configured AI provider backend readiness.")
    providers_parser.add_argument("-r", "--repo", type=Path, default=Path.cwd(), help="Target git repository to inspect.")
    providers_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Providers output format.")
    providers_parser.add_argument("-o", "--output", type=Path, help="Write providers output to this path.")

    init_parser = subcommands.add_parser("init", help="Create starter Themis files in a target repository.")
    init_parser.add_argument("-r", "--repo", type=Path, default=Path.cwd(), help="Target repository to initialize.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    init_parser.add_argument("--no-body", action="store_true", help="Do not create a starter pull request body file.")

    completion_parser = subcommands.add_parser("completion", help="Print shell completion script.")
    completion_parser.add_argument("shell", choices=["bash", "zsh", "fish"], help="Shell to generate completions for.")
    return parser


def add_validation_args(parser: argparse.ArgumentParser, *, base_default: str | None = None, require_pr_description: bool = False) -> None:
    parser.add_argument("-r", "--repo", type=Path, default=Path.cwd(), help="Target git repository to validate.")
    parser.add_argument("-b", "--base", default=base_default, help="Base ref for PR diff, for example origin/main. Defaults to HEAD plus working tree changes.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ai", "--ai-assisted", dest="ai_assisted", action="store_true", help="Treat the patch as AI-assisted. This is the default.")
    mode.add_argument("--human", "--human-authored", dest="ai_assisted", action="store_false", help="Explicitly declare the patch was not AI-assisted.")
    parser.set_defaults(ai_assisted=True)
    parser.add_argument("-B", "--body-file", type=Path, required=require_pr_description, help="File containing the pull request body.")
    parser.add_argument("-e", "--evidence", default="", help="Short text proving which tests/checks passed.")
    parser.add_argument("-E", "--evidence-file", type=Path, help="File containing test/check evidence.")
    parser.add_argument("-o", "--output", type=Path, help="Write gate output to this path.")
    parser.add_argument("--format", choices=["markdown", "json", "sarif"], default="markdown", help="Output format for gate results.")
    parser.add_argument("--annotations", choices=["none", "github"], default="none", help="Emit CI annotations for findings.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "docs":
            from .docs import handle_cli_docs

            return handle_cli_docs(args)
        if args.command == "explain":
            from .explain import render_explanation

            print(render_explanation(args.code), end="")
            return 0
        if args.command == "doctor":
            from .doctor import doctor_exit_code, render_doctor_json, render_doctor_markdown, run_doctor

            result = run_doctor(args.repo.resolve())
            output = render_doctor_json(result) if args.format == "json" else render_doctor_markdown(result)
            write_output(output, args.output)
            return doctor_exit_code(result)
        if args.command == "rules":
            from .rules import inspect_rules, render_rules_json, render_rules_markdown, rules_exit_code

            root = repo_root(args.repo.resolve())
            inspection = inspect_rules(root, PolicyConfig.load(root))
            output = render_rules_json(inspection) if args.format == "json" else render_rules_markdown(inspection)
            write_output(output, args.output)
            return rules_exit_code(inspection)
        if args.command == "providers":
            from .providers import inspect_providers, providers_exit_code, render_providers_json, render_providers_markdown

            root = repo_root(args.repo.resolve())
            diagnostics = inspect_providers(root)
            output = render_providers_json(diagnostics) if args.format == "json" else render_providers_markdown(diagnostics)
            write_output(output, args.output)
            return providers_exit_code(diagnostics)
        if args.command == "init":
            from .init import init_repo

            result = init_repo(args.repo.resolve(), force=args.force, include_pr_body=not args.no_body)
            for path in result.written:
                print(f"created {path}")
            for path in result.skipped:
                print(f"skipped existing {path}")
            return 0
        if args.command == "completion":
            from .completion import render_completion

            print(render_completion(args.shell), end="")
            return 0
        if args.command in {"guide", "g", "maintainer-packet", "mp"}:
            from .guide import render_guide
            from .review import render_review_packet

            gate = evaluate_gate(args, run_checks=args.run_checks)
            run = gate.validation
            if args.command in {"maintainer-packet", "mp"}:
                markdown_output = render_review_packet(
                    run.root,
                    base=args.base,
                    changed=run.changed,
                    stats=run.stats,
                    config=run.config,
                    findings=gate.findings,
                )
                workflow = "maintainer-packet"
            else:
                markdown_output = render_guide(
                    run.root,
                    base=args.base,
                    changed=run.changed,
                    stats=run.stats,
                    config=run.config,
                    findings=gate.findings,
                )
                workflow = "guide"
            exit_code = gate_exit_code(gate.findings)
            output = render_gate_output(args.format, gate, workflow=workflow, exit_code=exit_code, markdown_output=markdown_output)
            write_output(output, args.output)
            write_annotations(gate.findings, args.annotations)
            return exit_code
        draft_pr = args.command in {"pull-request", "pr"} and args.pr_command in {"draft", "d"}
        run_checks = args.run_checks if args.command in {"validate", "v"} else not args.skip_checks
        gate = evaluate_gate(args, run_checks=run_checks)
        run = gate.validation
        markdown_report = render_markdown(run.data, gate.findings)
        exit_code = gate_exit_code(gate.findings)
        workflow = "pull-request draft" if draft_pr else "validate"
        draft_pr_url = None
        if not has_blockers(gate.findings) and draft_pr:
            title = args.title or last_commit_subject(run.root)
            pr_base = args.base_branch or infer_pr_base(args.base)
            pr_head = args.head_branch or current_branch(run.root) or None
            draft_pr_url = create_draft_pr(
                run.root,
                DraftPrOptions(
                    title=title,
                    base=pr_base,
                    head=pr_head,
                    body=build_pr_body(run.pr_description, markdown_report),
                ),
            )
        report = render_gate_output(
            args.format,
            gate,
            workflow=workflow,
            exit_code=exit_code,
            markdown_output=markdown_report,
            draft_pr_url=draft_pr_url,
        )
        write_output(report, args.output)
        write_annotations(gate.findings, args.annotations)
        if has_blockers(gate.findings):
            return exit_code
        if draft_pr and draft_pr_url and args.format == "markdown":
            print(draft_pr_url)
        return 0
    except (DraftPrError, GitError, OSError, ValueError) as exc:
        print(f"themis error: {exc}", file=sys.stderr)
        return 3


def read_optional(path: Path | None) -> str:
    if not path:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_validation_run(args: argparse.Namespace, *, run_checks: bool) -> ValidationRun:
    root = repo_root(args.repo.resolve())
    config = PolicyConfig.load(root)
    pr_description = read_optional(args.body_file)
    test_evidence = args.evidence
    if args.evidence_file:
        test_evidence = join_evidence(test_evidence, read_optional(args.evidence_file))
    checks = run_required_checks(root, config.required_checks) if run_checks else []
    changed = changed_files(root, args.base)
    stats = numstat(root, args.base)
    data = ValidationInput(
        repo=root,
        base=args.base,
        changed_files=changed,
        numstat=stats,
        diff_text=diff_text(root, args.base),
        tracked_files=tracked_files(root),
        commits=commits(root, args.base),
        pr_description=pr_description,
        test_evidence=test_evidence,
        ai_assisted=args.ai_assisted,
        check_results=checks,
    )
    return ValidationRun(
        root=root,
        config=config,
        pr_description=pr_description,
        changed=changed,
        stats=stats,
        data=data,
    )


def evaluate_gate(args: argparse.Namespace, *, run_checks: bool) -> GateRun:
    run = build_validation_run(args, run_checks=run_checks)
    return GateRun(validation=run, findings=validate(run.data, run.config))


def write_output(output: str, path: Path | None) -> None:
    if path:
        path.write_text(output, encoding="utf-8")
    else:
        print(output)


def write_annotations(findings: list[Finding], mode: str) -> None:
    annotations = render_annotations(findings, mode)
    if annotations:
        print(annotations, end="", file=sys.stderr)


def render_gate_output(
    output_format: str,
    gate: GateRun,
    *,
    workflow: str,
    exit_code: int,
    markdown_output: str,
    draft_pr_url: str | None = None,
) -> str:
    if output_format == "markdown":
        return markdown_output
    if output_format == "json":
        return render_json(gate.validation.data, gate.findings, workflow=workflow, exit_code=exit_code, draft_pr_url=draft_pr_url)
    if output_format == "sarif":
        return render_sarif(gate.validation.data, gate.findings)
    raise ValueError(f"unsupported output format: {output_format}")


def has_blockers(findings: list[Finding]) -> bool:
    return any(item.severity == BLOCKER for item in findings)


def gate_exit_code(findings: list[Finding]) -> int:
    return 2 if has_blockers(findings) else 0


def join_evidence(first: str, second: str) -> str:
    if first and second:
        return f"{first}\n{second}"
    return first or second


if __name__ == "__main__":
    raise SystemExit(main())
