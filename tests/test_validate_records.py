import tempfile
import unittest
from pathlib import Path

from scripts.validate_records import (
    INSTRUMENT_MANIFEST,
    PRODUCT_MANIFEST,
    canonical_text_sha256,
    validate_instrument_manifest,
    validate_product_manifest,
)


class CanonicalTextHashTests(unittest.TestCase):
    def test_line_endings_do_not_change_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lf_path = root / "lf.md"
            crlf_path = root / "crlf.md"
            lf_path.write_bytes(b"first\nsecond\n")
            crlf_path.write_bytes(b"first\r\nsecond\r\n")

            self.assertEqual(
                canonical_text_sha256(lf_path),
                canonical_text_sha256(crlf_path),
            )


class ProductContractTests(unittest.TestCase):
    def test_public_instrument_contracts_are_valid(self):
        errors, count = validate_instrument_manifest(INSTRUMENT_MANIFEST)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(count, 1)

    def test_frozen_product_ladder_is_valid(self):
        errors, count = validate_product_manifest(PRODUCT_MANIFEST)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
