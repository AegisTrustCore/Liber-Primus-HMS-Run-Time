#!/usr/bin/env python3
"""Validate the public HMS record boundary using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = ROOT / "research" / "records"
PAGES_DIR = ROOT / "pages"

ID_PATTERN = re.compile(r"^(OBS|HYP|EXP|RES|NEG|RR|PL|COR|RET)-[0-9]{3,}$")
OBJECT_TYPES = {
    "OBSERVATION",
    "HYPOTHESIS",
    "EXPERIMENT",
    "RESULT",
    "NEGATIVE_RESULT",
    "RESEARCH_REPORT",
    "PROOFLOCK",
    "CORRECTION",
    "RETRACTION",
}
EVIDENCE_STATES = {
    "OBSERVATION",
    "HYPOTHESIS",
    "EXPERIMENTAL",
    "PROVISIONAL",
    "REPRODUCED",
    "VERIFIED",
    "UNSUPPORTED",
    "REFUTED",
    "RETRACTED",
}
DOSSIER_STATES = {"AUDIT_PENDING", "AUDIT_IN_PROGRESS", "REVIEW_READY", "PUBLISHED"}
REQUIRED_RECORD_FIELDS = {
    "schema_version",
    "id",
    "object_type",
    "title",
    "claim",
    "scope",
    "classification",
    "publication_status",
    "evidence_status",
    "created_at",
    "updated_at",
    "authors",
    "sources",
    "reproduction",
    "limitations",
    "related_records",
    "content_hash",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def validate_research_record(path: Path, seen_ids: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        record = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]

    missing = sorted(REQUIRED_RECORD_FIELDS - record.keys())
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")

    record_id = record.get("id")
    if not isinstance(record_id, str) or not ID_PATTERN.fullmatch(record_id):
        errors.append("id must use a recognized prefix and at least three digits")
    elif record_id in seen_ids:
        errors.append(f"duplicate id: {record_id}")
    else:
        seen_ids.add(record_id)

    if record.get("classification") != "PUBLIC":
        errors.append("public repository records must be classified PUBLIC")
    if record.get("publication_status") != "PUBLISHED":
        errors.append("public repository records must be PUBLISHED")
    if record.get("object_type") not in OBJECT_TYPES:
        errors.append("unrecognized object_type")
    if record.get("evidence_status") not in EVIDENCE_STATES:
        errors.append("unrecognized evidence_status")
    if not isinstance(record.get("authors"), list) or not record.get("authors"):
        errors.append("authors must be a non-empty list")
    if not isinstance(record.get("sources"), list) or not record.get("sources"):
        errors.append("sources must be a non-empty list")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors]


def validate_page_record(path: Path) -> list[str]:
    try:
        record = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]

    errors: list[str] = []
    if record.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(record.get("page"), int) or record["page"] < 0:
        errors.append("page must be a non-negative integer")
    if record.get("dossier_status") not in DOSSIER_STATES:
        errors.append("unrecognized dossier_status")
    if not isinstance(record.get("audit_priority"), int) or record["audit_priority"] < 1:
        errors.append("audit_priority must be a positive integer")
    count = record.get("public_verified_claim_count")
    if not isinstance(count, int) or count < 0:
        errors.append("public_verified_claim_count must be a non-negative integer")
    return [f"{path.relative_to(ROOT)}: {error}" for error in errors]


def main() -> int:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in sorted(RECORD_DIR.glob("*.json")):
        errors.extend(validate_research_record(path, seen_ids))
    for path in sorted(PAGES_DIR.glob("page-*/record.json")):
        errors.extend(validate_page_record(path))

    if errors:
        print("Public record validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(seen_ids)} published research record(s) and "
        f"{len(list(PAGES_DIR.glob('page-*/record.json')))} page dossier(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
