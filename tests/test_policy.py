from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import ChangedFile, Numstat
from themis.policy import BLOCKER, PolicyConfig, ValidationInput, validate


def make_input(tmp: Path, *, diff: str, files: list[ChangedFile], pr: str = "", evidence: str = "") -> ValidationInput:
    return ValidationInput(
        repo=tmp,
        base="origin/main",
        changed_files=files,
        numstat=[Numstat(path=item.path, added=1, deleted=0) for item in files],
        diff_text=diff,
        tracked_files=[item.path for item in files],
        commits=[],
        pr_description=pr,
        test_evidence=evidence,
        ai_assisted=True,
        check_results=[],
    )


class PolicyTests(unittest.TestCase):
    def test_ai_assisted_requires_disclosure_and_accountability(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            data = make_input(tmp, diff="", files=[ChangedFile("src/app.py", "M")], evidence="pytest passed")
            findings = validate(data, PolicyConfig(require_test_changes_for_code=False))
            codes = {item.code for item in findings if item.severity == BLOCKER}
            self.assertIn("missing-ai-disclosure", codes)
            self.assertIn("missing-human-accountability", codes)

    def test_blocks_placeholder_code(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Please test changes.\n", encoding="utf-8")
            placeholder = "TO" + "DO"
            diff = f"+++ b/src/app.py\n+def run():\n+    # {placeholder} fix this later\n+    return True\n"
            pr = "AI assistance: used.\n\nHuman accountability: I own every line."
            data = make_input(tmp, diff=diff, files=[ChangedFile("src/app.py", "M")], pr=pr, evidence="pytest passed")
            findings = validate(data, PolicyConfig(require_test_changes_for_code=False))
            self.assertIn("placeholder-in-code", {item.code for item in findings if item.severity == BLOCKER})

    def test_allows_placeholder_word_in_explanation_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            diff = '+++ b/src/themis/explain.py\n+    "placeholder-in-code": FindingExplanation(\n+        "Code contains placeholder or cleanup language.",\n'
            pr = "AI assistance: Used for implementation suggestions and reviewed manually.\n\nHuman accountability: I own every line and take responsibility for tests."
            data = make_input(tmp, diff=diff, files=[ChangedFile("src/themis/explain.py", "M")], pr=pr, evidence="nix flake check passed")
            findings = validate(data, PolicyConfig(require_test_changes_for_code=False))
            self.assertNotIn("placeholder-in-code", {item.code for item in findings if item.severity == BLOCKER})

    def test_ai_assisted_blocks_placeholder_disclosure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            pr = "AI assistance: used\n\nHuman accountability: I own every line and tested it."
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertIn("weak-ai-disclosure", {item.code for item in findings if item.severity == BLOCKER})

    def test_ai_assisted_blocks_weak_accountability(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            pr = "AI assistance: Used for implementation suggestions and reviewed manually.\n\nHuman accountability: yes"
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertIn("weak-human-accountability", {item.code for item in findings if item.severity == BLOCKER})

    def test_accountability_language_does_not_forbid_ai(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("AI use must be disclosed.\n", encoding="utf-8")
            (tmp / ".github").mkdir()
            (tmp / ".github" / "pull_request_template.md").write_text("Human accountability: State that you, not Themis or any AI tool, take responsibility.\n", encoding="utf-8")
            pr = "AI assistance: Used for implementation suggestions and reviewed manually.\n\nHuman accountability: I own every line and take responsibility for tests."
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertNotIn("upstream-forbids-ai", {item.code for item in findings if item.severity == BLOCKER})

    def test_blocks_weak_test_evidence_for_code_changes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            pr = "AI assistance: Used for implementation suggestions and reviewed manually.\n\nHuman accountability: I own every line and take responsibility for tests."
            data = make_input(tmp, diff="+++ b/src/app.py\n+return 1\n", files=[ChangedFile("src/app.py", "M")], pr=pr, evidence="looks good")
            findings = validate(data, PolicyConfig(require_test_changes_for_code=False))
            self.assertIn("weak-test-evidence", {item.code for item in findings if item.severity == BLOCKER})

    def test_missing_upstream_rules_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            pr = "AI assistance: used.\n\nHuman accountability: I own every line."
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertIn("missing-upstream-rules", {item.code for item in findings if item.severity == BLOCKER})

    def test_project_changelog_rule_is_inferred_from_docs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Code changes must update release notes.\n", encoding="utf-8")
            pr = "AI assistance: used.\n\nHuman accountability: I own every line."
            data = make_input(tmp, diff="+++ b/src/app.py\n+return 1\n", files=[ChangedFile("src/app.py", "M")], pr=pr, evidence="pytest passed")
            findings = validate(data, PolicyConfig(require_test_changes_for_code=False))
            self.assertIn("missing-changelog-decision", {item.code for item in findings if item.severity == BLOCKER})

    def test_project_pr_template_checklist_is_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / ".github").mkdir()
            (tmp / ".github" / "pull_request_template.md").write_text("- [ ] I ran tests\n", encoding="utf-8")
            pr = "AI assistance: used.\n\nHuman accountability: I own every line."
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertIn("pr-template-not-acknowledged", {item.code for item in findings if item.severity == BLOCKER})

    def test_issue_templates_do_not_create_pr_issue_link_rule(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            issue_templates = tmp / ".github" / "ISSUE_TEMPLATE"
            issue_templates.mkdir(parents=True)
            (issue_templates / "bug_report.md").write_text("Link the related pull request for this issue.\n", encoding="utf-8")
            pr = "AI assistance: Used for implementation suggestions and reviewed manually.\n\nHuman accountability: I own every line and take responsibility for tests."
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertNotIn("missing-issue-link", {item.code for item in findings if item.severity == BLOCKER})

    def test_code_of_conduct_does_not_create_pr_issue_link_rule(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            (tmp / "CODE_OF_CONDUCT.md").write_text("Maintainers may close issues when repeated patch submissions harm the project.\n", encoding="utf-8")
            pr = "AI assistance: Used for implementation suggestions and reviewed manually.\n\nHuman accountability: I own every line and take responsibility for tests."
            data = make_input(tmp, diff="", files=[ChangedFile("README.md", "M")], pr=pr)
            findings = validate(data, PolicyConfig())
            self.assertNotIn("missing-issue-link", {item.code for item in findings if item.severity == BLOCKER})

    def test_human_authored_with_test_evidence_can_pass_basic_gate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            (tmp / "CONTRIBUTING.md").write_text("Run tests before submitting.\n", encoding="utf-8")
            data = ValidationInput(
                repo=tmp,
                base="origin/main",
                changed_files=[ChangedFile("src/app.py", "M"), ChangedFile("tests/test_app.py", "M")],
                numstat=[Numstat("src/app.py", 1, 0), Numstat("tests/test_app.py", 1, 0)],
                diff_text="+++ b/src/app.py\n+return 1\n+++ b/tests/test_app.py\n+assert True\n",
                tracked_files=[],
                commits=[],
                pr_description="",
                test_evidence="python -m unittest passed",
                ai_assisted=False,
                check_results=[],
            )
            findings = validate(data, PolicyConfig())
            self.assertNotIn(BLOCKER, {item.severity for item in findings})


if __name__ == "__main__":
    unittest.main()
