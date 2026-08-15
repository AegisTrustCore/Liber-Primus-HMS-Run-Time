from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hms_tools.corpus_manifest import CorpusManifestError, canonical_json, create_manifest, run_demo_self_test, validate_manifest, validate_verification_report, verify_manifest
from hms_tools.runtime import create_corpus_report_job, execute_job
from scripts.corpus_verifier_app import finding_matches, inspect_manifest, packaged_self_test


ROOT = Path(__file__).resolve().parents[1]


class CorpusManifestTests(unittest.TestCase):
    def test_desktop_manifest_identity_and_finding_filters(self):
        manifest = json.loads((ROOT / "corpus/liber-primus/manifests/LP-75-IMAGES-v1.0.0.json").read_text(encoding="utf-8"))
        identity = inspect_manifest(manifest)
        self.assertEqual(identity["corpus_id"], "LP-75-IMAGES")
        self.assertEqual(identity["file_count"], 75)
        self.assertEqual(identity["manifest_sha256"], "d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009")
        self.assertTrue(finding_matches("MISMATCH", "32.jpg", "Problems only", "32"))
        self.assertFalse(finding_matches("VERIFIED", "32.jpg", "Problems only", ""))
        self.assertTrue(finding_matches("VERIFIED", "72.jpg", "Verified only", "72"))

    def test_desktop_self_test_exercises_all_packaged_controls(self):
        result = packaged_self_test()
        self.assertTrue(result["passed"], result)
        self.assertEqual(set(result["cases"]), {"GOOD", "ALTERED", "MISSING", "EXTRA", "TRAVERSAL"})

    def test_canonical_lp_manifest_has_fixed_identity_and_complete_page_range(self):
        path = ROOT / "corpus/liber-primus/manifests/LP-75-IMAGES-v1.0.0.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        files = validate_manifest(manifest)
        self.assertEqual(manifest["corpus_id"], "LP-75-IMAGES")
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual([item["path"] for item in files], [f"{number:02}.jpg" for number in range(75)])
        self.assertEqual({item["role"] for item in files}, {"CANONICAL_PAGE_IMAGE"})
        self.assertEqual(sum(item["bytes"] for item in files), 52_248_065)
        self.assertEqual(hashlib.sha256(canonical_json(manifest)).hexdigest(), "d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009")

    def test_canonical_info_cli(self):
        completed = subprocess.run(
            [sys.executable, "scripts/corpus_manifest.py", "canonical-info"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        info = json.loads(completed.stdout)
        self.assertEqual(info["application_version"], "0.1.0-rc.2")
        self.assertEqual(info["file_count"], 75)
        self.assertEqual(info["manifest_sha256"], "d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009")

    def test_packaged_synthetic_demo_covers_all_required_cases(self):
        result = run_demo_self_test(ROOT / "demo" / "corpus-verifier")
        self.assertTrue(result["passed"], result)
        self.assertEqual(set(result["cases"]), {"GOOD", "ALTERED", "MISSING", "EXTRA", "TRAVERSAL"})

    def test_demo_self_test_cli(self):
        completed = subprocess.run(
            [sys.executable, "scripts/corpus_manifest.py", "demo-self-test"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["passed"])

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

    def test_runtime_accepts_digest_valid_report_without_corpus_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "page.txt").write_text("control", encoding="utf-8")
            report = verify_manifest(create_manifest(root, "TEST", "1"), root, strict=True)
            result = execute_job(create_corpus_report_job(report))
            self.assertEqual(result["evidence_label"], "PROVENANCE_ONLY")
            self.assertEqual(result["output"]["verification_status"], "PASS")
            self.assertNotIn(str(root), json.dumps(result))

    def test_runtime_rejects_tampered_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "page.txt").write_text("control", encoding="utf-8")
            report = verify_manifest(create_manifest(root, "TEST", "1"), root)
            report["status"] = "FAIL"
            with self.assertRaises(CorpusManifestError):
                validate_verification_report(report)


if __name__ == "__main__":
    unittest.main()
