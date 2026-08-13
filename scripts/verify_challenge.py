#!/usr/bin/env python3
"""Verify a public HMS challenge answer locally without telemetry."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.challenge_verifier import verify_answer


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/verify_challenge.py XPD-0001 YOUR_ANSWER")
        return 2

    result = verify_answer(sys.argv[1], sys.argv[2])
    print(result.message)
    return result.code


if __name__ == "__main__":
    raise SystemExit(main())
