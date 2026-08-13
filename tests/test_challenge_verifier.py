from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from hms_tools.challenge_verifier import normalize, verify_answer


class ChallengeVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.manifest = Path(self.temp.name) / "manifest.json"
        digest = hashlib.sha256(b"TESTVECTOR").hexdigest()
        self.manifest.write_text(
            json.dumps({"challenges": [{"id": "XPD-TEST", "answer_sha256": digest}]}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_normalization(self) -> None:
        self.assertEqual(normalize(" test-vector "), "TESTVECTOR")

    def test_accepts_matching_synthetic_vector(self) -> None:
        result = verify_answer("XPD-TEST", "test vector", self.manifest)
        self.assertTrue(result.matched)
        self.assertEqual(result.code, 0)

    def test_rejects_nonmatching_vector(self) -> None:
        result = verify_answer("XPD-TEST", "wrong", self.manifest)
        self.assertFalse(result.matched)
        self.assertEqual(result.code, 1)

    def test_rejects_unknown_challenge(self) -> None:
        self.assertEqual(verify_answer("XPD-NOPE", "answer", self.manifest).code, 2)

    def test_rejects_empty_normalized_answer(self) -> None:
        self.assertEqual(verify_answer("XPD-TEST", "---", self.manifest).code, 2)


if __name__ == "__main__":
    unittest.main()
