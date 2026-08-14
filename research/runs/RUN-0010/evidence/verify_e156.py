#!/usr/bin/env python3
"""Verify the retained E156 solved-LP1 segment ledger."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = json.loads((ROOT / "historical" / "e156_result.json").read_text(encoding="utf-8-sig"))
    with (ROOT / "historical" / "E156_LP1_SEGMENT_OPERATION_LEDGER.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    pages: list[int] = []
    methods: list[str] = []
    segment_boundaries: list[int] = []
    for row_index, row in enumerate(rows):
        segment_pages = [int(value) for value in row["pages"].split(",")]
        if row_index:
            segment_boundaries.append(len(pages) - 1)
        pages.extend(segment_pages)
        methods.extend([row["cipher_method"]] * len(segment_pages))

    method_changes = [index for index in range(len(methods) - 1) if methods[index] != methods[index + 1]]
    combinations = math.comb(len(methods) - 1, len(rows) - 1)
    checks = {
        "seven segments": len(rows) == result.get("segments") == 7,
        "fifteen rune pages": pages == result.get("rune_pages") and len(pages) == 15,
        "all rows homogeneous": all(row["homogeneous"] == "1" for row in rows) and result.get("all_segments_homogeneous") is True,
        "boundaries equal changes": segment_boundaries == method_changes == result.get("segment_boundaries") == result.get("method_change_gaps"),
        "complete boundary family": combinations == result.get("boundary_sets_tested") == 3003,
        "unique homogeneous placement": result.get("homogeneous_boundary_sets") == 1,
        "exact probability": math.isclose(result.get("exact_random_boundary_p"), 1 / combinations, rel_tol=0, abs_tol=1e-15),
        "bounded decision": result.get("decision") == "DOLLAR_SEGMENT_IS_OPERATION_FRAME_ON_SOLVED_LP1",
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        print("FAIL — " + "; ".join(failed))
        return 1
    print(f"PASS — {len(checks)}/{len(checks)} E156 ledger checks; solved-LP1 boundaries equal operation changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
