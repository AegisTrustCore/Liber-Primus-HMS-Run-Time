import json
import unittest
from pathlib import Path

from scripts.build_research_archive import ROOT, validate_archive


class ResearchArchiveTests(unittest.TestCase):
    def load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_archive_is_internally_consistent(self):
        self.assertEqual(validate_archive(), [])

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

    def test_run_set_zip_contains_member_packages(self):
        import zipfile

        bundle = ROOT / "research/runsets/RSET-0001/RSET-0001.zip"
        with zipfile.ZipFile(bundle) as archive:
            names = set(archive.namelist())
        self.assertIn("RSET-0001/bundles/RUN-0001.zip", names)
        self.assertIn("RSET-0001/bundles/RES-0001.zip", names)


if __name__ == "__main__":
    unittest.main()
