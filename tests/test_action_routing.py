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


class ActionRouteResult:
    def __init__(self, completed: subprocess.CompletedProcess[str], argv: list[str]) -> None:
        self.returncode = completed.returncode
        self.stderr = completed.stderr
        self.argv = argv


def run_action_route(overrides: dict[str, str]) -> ActionRouteResult:
    root = Path(__file__).resolve().parents[1]
    script = extract_validation_script(root / "action.yml")
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
        return ActionRouteResult(completed, argv)


def extract_validation_script(action_path: Path) -> str:
    lines = action_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == "      run: |" and index > 0 and "Validate upstream readiness" in "\n".join(lines[max(0, index - 20) : index]):
            body: list[str] = []
            for body_line in lines[index + 1 :]:
                if body_line.startswith("    - name:"):
                    break
                body.append(body_line[8:] if body_line.startswith("        ") else body_line)
            return "\n".join(body) + "\n"
    raise AssertionError("could not find action validation script")


if __name__ == "__main__":
    unittest.main()
