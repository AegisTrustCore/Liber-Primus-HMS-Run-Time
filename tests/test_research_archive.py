import json
import unittest
from pathlib import Path

from scripts.build_research_archive import ROOT, canonical_file_bytes, validate_archive


class ResearchArchiveTests(unittest.TestCase):
    def load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_archive_is_internally_consistent(self):
        self.assertEqual(validate_archive(), [])

    def test_archive_text_bytes_are_platform_canonical(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            lf = Path(directory) / "lf.txt"
            crlf = Path(directory) / "crlf.txt"
            lf.write_bytes(b"alpha\nbeta\n")
            crlf.write_bytes(b"alpha\r\nbeta\r\n")
            self.assertEqual(canonical_file_bytes(lf), canonical_file_bytes(crlf))

    def test_run_result_links_are_reciprocal(self):
        run = self.load("research/runs/RUN-0001/manifest.json")
        result = self.load("research/results/RES-0001/manifest.json")
        self.assertIn(result["id"], run["result_ids"])
        self.assertIn(run["id"], result["supporting_runs"])

    def test_source_inventory_is_not_reported_as_results(self):
        archive = self.load("research/archive-index.json")
        self.assertGreater(archive["source_artifact_count"], archive["published_results"])
        self.assertIn("not a result count", archive["source_artifact_count_note"])

    def test_initial_run_set_remains_staged(self):
        run_set = self.load("research/runsets/RSET-0001/manifest.json")
        self.assertEqual(run_set["publication_status"], "STAGED")

    def test_page_32_closure_run_set_is_published(self):
        run_set = self.load("research/runsets/RSET-0002/manifest.json")
        self.assertEqual(run_set["publication_status"], "PUBLISHED")

    def test_e1059_run_set_remains_staged(self):
        run_set = self.load("research/runsets/RSET-0003/manifest.json")
        self.assertEqual(run_set["publication_status"], "STAGED")

    def test_public_status_matches_archive_counts_and_run_set_states(self):
        archive = self.load("research/archive-index.json")
        project_status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        research_index = (ROOT / "RESEARCH_INDEX.md").read_text(encoding="utf-8")

        summary = (
            f"{archive['published_runs']} published Runs, "
            f"{archive['published_results']} published Results, "
            f"{archive['published_capsules']} published Capsules"
        )
        self.assertIn(summary, project_status)
        self.assertIn("`RSET-0001` remains `STAGED`", project_status)
        self.assertIn("`RSET-0002` is `PUBLISHED`", project_status)
        self.assertIn("`RSET-0003` remains `STAGED`", project_status)
        self.assertIn("Eight Results", research_index)
        self.assertNotIn("draft PR #6", project_status)

    def test_e1059_public_verifier(self):
        import subprocess
        import sys

        verifier = ROOT / "research/runs/RUN-0008/evidence/verify_e1059.py"
        completed = subprocess.run(
            [sys.executable, str(verifier)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["passed"], 13)
        self.assertEqual(result["failed"], 0)

    def test_run_set_zip_contains_member_packages(self):
        import zipfile

        bundle = ROOT / "research/runsets/RSET-0001/RSET-0001.zip"
        with zipfile.ZipFile(bundle) as archive:
            names = set(archive.namelist())
        self.assertIn("RSET-0001/bundles/RUN-0001.zip", names)
        self.assertIn("RSET-0001/bundles/RES-0001.zip", names)

    def test_published_run_set_contains_reader_guide(self):
        import zipfile

        bundle = ROOT / "research/runsets/RSET-0002/RSET-0002.zip"
        with zipfile.ZipFile(bundle) as archive:
            names = set(archive.namelist())
        self.assertIn("RSET-0002/START-HERE.md", names)
        self.assertIn("RSET-0002/RELEASE-NOTES.txt", names)


if __name__ == "__main__":
    unittest.main()
