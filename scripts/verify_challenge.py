#!/usr/bin/env python3
"""Verify a public HMS challenge answer locally without telemetry."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "challenges" / "manifest.json"


def normalize(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/verify_challenge.py XPD-0001 YOUR_ANSWER")
        return 2

    challenge_id, submitted = sys.argv[1], normalize(sys.argv[2])
    with MANIFEST.open("r", encoding="utf-8") as handle:
        challenges = json.load(handle).get("challenges", [])

    challenge = next((item for item in challenges if item.get("id") == challenge_id), None)
    if challenge is None:
        print(f"Unknown challenge: {challenge_id}")
        return 2
    if not submitted:
        print("Answer is empty after normalization.")
        return 2

    digest = hashlib.sha256(submitted.encode("utf-8")).hexdigest()
    if digest == challenge["answer_sha256"]:
        print(f"PASS — {challenge_id} answer matches the sealed digest.")
        return 0

    print(f"NO MATCH — {challenge_id} remains unsolved by this submission.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
