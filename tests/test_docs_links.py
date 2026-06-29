from pathlib import Path
import re
import unittest


class DocsLinksTests(unittest.TestCase):
    def test_readme_referenced_docs_exist(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        docs = sorted(set(re.findall(r"`(docs/[^`]+\.md)`", readme)))
        self.assertIn("docs/integrations.md", docs)
        self.assertIn("docs/release.md", docs)
        for relative in docs:
            with self.subTest(relative=relative):
                self.assertTrue((root / relative).is_file())


if __name__ == "__main__":
    unittest.main()
