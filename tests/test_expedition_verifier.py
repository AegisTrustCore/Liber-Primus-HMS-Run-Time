from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hms_tools.challenge_verifier import verify_answer
from hms_tools.expedition_verifier import build_receipt, packaged_self_test


ROOT = Path(__file__).resolve().parents[1]


class ExpeditionCustomerVerifierTests(unittest.TestCase):
    def test_receipt_is_non_disclosing_and_stable_except_time(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(json.dumps({"challenges": [{
                "id": "XPD-TEST",
                "answer_sha256": hashlib.sha256(b"TESTVECTOR").hexdigest(),
            }]}), encoding="utf-8")
            submitted = "test vector"
            result = verify_answer("XPD-TEST", submitted, manifest)
            receipt = build_receipt("XPD-TEST", submitted, result, "0.2.0", "2026-01-01T00:00:00Z")
        rendered = json.dumps(receipt)
        self.assertTrue(receipt["accepted"])
        self.assertFalse(receipt["solution_disclosed"])
        self.assertNotIn(submitted, rendered)
        self.assertEqual(receipt["submission_sha256"], hashlib.sha256(b"TESTVECTOR").hexdigest())
        self.assertRegex(receipt["receipt_id"], r"^VRF-[A-F0-9]{12}$")

    def test_packaged_self_test(self) -> None:
        self.assertTrue(packaged_self_test("0.2.0"))

    def test_cli_self_test_and_version(self) -> None:
        self_test = subprocess.run(
            [sys.executable, "scripts/verify_challenge.py", "--self-test", "--json"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(self_test.returncode, 0, self_test.stderr)
        self.assertEqual(json.loads(self_test.stdout)["self_test"], "PASS")
        version = subprocess.run(
            [sys.executable, "scripts/verify_challenge.py", "--version"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("0.2.0", version.stdout)

    def test_cli_rejection_receipt_discloses_no_proximity(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify_challenge.py", "--json", "deliberate-wrong-answer"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        receipt = json.loads(completed.stdout)
        self.assertFalse(receipt["accepted"])
        self.assertFalse(receipt["solution_disclosed"])
        self.assertNotIn("deliberate-wrong-answer", completed.stdout)


if __name__ == "__main__":
    unittest.main()
