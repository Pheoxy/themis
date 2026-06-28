import unittest

from themis.pr import build_pr_body, infer_pr_base


class DraftPrTests(unittest.TestCase):
    def test_infers_github_base_branch_from_origin_ref(self) -> None:
        self.assertEqual(infer_pr_base("origin/main"), "main")

    def test_infers_github_base_branch_from_remote_ref(self) -> None:
        self.assertEqual(infer_pr_base("refs/remotes/upstream/master"), "upstream/master")

    def test_build_pr_body_includes_existing_text_and_report(self) -> None:
        body = build_pr_body("AI assistance: disclosed", "# Report\n\nStatus: **PASS**")
        self.assertIn("AI assistance: disclosed", body)
        self.assertIn("Upstream Validator Report", body)
        self.assertIn("Status: **PASS**", body)


if __name__ == "__main__":
    unittest.main()
