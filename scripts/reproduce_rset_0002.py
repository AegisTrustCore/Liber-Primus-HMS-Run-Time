#!/usr/bin/env python3
"""Independently reproduce the public arithmetic and ledger checks in RSET-0002."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def reproduce_e1606() -> dict:
    data = rows("research/runs/RUN-0004/historical/orientation_scores.csv")
    target = next(item for item in data if item["pair"] == "15-16")
    controls = [item for item in data if item["pair"] != "15-16"]
    scores = {key[3:]: float(target[key]) for key in ("ll_DD", "ll_DR", "ll_RD", "ll_RR")}
    ordered = sorted(scores, key=scores.get, reverse=True)
    return {"rr_rank": ordered.index("RR") + 1, "rr_margin": scores["RR"] - max(v for k, v in scores.items() if k != "RR"), "max_control_rr_margin": max(float(item["rr_margin_over_best_non_rr"]) for item in controls)}


def reproduce_e1607() -> dict:
    data = rows("research/runs/RUN-0005/historical/turn_boundary_ledger.csv")
    turns = {int(item["position"]) for item in data if item["spiral_turn"] == "True"}
    boundaries = {int(item["position"]) for item in data if item["contains_internal_page_boundary"] == "True"}
    overlap = len(turns & boundaries)
    denominator = math.comb(16, 6)
    upper = sum(math.comb(6, k) * math.comb(10, 6 - k) for k in range(overlap, 7)) / denominator
    return {"overlap": overlap, "hypergeometric_upper_p": upper}


def reproduce_e1608() -> dict:
    data = rows("research/runs/RUN-0006/historical/gap_junction_ledger.csv")
    matches = sum(item["match"] == "True" for item in data)
    n = len(data); p = 1 / 29
    upper = sum(math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(matches, n+1))
    return {"positionwise_matches": matches, "binomial_upper_p": upper}


def reproduce_e1609() -> dict:
    data = rows("research/runs/RUN-0007/historical/terminal_holdout_eligibility.csv")
    return {"audited_targets": len(data), "eligible_targets": sum(item["independent_holdout"] == "True" for item in data)}


def main() -> int:
    actual = {"E1606": reproduce_e1606(), "E1607": reproduce_e1607(), "E1608": reproduce_e1608(), "E1609": reproduce_e1609()}
    expected = {
        "E1606": {"rr_rank": 3, "rr_margin": -0.030043545034063257, "max_control_rr_margin": 0.05369590033953564},
        "E1607": {"overlap": 4, "hypergeometric_upper_p": 0.09190809190809192},
        "E1608": {"positionwise_matches": 0, "binomial_upper_p": 1.0},
        "E1609": {"audited_targets": 6, "eligible_targets": 0},
    }
    for experiment, fields in expected.items():
        for name, value in fields.items():
            observed = actual[experiment][name]
            if isinstance(value, float):
                if not math.isclose(observed, value, rel_tol=1e-12, abs_tol=1e-12):
                    raise AssertionError(f"{experiment}.{name}: {observed} != {value}")
            elif observed != value:
                raise AssertionError(f"{experiment}.{name}: {observed} != {value}")
    print(json.dumps(actual, indent=2, sort_keys=True))
    print("PASS — RSET-0002 public ledgers reproduce their declared metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
