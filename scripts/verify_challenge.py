#!/usr/bin/env python3
"""Verify a public HMS challenge answer locally without telemetry."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.challenge_verifier import verify_answer
from hms_tools.expedition_001 import HINTS, VERSION, hint_text, instructions_text


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] in {"--help", "-h", "--instructions"}:
        print(instructions_text())
        print(f"\nVerifier version {VERSION}")
        print("\nUsage: HMS-XPD-0001-Verifier-CLI XPD-0001 YOUR_ANSWER")
        print("       HMS-XPD-0001-Verifier-CLI --hint 1")
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "--hint":
        try:
            level = int(sys.argv[2])
            print(hint_text(level))
            return 0
        except (TypeError, ValueError) as exc:
            print(f"Hint error: {exc}")
            print(f"Available hint levels: 1-{len(HINTS)}")
            return 2
    if len(sys.argv) != 3:
        print("Usage: python scripts/verify_challenge.py XPD-0001 YOUR_ANSWER")
        print("Run with --help for puzzle instructions or --hint 1 for the first hint.")
        return 2

    result = verify_answer(sys.argv[1], sys.argv[2])
    print(result.message)
    return result.code


if __name__ == "__main__":
    raise SystemExit(main())
