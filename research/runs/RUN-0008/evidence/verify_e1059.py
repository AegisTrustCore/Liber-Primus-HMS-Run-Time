#!/usr/bin/env python3
"""Verify the normalized E1059 evidence without mutating the package."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-root",
        type=Path,
        help="Path to the historical evidence directory; defaults to ../historical.",
    )
    args = parser.parse_args()
    root = (
        args.evidence_root.resolve()
        if args.evidence_root
        else Path(__file__).resolve().parents[1] / "historical"
    )

    detector = load_json(root / "page_detector_ledger.json")
    result = load_json(root / "E1059_RESULT.json")
    crosscheck = load_json(root / "independent_retrieval_crosscheck.json")
    pages = {int(row["page"]): row for row in detector["pages"]}
    extraction_ledgers = sorted((root / "extraction_ledgers").glob("page_*.extraction.json"))
    with (root / "canonical_page_manifest.csv").open(newline="", encoding="utf-8") as handle:
        canonical_pages = list(csv.DictReader(handle))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check(
        "75 canonical pages and extraction ledgers",
        len(canonical_pages) == 75
        and len(extraction_ledgers) == 75
        and set(pages) == set(range(75)),
        f"manifest={len(canonical_pages)}, ledgers={len(extraction_ledgers)}, detector={len(pages)}",
    )
    check("75 page detector rows", len(detector["pages"]) == 75)
    check(
        "independent implementation 75/75",
        crosscheck["pages"] == 75
        and crosscheck["matches"] == 75
        and crosscheck["mismatches"] == 0,
        f"{crosscheck['matches']}/{crosscheck['pages']}",
    )
    dominant = [row for row in pages.values() if row["raw_header_hex"] == "ffffffff"]
    check("dominant FFFFFFFF family count", len(dominant) == 65, str(len(dominant)))
    check(
        "FFFFFFFF complete/partial split",
        sum(bool(row["complete"]) for row in dominant) == 19
        and sum(not bool(row["complete"]) for row in dominant) == 46,
    )
    check(
        "41 one-byte-short attractors",
        sum(
            not bool(row["complete"]) and row["recovered_length"] == 58151
            for row in dominant
        )
        == 41,
    )
    known_positive = {0, 1, 2, 3, 4, 8, 10, 11, 12, 13}
    check(
        "known-positive detector recovery",
        {page for page, row in pages.items() if row["detector_positive"]} == known_positive,
    )
    check(
        "held-out page08 transfer",
        bool(pages[8]["detector_positive"])
        and pages[8]["null"]["minimum_familywise_p"] <= 0.05,
        str(pages[8]["null"]["minimum_familywise_p"]),
    )
    false_controls = {17, 18, 20, 21, 22, 43}
    check(
        "frozen false controls rejected",
        all(not bool(pages[page]["detector_positive"]) for page in false_controls),
    )
    check(
        "no LP2 non-attractor headers",
        all(not bool(row["non_attractor_header"]) for page, row in pages.items() if page >= 17),
    )
    check(
        "no LP2 familywise anomaly",
        all(row["null"]["minimum_familywise_p"] > 0.05 for page, row in pages.items() if page >= 17),
    )
    check(
        "no active LP2 detector positives",
        all(not bool(row["detector_positive"]) for page, row in pages.items() if page >= 17),
    )
    decision = result["decision"]
    check(
        "decision retracts only the tested default-key lane",
        decision["active_lp2_outguess_leads"] == []
        and decision["action"]
        == "REMOVE_OUTGUESS_DEFAULT_KEY_EXTRACTION_FROM_ACTIVE_LP2_KEY_CHANNELS",
    )

    summary = {
        "schema": "HMS_PUBLIC_E1059_VERIFICATION_V1",
        "evidence_root": str(root),
        "passed": sum(bool(item["passed"]) for item in checks),
        "failed": sum(not bool(item["passed"]) for item in checks),
        "checks": checks,
        "boundary": (
            "This verifies the retained E1059 ledgers and bounded conclusion. "
            "It does not rerun JPEG coefficient extraction because carrier images and "
            "large coefficient bitmaps are not distributed in this normalized package."
        ),
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
