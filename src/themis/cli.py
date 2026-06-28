from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .git import GitError, changed_files, commits, current_branch, diff_text, last_commit_subject, numstat, repo_root, tracked_files
from .policy import BLOCKER, PolicyConfig, ValidationInput, run_required_checks, validate
from .pr import DraftPrError, DraftPrOptions, build_pr_body, create_draft_pr, infer_pr_base
from .report import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="themis",
        description="Paranoid upstream PR validator for AI-assisted code.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate_parser = subcommands.add_parser("validate", aliases=["check", "v"], help="Run the hard upstream-readiness gate.")
    add_validation_args(validate_parser)
    validate_parser.add_argument("--run-checks", action="store_true", help="Run required checks from .themis.toml in the target repo.")

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
    parser.add_argument("-o", "--output", type=Path, help="Write Markdown report to this path.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "docs":
            from .docs import handle_cli_docs

            return handle_cli_docs(args)
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
        draft_pr = args.command in {"pull-request", "pr"} and args.pr_command in {"draft", "d"}
        run_checks = args.run_checks if args.command == "validate" else not args.skip_checks
        root = repo_root(args.repo.resolve())
        config = PolicyConfig.load(root)
        pr_description = read_optional(args.body_file)
        test_evidence = args.evidence
        if args.evidence_file:
            test_evidence = join_evidence(test_evidence, read_optional(args.evidence_file))
        checks = run_required_checks(root, config.required_checks) if run_checks else []
        data = ValidationInput(
            repo=root,
            base=args.base,
            changed_files=changed_files(root, args.base),
            numstat=numstat(root, args.base),
            diff_text=diff_text(root, args.base),
            tracked_files=tracked_files(root),
            commits=commits(root, args.base),
            pr_description=pr_description,
            test_evidence=test_evidence,
            ai_assisted=args.ai_assisted,
            check_results=checks,
        )
        findings = validate(data, config)
        report = render_markdown(data, findings)
        if args.output:
            args.output.write_text(report, encoding="utf-8")
        else:
            print(report)
        if any(item.severity == BLOCKER for item in findings):
            return 2
        if draft_pr:
            title = args.title or last_commit_subject(root)
            pr_base = args.base_branch or infer_pr_base(args.base)
            pr_head = args.head_branch or current_branch(root) or None
            url = create_draft_pr(
                root,
                DraftPrOptions(
                    title=title,
                    base=pr_base,
                    head=pr_head,
                    body=build_pr_body(pr_description, report),
                ),
            )
            if url:
                print(url)
        return 0
    except (DraftPrError, GitError, OSError, ValueError) as exc:
        print(f"themis error: {exc}", file=sys.stderr)
        return 3


def read_optional(path: Path | None) -> str:
    if not path:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def join_evidence(first: str, second: str) -> str:
    if first and second:
        return f"{first}\n{second}"
    return first or second


if __name__ == "__main__":
    raise SystemExit(main())
