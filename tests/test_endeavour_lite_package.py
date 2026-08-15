from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_endeavour_lite_windows import write_package


class EndeavourLitePackageTests(unittest.TestCase):
    def test_portable_envelope_is_deterministic_and_checksummed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); stage=root / "stage"; (stage / "canonical").mkdir(parents=True)
            (stage / "HMS-Endeavour-Lite.exe").write_bytes(b"gui"); (stage / "HMS-Endeavour-Lite-CLI.exe").write_bytes(b"cli")
            (stage / "canonical/LP-75-IMAGES-v1.0.0.json").write_text("{}\n",encoding="utf-8")
            first=write_package(stage,root / "first.zip"); digest=hashlib.sha256(first.read_bytes()).hexdigest(); second=write_package(stage,root / "second.zip")
            self.assertEqual(digest,hashlib.sha256(second.read_bytes()).hexdigest())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip()); self.assertIn("canonical/LP-75-IMAGES-v1.0.0.json",archive.namelist()); self.assertIn("HMS-Endeavour-Lite-CLI.exe",archive.read("SHA256SUMS").decode())


if __name__ == "__main__":
    unittest.main()
