#!/usr/bin/env python3
"""Derive public Expedition receipt-verification identity from a secret-manager value."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> int:
    encoded = os.environ.get("HMS_EXPEDITION_SIGNING_KEY_B64")
    if not encoded:
        print("ERROR: HMS_EXPEDITION_SIGNING_KEY_B64 is required", file=sys.stderr)
        return 2
    try:
        private_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        print("ERROR: signing key is not valid base64", file=sys.stderr)
        return 2
    if len(private_bytes) != 32:
        print("ERROR: signing key must decode to exactly 32 bytes", file=sys.stderr)
        return 2
    public_bytes = Ed25519PrivateKey.from_private_bytes(private_bytes).public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    print(json.dumps({
        "signature_algorithm": "ED25519",
        "verification_public_key": base64.b64encode(public_bytes).decode("ascii"),
        "verification_public_key_id": "ED25519-" + hashlib.sha256(public_bytes).hexdigest()[:16].upper(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
