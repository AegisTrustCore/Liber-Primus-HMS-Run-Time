#!/usr/bin/env python3
"""Verify the retained E159 terminal known-control ledger."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    9: ("73", "E118_PRIME_TOTIENT_F_PAUSE", "AN END WITHIN THE DEEP WEB"),
    10: ("74", "DIRECT_GP", "PARABLE LIKE THE INSTAR"),
}


def main() -> int:
    result = json.loads((ROOT / "historical" / "e159_terminal_controls.json").read_text(encoding="utf-8-sig"))
    with (ROOT / "historical" / "E159_TERMINAL_FULL_FAMILY_CONTROLS.csv").open(encoding="utf-8-sig", newline="") as handle:
        csv_rows = {int(row["segment"]): row for row in csv.DictReader(handle)}
    json_rows = {int(row["segment"]): row for row in result["rows"]}

    checks: list[tuple[str, bool]] = [("two declared controls", set(csv_rows) == set(json_rows) == set(EXPECTED))]
    for segment, (pages, transform, prefix) in EXPECTED.items():
        csv_row = csv_rows[segment]
        json_row = json_rows[segment]
        expected_p = 1 / (int(csv_row["null_iterations"]) + 1)
        checks.extend([
            (f"segment {segment} identity", csv_row["pages"] == pages and csv_row["real_best_transform"] == transform),
            (f"segment {segment} known text", csv_row["real_rendered"].startswith(prefix) and csv_row["real_rendered"] == json_row["real_rendered"]),
            (f"segment {segment} token separation", float(csv_row["real_token4_score"]) > float(csv_row["null_best_token_max"])),
            (f"segment {segment} vocabulary separation", float(csv_row["real_vocab_coverage"]) > float(csv_row["null_best_vocab_max"])),
            (f"segment {segment} full-family p", math.isclose(float(csv_row["full_family_joint_p"]), expected_p, rel_tol=0, abs_tol=1e-15)),
            (f"segment {segment} JSON agreement", all(str(json_row[key]) == csv_row[key] for key in ("pages", "real_best_transform", "real_rendered", "null_iterations"))),
        ])
    checks.append(("bounded decision", result.get("decision") == "BOTH_TERMINAL_SEGMENTS_SELECT_KNOWN_OPERATIONS_AND_BEAT_FULL_FAMILY_SHUFFLES"))

    failed = [name for name, passed in checks if not passed]
    if failed:
        print("FAIL — " + "; ".join(failed))
        return 1
    print(f"PASS — {len(checks)}/{len(checks)} E159 terminal-control checks; both established operators separate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
