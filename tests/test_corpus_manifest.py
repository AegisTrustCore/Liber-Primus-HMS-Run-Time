from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hms_tools.corpus_manifest import CorpusManifestError, create_manifest, validate_manifest, verify_manifest


ROOT = Path(__file__).resolve().parents[1]


class CorpusManifestTests(unittest.TestCase):
    def test_create_and_verify_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pages").mkdir()
            (root / "pages/001.txt").write_text("ᚠᚢᚦ\n", encoding="utf-8")
            manifest = create_manifest(root, "TEST-CORPUS", "1")
            report = verify_manifest(manifest, root, strict=True)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["summary"]["verified"], 1)

    def test_modified_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "page.txt"
            target.write_text("first", encoding="utf-8")
            manifest = create_manifest(root, "TEST", "1")
            target.write_text("second", encoding="utf-8")
            report = verify_manifest(manifest, root)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["summary"]["mismatch"], 1)

    def test_missing_and_unexpected_files_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "expected.txt"
            target.write_text("expected", encoding="utf-8")
            manifest = create_manifest(root, "TEST", "1")
            target.unlink()
            (root / "other.txt").write_text("other", encoding="utf-8")
            report = verify_manifest(manifest, root, strict=True)
            self.assertEqual(report["summary"]["missing"], 1)
            self.assertEqual(report["summary"]["unexpected"], 1)

    def test_traversal_and_unsorted_entries_are_rejected(self):
        with self.assertRaises(CorpusManifestError):
            validate_manifest({"schema": "HMS_CORPUS_MANIFEST_V1", "corpus_id": "X", "version": "1", "files": [{"path": "../secret", "sha256": "0" * 64, "bytes": 1, "role": "X"}]})
        with self.assertRaises(CorpusManifestError):
            validate_manifest({"schema": "HMS_CORPUS_MANIFEST_V1", "corpus_id": "X", "version": "1", "files": [
                {"path": "b", "sha256": "0" * 64, "bytes": 1, "role": "X"},
                {"path": "a", "sha256": "0" * 64, "bytes": 1, "role": "X"},
            ]})

    def test_cli_returns_one_for_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "page.txt"
            target.write_text("one", encoding="utf-8")
            manifest = create_manifest(root, "TEST", "1")
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            target.write_text("two", encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/corpus_manifest.py", "verify", str(manifest_path), str(root)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 1, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
