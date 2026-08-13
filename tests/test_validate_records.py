import tempfile
import unittest
from pathlib import Path

from scripts.validate_records import canonical_text_sha256


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


if __name__ == "__main__":
    unittest.main()
