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
INSTRUMENT_MANIFEST = ROOT / "instruments" / "manifest.json"
RELEASE_STATE = ROOT / "releases" / "release-state.json"
PATREON_POST_MANIFEST = ROOT / "patreon" / "posts" / "manifest.json"

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
INSTRUMENT_STATES = {
    "PLANNED",
    "IN_DEVELOPMENT",
    "INTERNAL_TESTING",
    "EXPERIMENTAL",
    "BETA",
    "RELEASE_CANDIDATE",
    "STABLE",
    "RELEASED",
    "DEPRECATED",
}
ACCESS_LEVELS = {"OBSERVER", "PILGRIM", "NAVIGATOR", "CARTOGRAPHER", "ADMIRAL", "INTERNAL"}
POST_AUDIENCES = {"PUBLIC", "PILGRIM", "NAVIGATOR", "CARTOGRAPHER", "ADMIRAL"}
POST_STATES = {"DRAFT", "INTERNAL_REVIEW", "APPROVED", "SCHEDULED", "POSTED", "CORRECTED", "ARCHIVED"}
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


def validate_instrument_manifest(path: Path) -> tuple[list[str], int]:
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"], 0

    errors: list[str] = []
    instruments = manifest.get("instruments")
    if manifest.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(instruments, list):
        return [f"{path.relative_to(ROOT)}: instruments must be a list"], 0

    seen_ids: set[str] = set()
    for index, instrument in enumerate(instruments):
        prefix = f"instrument[{index}]"
        if not isinstance(instrument, dict):
            errors.append(f"{prefix} must be an object")
            continue
        instrument_id = instrument.get("id")
        if not isinstance(instrument_id, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", instrument_id
        ):
            errors.append(f"{prefix}.id must be a lowercase kebab-case identifier")
        elif instrument_id in seen_ids:
            errors.append(f"duplicate instrument id: {instrument_id}")
        else:
            seen_ids.add(instrument_id)
        if instrument.get("status") not in INSTRUMENT_STATES:
            errors.append(f"{prefix}.status is unrecognized")
        if instrument.get("access_level") not in ACCESS_LEVELS:
            errors.append(f"{prefix}.access_level is unrecognized")
        for field in ("name", "purpose", "last_updated"):
            if not isinstance(instrument.get(field), str) or not instrument[field]:
                errors.append(f"{prefix}.{field} must be a non-empty string")
        version = instrument.get("current_version")
        if instrument.get("status") == "RELEASED" and not isinstance(version, str):
            errors.append(f"{prefix}.current_version is required when RELEASED")
        if instrument.get("status") == "RELEASE_CANDIDATE" and not isinstance(version, str):
            errors.append(f"{prefix}.current_version is required when RELEASE_CANDIDATE")
        if instrument.get("status") == "PLANNED" and version is not None:
            errors.append(f"{prefix}.current_version must be null when PLANNED")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors], len(instruments)


def validate_release_state(path: Path, published_record_count: int) -> tuple[list[str], dict]:
    try:
        state = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"], {}

    errors: list[str] = []
    github = state.get("github")
    research = state.get("research")
    patreon = state.get("patreon")
    if state.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(github, dict):
        errors.append("github must be an object")
    if not isinstance(research, dict):
        errors.append("research must be an object")
    elif research.get("published_record_count") != published_record_count:
        errors.append("research.published_record_count must match published records")
    if not isinstance(patreon, dict) or patreon.get("status") not in {
        "PRE_LAUNCH_UNPUBLISHED", "PUBLISHED", "PAUSED"
    }:
        errors.append("patreon.status is unrecognized")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors], state


def validate_patreon_posts(path: Path, patreon_status: str | None) -> tuple[list[str], int]:
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"], 0

    errors: list[str] = []
    posts = manifest.get("posts")
    if manifest.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(posts, list):
        return [f"{path.relative_to(ROOT)}: posts must be a list"], 0

    seen_ids: set[str] = set()
    posts_root = path.parent.resolve()
    for index, post in enumerate(posts):
        prefix = f"post[{index}]"
        if not isinstance(post, dict):
            errors.append(f"{prefix} must be an object")
            continue
        post_id = post.get("id")
        audience = post.get("audience")
        status = post.get("status")
        if not isinstance(post_id, str) or not re.fullmatch(
            r"(PUBLIC|PILGRIM|NAVIGATOR|CARTOGRAPHER|ADMIRAL)-[0-9]{3,}", post_id
        ):
            errors.append(f"{prefix}.id is invalid")
        elif post_id in seen_ids:
            errors.append(f"duplicate post id: {post_id}")
        else:
            seen_ids.add(post_id)
        if audience not in POST_AUDIENCES:
            errors.append(f"{prefix}.audience is unrecognized")
        elif isinstance(post_id, str) and not post_id.startswith(f"{audience}-"):
            errors.append(f"{prefix}.id must match its audience")
        if status not in POST_STATES:
            errors.append(f"{prefix}.status is unrecognized")
        if patreon_status == "PRE_LAUNCH_UNPUBLISHED" and status == "POSTED":
            errors.append(f"{prefix} cannot be POSTED while Patreon is unpublished")
        relative_file = post.get("file")
        if not isinstance(relative_file, str) or not relative_file:
            errors.append(f"{prefix}.file must be a non-empty string")
        else:
            resolved = (posts_root / relative_file).resolve()
            if not resolved.is_relative_to(posts_root) or not resolved.is_file():
                errors.append(f"{prefix}.file does not resolve to a post draft")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors], len(posts)


def main() -> int:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for path in sorted(RECORD_DIR.glob("*.json")):
        errors.extend(validate_research_record(path, seen_ids))
    for path in sorted(PAGES_DIR.glob("page-*/record.json")):
        errors.extend(validate_page_record(path))
    instrument_errors, instrument_count = validate_instrument_manifest(INSTRUMENT_MANIFEST)
    errors.extend(instrument_errors)
    release_errors, release_state = validate_release_state(RELEASE_STATE, len(seen_ids))
    errors.extend(release_errors)
    patreon_status = release_state.get("patreon", {}).get("status")
    post_errors, post_count = validate_patreon_posts(PATREON_POST_MANIFEST, patreon_status)
    errors.extend(post_errors)

    if release_state.get("github", {}).get("current_public_tag") is None:
        instrument_manifest = load_json(INSTRUMENT_MANIFEST)
        released = [
            item.get("id") for item in instrument_manifest.get("instruments", [])
            if item.get("status") == "RELEASED"
        ]
        if released:
            errors.append(
                "instruments/manifest.json: RELEASED instruments require a current public tag: "
                + ", ".join(released)
            )

    if errors:
        print("Public record validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(seen_ids)} published research record(s) and "
        f"{len(list(PAGES_DIR.glob('page-*/record.json')))} page dossier(s), and "
        f"{instrument_count} instrument status record(s), and {post_count} Patreon post draft(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
