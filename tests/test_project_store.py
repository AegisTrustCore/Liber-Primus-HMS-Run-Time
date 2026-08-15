from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hms_tools.project import ProjectError, ProjectStore, create_result_envelope, validate_result_envelope
from hms_tools.runtime import create_job, execute_job


ROOT = Path(__file__).resolve().parents[1]


class ProjectStoreTests(unittest.TestCase):
    def test_create_open_and_layout_do_not_copy_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            store = ProjectStore.create(root, "LP Study", created_at="2026-08-14T00:00:00Z", manifest_ref="LP-75-IMAGES-v1.0.0.json", manifest_sha256="0" * 64)
            self.assertEqual(ProjectStore.open(root).project, store.project)
            self.assertEqual({path.name for path in root.iterdir()}, {"project.json","settings.json","index.json","runs","results","exports","notes"})
            self.assertFalse(any(path.suffix.lower() in {".jpg",".png"} for path in root.rglob("*")))

    def test_runtime_execution_is_saved_as_shared_envelope(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProjectStore.create(Path(directory) / "project", "GP", created_at="2026-08-14T00:00:00Z")
            job = create_job("F U/V TH", "tokens")
            runtime_result = execute_job(job)
            envelope = store.save_execution(job, runtime_result, instrument_id="public-gp29-calculator", instrument_version="0.1.1")
            self.assertEqual(envelope["evidence_label"], "CALCULATION_ONLY")
            self.assertEqual(envelope["payload"]["gp_sum"], 10)
            self.assertEqual(store.list_results(), [envelope])
            index = json.loads((store.root / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["runs"], [job["job_id"]])
            self.assertEqual(index["results"], [envelope["result_id"]])

    def test_result_tampering_is_rejected(self):
        envelope = create_result_envelope(project_id="PRJ-" + "A" * 16, instrument_id="test", instrument_version="1", operation="test", payload={"value":1}, evidence_label="EXPERIMENTAL", limitations=["Synthetic test."], created_at="2026-08-14T00:00:00Z")
        envelope["payload"]["value"] = 2
        with self.assertRaisesRegex(ProjectError, "digest"):
            validate_result_envelope(envelope)

    def test_signed_expedition_receipt_is_saved_without_plaintext(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProjectStore.create(Path(directory) / "project", "Expedition", created_at="2026-08-14T00:00:00Z")
            receipt = {
                "schema":"HMS_EXPEDITION_VERIFICATION_RECEIPT_V2",
                "receipt_id":"VRF-0123456789ABCDEF",
                "expedition_id":"XPD-0001",
                "client_version":"0.3.0",
                "accepted":True,
                "submission_sha256":"a" * 64,
                "verified_at":"2026-08-14T00:00:00Z",
                "verification_authority":"HMS_ENDEAVOUR",
                "signature_algorithm":"ED25519",
                "public_key_id":"ED25519-0123456789ABCDEF",
                "server_verified":True,
                "solution_disclosed":False,
                "receipt_signature":"synthetic-test-signature",
            }
            envelope = store.save_expedition_receipt(receipt, instrument_version="0.3.0")
            rendered = json.dumps(envelope)
            self.assertEqual(envelope["evidence_label"], "TRAINING_ONLY")
            self.assertEqual(envelope["operation"], "REMOTE_SEALED_VERIFICATION")
            self.assertEqual(envelope["payload"], receipt)
            self.assertNotIn("known answer plaintext", rendered)
            self.assertEqual(store.list_results(), [envelope])

    def test_project_folder_must_be_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "existing.txt").write_text("owned", encoding="utf-8")
            with self.assertRaisesRegex(ProjectError, "empty"):
                ProjectStore.create(root, "Unsafe")

    def test_cli_project_gp29_and_list_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            create = subprocess.run([sys.executable,"scripts/endeavour_lite.py","create",str(project),"--name","CLI Test"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(create.returncode, 0, create.stderr)
            calculate = subprocess.run([sys.executable,"scripts/endeavour_lite.py","gp29",str(project),"F U/V TH","--mode","tokens"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(calculate.returncode, 0, calculate.stderr)
            self.assertEqual(json.loads(calculate.stdout)["payload"]["gp_sum"], 10)
            listing = subprocess.run([sys.executable,"scripts/endeavour_lite.py","list",str(project)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(listing.returncode, 0, listing.stderr)
            self.assertEqual(len(json.loads(listing.stdout)), 1)

    def test_cli_expedition_fails_closed_without_approved_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            ProjectStore.create(project, "Closed Campaign", created_at="2026-08-14T00:00:00Z")
            completed = subprocess.run([sys.executable,"scripts/endeavour_lite.py","expedition",str(project),"attempt"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 2)
            self.assertIn("campaign remains closed", completed.stderr)
            self.assertEqual(ProjectStore.open(project).list_results(), [])


if __name__ == "__main__":
    unittest.main()
