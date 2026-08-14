#!/usr/bin/env python3
"""Verify the retained E1477 decision without modifying the evidence package."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    return json.loads((ROOT / "historical" / name).read_text(encoding="utf-8-sig"))


def main() -> int:
    compact = load("E1477_REPRODUCTION_RESULT.json")
    report = load("E1477_FINISHED.json")
    checks: list[tuple[str, bool]] = []

    checks.append(("experiment identity", compact.get("experiment") == report.get("experiment") == "E1477"))
    checks.append(("decision identity", compact.get("decision") == report.get("decision") == "PAGE05_BOARD_TO_PAGE33_REJECTED_ROBUST"))
    checks.append(("declared family size", compact.get("observed_routes") == report["inputs"].get("observed_route_count") == 640))
    checks.append(("page size", compact.get("page33_runes") == report["inputs"].get("page33_rune_count") == 267))
    checks.append(("control count", compact.get("control_iterations") == report["inputs"].get("control_iterations") == 999))
    checks.append(("no plaintext claim", compact.get("verified_plaintext_recovered") is False and report["claim_boundary"].get("verified_plaintext_recovered") is False))
    checks.append(("missing original scorer disclosed", report["source_program"].get("canonical_transient_dependency_available") is False))

    for order in ("2", "3", "4"):
        observed = compact["models"][order]
        detailed = report["models"][order]
        gates = detailed["promotion_gate_passes"]
        checks.append((f"{order}-gram calibration", observed.get("calibration_exact_recovery") is True and observed.get("calibration_truth_rank") == 1))
        checks.append((f"{order}-gram rejection gates", observed.get("same_route_both_halves") is False and gates.get("p_le_0_01") is False and gates.get("score_at_least_solved_reference") is False and observed.get("promoted") is False))
        checks.append((f"{order}-gram metrics agree", observed.get("familywise_empirical_p") == detailed.get("familywise_empirical_p") and observed.get("best_score") == detailed.get("observed_best_score") and observed.get("solved_reference_score") == detailed.get("solved_reference_score")))

    failed = [name for name, passed in checks if not passed]
    if failed:
        print("FAIL — " + "; ".join(failed))
        return 1
    print(f"PASS — {len(checks)}/{len(checks)} retained E1477 checks; direct Page05-board to Page33 lane rejected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
