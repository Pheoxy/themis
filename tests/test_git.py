from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from themis.git import parse_commit_log, parse_numstat


class GitParsingTests(unittest.TestCase):
    def test_parse_numstat_handles_text_and_binary_files(self) -> None:
        stats = parse_numstat("3\t1\tsrc/app.py\n-\t-\timage.png\n")
        self.assertEqual(stats[0].path, "src/app.py")
        self.assertEqual(stats[0].added, 3)
        self.assertEqual(stats[0].deleted, 1)
        self.assertEqual(stats[1].path, "image.png")
        self.assertIsNone(stats[1].added)
        self.assertIsNone(stats[1].deleted)

    def test_parse_commit_log_records_merge_parents(self) -> None:
        output = (
            "abc123\x1fLock file maintenance\x1fparent1\x1fSigned-off-by: bot@example.com\x1e"
            "def456\x1fMerge branch 'main'\x1fparent1 parent2\x1f\x1e"
        )
        commits = parse_commit_log(output)
        self.assertEqual(commits[0].subject, "Lock file maintenance")
        self.assertFalse(commits[0].is_merge)
        self.assertEqual(commits[0].parent_shas, ("parent1",))
        self.assertTrue(commits[1].is_merge)
        self.assertEqual(commits[1].parent_shas, ("parent1", "parent2"))


if __name__ == "__main__":
    unittest.main()
