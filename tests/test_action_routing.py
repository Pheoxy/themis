from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest


class ActionRoutingTests(unittest.TestCase):
    def test_validate_route_includes_gate_flags(self) -> None:
        result = run_action_route(
            {
                "INPUT_WORKFLOW": "validate",
                "INPUT_BASE": "origin/main",
                "INPUT_BODY_FILE": "pr-body.md",
                "INPUT_EVIDENCE": "nix flake check passed",
                "INPUT_HUMAN_AUTHORED": "true",
                "INPUT_RUN_CHECKS": "true",
                "INPUT_FORMAT": "markdown",
                "INPUT_ANNOTATIONS": "github",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        argv = result.argv
        self.assertIn("validate", argv)
        self.assertIn("--base", argv)
        self.assertIn("origin/main", argv)
        self.assertIn("--body-file", argv)
        self.assertIn("--evidence", argv)
        self.assertIn("--human-authored", argv)
        self.assertIn("--annotations", argv)
        self.assertIn("--run-checks", argv)
        self.assertEqual(result.outputs["status"], "pass")
        self.assertEqual(result.outputs["exit-code"], "0")
        self.assertEqual(result.outputs["report"], "report.md")

    def test_validate_route_outputs_blocked_status_on_nonzero_exit(self) -> None:
        result = run_action_route(
            {
                "THEMIS_FAKE_EXIT": "2",
            }
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.outputs["status"], "blocked")
        self.assertEqual(result.outputs["exit-code"], "2")
        self.assertEqual(result.outputs["report"], "report.md")

    def test_validate_route_ignores_draft_pr_only_flags(self) -> None:
        result = run_action_route(
            {
                "INPUT_WORKFLOW": "validate",
                "INPUT_TITLE": "Draft title",
                "INPUT_BASE_BRANCH": "main",
                "INPUT_HEAD_BRANCH": "feature",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--title", result.argv)
        self.assertNotIn("--base-branch", result.argv)
        self.assertNotIn("--head-branch", result.argv)

    def test_draft_pr_route_includes_draft_pr_only_flags(self) -> None:
        result = run_action_route(
            {
                "INPUT_DRAFT_PR": "true",
                "INPUT_BODY_FILE": "pr-body.md",
                "INPUT_TITLE": "Draft title",
                "INPUT_BASE_BRANCH": "main",
                "INPUT_HEAD_BRANCH": "feature",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pull-request", result.argv)
        self.assertIn("draft", result.argv)
        self.assertIn("--title", result.argv)
        self.assertIn("Draft title", result.argv)
        self.assertIn("--base-branch", result.argv)
        self.assertIn("main", result.argv)
        self.assertIn("--head-branch", result.argv)
        self.assertIn("feature", result.argv)

    def test_draft_pr_route_requires_body_file(self) -> None:
        result = run_action_route(
            {
                "INPUT_DRAFT_PR": "true",
                "INPUT_BODY_FILE": "",
            }
        )

        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.argv, [])
        self.assertIn("draft-pr requires body-file", result.stderr)

    def test_config_check_route_excludes_gate_flags(self) -> None:
        result = run_action_route(
            {
                "INPUT_WORKFLOW": "config-check",
                "INPUT_BASE": "origin/main",
                "INPUT_BODY_FILE": "pr-body.md",
                "INPUT_EVIDENCE": "nix flake check passed",
                "INPUT_EVIDENCE_FILE": "evidence.txt",
                "INPUT_HUMAN_AUTHORED": "true",
                "INPUT_RUN_CHECKS": "true",
                "INPUT_FORMAT": "json",
                "INPUT_ANNOTATIONS": "github",
                "INPUT_TITLE": "Draft title",
                "INPUT_BASE_BRANCH": "main",
                "INPUT_HEAD_BRANCH": "feature",
            }
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.argv,
            [
                "run",
                str(Path(__file__).resolve().parents[1]),
                "--",
                "config",
                "check",
                "--repo",
                ".",
                "--output",
                "report.md",
                "--format",
                "json",
            ],
        )

    def test_config_check_rejects_gate_only_output_formats(self) -> None:
        result = run_action_route(
            {
                "INPUT_WORKFLOW": "config-check",
                "INPUT_FORMAT": "comment",
            }
        )

        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.argv, [])
        self.assertIn("Unsupported format for config-check", result.stderr)

    def test_self_check_rejects_gate_only_output_formats(self) -> None:
        result = run_action_route(
            {
                "INPUT_WORKFLOW": "self-check",
                "INPUT_FORMAT": "comment",
            }
        )

        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.argv, [])
        self.assertIn("Unsupported format for self-check", result.stderr)


class ActionCommentTests(unittest.TestCase):
    def test_comment_step_uses_explicit_pr_number(self) -> None:
        result = run_comment_step({"INPUT_PR_NUMBER": "42", "EVENT_PR_NUMBER": "99"}, report_exists=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.argv, ["pr", "comment", "42", "--body-file", "report.md"])

    def test_comment_step_falls_back_to_event_pr_number(self) -> None:
        result = run_comment_step({"INPUT_PR_NUMBER": "", "EVENT_PR_NUMBER": "99"}, report_exists=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.argv, ["pr", "comment", "99", "--body-file", "report.md"])

    def test_comment_step_skips_missing_report(self) -> None:
        result = run_comment_step({"INPUT_PR_NUMBER": "42", "EVENT_PR_NUMBER": ""}, report_exists=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.argv, [])


class ActionStepSummaryTests(unittest.TestCase):
    def test_step_summary_appends_markdown_report_directly(self) -> None:
        result = run_step_summary({"INPUT_FORMAT": "markdown"}, report="# Themis\n", report_exists=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.summary, "# Themis\n")

    def test_step_summary_wraps_json_report_in_fence(self) -> None:
        result = run_step_summary({"INPUT_FORMAT": "json"}, report='{"status":"pass"}\n', report_exists=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.summary, '## Themis json output\n\n```json\n{"status":"pass"}\n\n```\n')

    def test_step_summary_wraps_comment_report_in_fence(self) -> None:
        result = run_step_summary({"INPUT_FORMAT": "comment"}, report="Blocked\n", report_exists=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.summary, "## Themis comment output\n\n```comment\nBlocked\n\n```\n")

    def test_step_summary_skips_missing_report(self) -> None:
        result = run_step_summary({"INPUT_FORMAT": "markdown"}, report="", report_exists=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.summary, "")


class ActionRouteResult:
    def __init__(self, completed: subprocess.CompletedProcess[str], argv: list[str], outputs: dict[str, str] | None = None) -> None:
        self.returncode = completed.returncode
        self.stderr = completed.stderr
        self.argv = argv
        self.outputs = outputs or {}


class ActionSummaryResult:
    def __init__(self, completed: subprocess.CompletedProcess[str], summary: str) -> None:
        self.returncode = completed.returncode
        self.stderr = completed.stderr
        self.summary = summary


def run_action_route(overrides: dict[str, str]) -> ActionRouteResult:
    root = Path(__file__).resolve().parents[1]
    script = extract_action_script(root / "action.yml", "Validate upstream readiness")
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        capture = tmp / "argv.txt"
        output = tmp / "github-output.txt"
        fake_nix = bin_dir / "nix"
        fake_nix.write_text(
            f"#!{sys.executable}\n"
            "from pathlib import Path\n"
            "import os\n"
            "import sys\n"
            "Path(os.environ['THEMIS_CAPTURE']).write_text('\\n'.join(sys.argv[1:]) + '\\n', encoding='utf-8')\n"
            "raise SystemExit(int(os.environ.get('THEMIS_FAKE_EXIT', '0')))\n",
            encoding="utf-8",
        )
        fake_nix.chmod(0o755)
        route_script = tmp / "route.sh"
        route_script.write_text(script, encoding="utf-8")
        route_script.chmod(0o755)

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
                "GITHUB_ACTION_PATH": str(root),
                "GITHUB_OUTPUT": str(output),
                "THEMIS_CAPTURE": str(capture),
                "INPUT_REPO": ".",
                "INPUT_BASE": "",
                "INPUT_BODY_FILE": "",
                "INPUT_EVIDENCE": "",
                "INPUT_EVIDENCE_FILE": "",
                "INPUT_HUMAN_AUTHORED": "false",
                "INPUT_RUN_CHECKS": "true",
                "INPUT_WORKFLOW": "validate",
                "INPUT_OUTPUT": "report.md",
                "INPUT_FORMAT": "markdown",
                "INPUT_ANNOTATIONS": "github",
                "INPUT_DRAFT_PR": "false",
                "INPUT_TITLE": "",
                "INPUT_BASE_BRANCH": "",
                "INPUT_HEAD_BRANCH": "",
            }
        )
        env.update(overrides)
        completed = subprocess.run(["bash", str(route_script)], cwd=root, env=env, text=True, capture_output=True)
        argv = capture.read_text(encoding="utf-8").splitlines() if capture.exists() else []
        outputs = parse_github_output(output)
        return ActionRouteResult(completed, argv, outputs)


def run_step_summary(overrides: dict[str, str], *, report: str, report_exists: bool) -> ActionSummaryResult:
    root = Path(__file__).resolve().parents[1]
    script = extract_action_script(root / "action.yml", "Write step summary")
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        route_script = tmp / "summary.sh"
        route_script.write_text(script, encoding="utf-8")
        route_script.chmod(0o755)
        summary = tmp / "summary.md"
        if report_exists:
            (tmp / "report.out").write_text(report, encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "GITHUB_STEP_SUMMARY": str(summary),
                "INPUT_OUTPUT": "report.out",
                "INPUT_FORMAT": "markdown",
            }
        )
        env.update(overrides)
        completed = subprocess.run(["bash", str(route_script)], cwd=tmp, env=env, text=True, capture_output=True)
        summary_text = summary.read_text(encoding="utf-8") if summary.exists() else ""
        return ActionSummaryResult(completed, summary_text)


def run_comment_step(overrides: dict[str, str], *, report_exists: bool) -> ActionRouteResult:
    root = Path(__file__).resolve().parents[1]
    script = extract_action_script(root / "action.yml", "Comment on pull request")
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        bin_dir = tmp / "bin"
        bin_dir.mkdir()
        capture = tmp / "gh-argv.txt"
        fake_gh = bin_dir / "gh"
        fake_gh.write_text(
            f"#!{sys.executable}\n"
            "from pathlib import Path\n"
            "import os\n"
            "import sys\n"
            "Path(os.environ['THEMIS_CAPTURE']).write_text('\\n'.join(sys.argv[1:]) + '\\n', encoding='utf-8')\n"
            "raise SystemExit(int(os.environ.get('THEMIS_FAKE_GH_EXIT', '0')))\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        route_script = tmp / "comment.sh"
        route_script.write_text(script, encoding="utf-8")
        route_script.chmod(0o755)
        if report_exists:
            (tmp / "report.md").write_text("# report\n", encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
                "THEMIS_CAPTURE": str(capture),
                "INPUT_OUTPUT": "report.md",
                "INPUT_PR_NUMBER": "",
                "EVENT_PR_NUMBER": "",
            }
        )
        env.update(overrides)
        completed = subprocess.run(["bash", str(route_script)], cwd=tmp, env=env, text=True, capture_output=True)
        argv = capture.read_text(encoding="utf-8").splitlines() if capture.exists() else []
        return ActionRouteResult(completed, argv)


def parse_github_output(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    output: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        output[key] = value
    return output


def extract_action_script(action_path: Path, step_name: str) -> str:
    lines = action_path.read_text(encoding="utf-8").splitlines()
    for step_index, line in enumerate(lines):
        if line != f"    - name: {step_name}":
            continue
        for index in range(step_index + 1, len(lines)):
            if lines[index].startswith("    - name:"):
                break
            if lines[index] == "      run: |":
                body: list[str] = []
                for body_line in lines[index + 1 :]:
                    if body_line.startswith("    - name:"):
                        break
                    body.append(body_line[8:] if body_line.startswith("        ") else body_line)
                return "\n".join(body) + "\n"
    raise AssertionError(f"could not find action script for step: {step_name}")


if __name__ == "__main__":
    unittest.main()
