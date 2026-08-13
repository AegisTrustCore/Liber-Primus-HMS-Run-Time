from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_gp29_windows import write_package


class GP29PackageTests(unittest.TestCase):
    def test_portable_envelope_is_deterministic_and_checksummed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / "stage"
            stage.mkdir()
            (stage / "HMS-GP29.exe").write_bytes(b"gui")
            (stage / "HMS-GP29-CLI.exe").write_bytes(b"cli")
            (stage / "START-HERE.txt").write_text("start\n", encoding="utf-8")
            first = write_package(stage, root / "first.zip")
            first_digest = hashlib.sha256(first.read_bytes()).hexdigest()
            second = write_package(stage, root / "second.zip")
            self.assertEqual(first_digest, hashlib.sha256(second.read_bytes()).hexdigest())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(archive.testzip(), None)
                sums = archive.read("SHA256SUMS").decode("utf-8")
                self.assertIn(hashlib.sha256(b"gui").hexdigest(), sums)
                self.assertIn("HMS-GP29-CLI.exe", sums)


if __name__ == "__main__":
    unittest.main()
