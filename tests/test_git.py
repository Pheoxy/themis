from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import parse_numstat


class GitParsingTests(unittest.TestCase):
    def test_parse_numstat_handles_text_and_binary_files(self) -> None:
        stats = parse_numstat("3\t1\tsrc/app.py\n-\t-\timage.png\n")
        self.assertEqual(stats[0].path, "src/app.py")
        self.assertEqual(stats[0].added, 3)
        self.assertEqual(stats[0].deleted, 1)
        self.assertEqual(stats[1].path, "image.png")
        self.assertIsNone(stats[1].added)
        self.assertIsNone(stats[1].deleted)


if __name__ == "__main__":
    unittest.main()
