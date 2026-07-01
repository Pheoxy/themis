from pathlib import Path
import unittest


class PublicMetadataTests(unittest.TestCase):
    def test_public_metadata_uses_neutral_strict_language(self) -> None:
        root = Path(__file__).resolve().parents[1]
        public_files = (
            "README.md",
            "pyproject.toml",
            "action.yml",
            "flake.nix",
            "src/themis/__init__.py",
            "src/themis/cli.py",
            "docs/cli.md",
            "docs/configuration.md",
        )
        for relative in public_files:
            with self.subTest(relative=relative):
                text = (root / relative).read_text(encoding="utf-8").lower()
                self.assertNotIn("paranoid", text)
                self.assertNotIn("ai slop", text)


if __name__ == "__main__":
    unittest.main()
