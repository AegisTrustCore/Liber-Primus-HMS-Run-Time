from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_corpus_verifier_windows import write_package


class CorpusPackageTests(unittest.TestCase):
    def test_portable_envelope_is_deterministic_and_checksummed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / "stage"
            (stage / "canonical").mkdir(parents=True)
            (stage / "HMS-Corpus-Verifier.exe").write_bytes(b"gui")
            (stage / "HMS-Corpus-Verifier-CLI.exe").write_bytes(b"cli")
            (stage / "START-HERE.txt").write_text("start\n", encoding="utf-8")
            (stage / "canonical/LP-75-IMAGES-v1.0.0.json").write_text("{}\n", encoding="utf-8")
            first = write_package(stage, root / "first.zip")
            first_digest = hashlib.sha256(first.read_bytes()).hexdigest()
            second = write_package(stage, root / "second.zip")
            self.assertEqual(first_digest, hashlib.sha256(second.read_bytes()).hexdigest())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn("canonical/LP-75-IMAGES-v1.0.0.json", archive.namelist())
                sums = archive.read("SHA256SUMS").decode("utf-8")
                self.assertIn(hashlib.sha256(b"gui").hexdigest(), sums)
                self.assertIn("HMS-Corpus-Verifier-CLI.exe", sums)


if __name__ == "__main__":
    unittest.main()
