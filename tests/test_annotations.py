from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.annotations import render_annotations, render_github_annotation
from themis.policy import BLOCKER, INFO, WARNING, Finding


class AnnotationTests(unittest.TestCase):
    def test_github_annotation_maps_severity_and_file(self) -> None:
        annotation = render_github_annotation(Finding(BLOCKER, "missing-test", "No tests", file="src/app.py"))
        self.assertEqual(annotation, "::error title=missing-test,file=src/app.py::No tests")

    def test_github_annotation_escapes_message_and_properties(self) -> None:
        annotation = render_github_annotation(Finding(WARNING, "code:one,two", "Line 1\n100%", file="a:b,c.py"))
        self.assertIn("::warning title=code%3Aone%2Ctwo,file=a%3Ab%2Cc.py::", annotation)
        self.assertIn("Line 1%0A100%25", annotation)

    def test_render_annotations_supports_none_and_notice(self) -> None:
        self.assertEqual(render_annotations([Finding(INFO, "clean", "ok")], "none"), "")
        self.assertEqual(render_annotations([Finding(INFO, "clean", "ok")], "github"), "::notice title=clean::ok\n")


if __name__ == "__main__":
    unittest.main()
