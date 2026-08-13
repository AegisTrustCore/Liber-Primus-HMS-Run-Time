#!/usr/bin/env python3
"""Verify the bundled historical Cicada key bytes and parsed fingerprints."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY_ROOT = ROOT / "keys"
MANIFEST = KEY_ROOT / "manifest.json"


def main() -> int:
    with MANIFEST.open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)["artifacts"][0]
    key_path = KEY_ROOT / artifact["path"]

    actual_hash = hashlib.sha256(key_path.read_bytes()).hexdigest()
    if actual_hash != artifact["sha256"]:
        print(f"FAIL — SHA-256 mismatch: {actual_hash}")
        return 1

    gpg = shutil.which("gpg")
    if gpg is None:
        print("FAIL — GnuPG is required to parse the OpenPGP fingerprint.")
        return 2
    completed = subprocess.run(
        [gpg, "--batch", "--with-colons", "--show-keys", "--with-fingerprint", "--with-subkey-fingerprint", str(key_path)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        print("FAIL — GnuPG could not parse the bundled key.")
        return 1

    fingerprints = [line.split(":")[9] for line in completed.stdout.splitlines() if line.startswith("fpr:")]
    expected = [artifact["primary_fingerprint"], *artifact["subkey_fingerprints"]]
    if fingerprints != expected:
        print(f"FAIL — parsed fingerprints differ: {fingerprints}")
        return 1

    print(f"PASS — SHA-256 and {len(fingerprints)} OpenPGP fingerprint(s) match the manifest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
