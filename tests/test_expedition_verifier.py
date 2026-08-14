from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from hms_tools.expedition_verifier import packaged_self_test


ROOT = Path(__file__).resolve().parents[1]


class ExpeditionCustomerVerifierTests(unittest.TestCase):
    def test_packaged_self_test(self) -> None:
        self.assertTrue(packaged_self_test("0.3.0"))

    def test_cli_self_test_and_version(self) -> None:
        self_test = subprocess.run([sys.executable,"scripts/verify_challenge.py","--self-test","--json"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(self_test.returncode, 0, self_test.stderr)
        self.assertEqual(json.loads(self_test.stdout)["self_test"], "PASS")
        version = subprocess.run([sys.executable,"scripts/verify_challenge.py","--version"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("0.3.0", version.stdout)

    def test_cli_fails_closed_without_approved_endpoint(self) -> None:
        submitted = "deliberate-nonmatch"
        completed = subprocess.run([sys.executable,"scripts/verify_challenge.py","--json",submitted], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(completed.returncode, 2)
        self.assertIn("campaign remains closed", completed.stderr)
        self.assertNotIn(submitted, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
