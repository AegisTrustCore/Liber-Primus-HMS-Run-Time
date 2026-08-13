#!/usr/bin/env python3
"""Validate the public HMS record boundary using only the Python standard library."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from scripts.build_research_archive import validate_archive
except ModuleNotFoundError:
    from build_research_archive import validate_archive


ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = ROOT / "research" / "records"
PAGES_DIR = ROOT / "pages"
INSTRUMENT_MANIFEST = ROOT / "instruments" / "manifest.json"
RELEASE_STATE = ROOT / "releases" / "release-state.json"
PATREON_POST_MANIFEST = ROOT / "patreon" / "public-manifest.json"
CHALLENGE_MANIFEST = ROOT / "challenges" / "manifest.json"
RELEASE_GATE_DIR = ROOT / "releases" / "gates"
ENVIRONMENT_DIR = ROOT / "releases" / "environments"
ID_REGISTRY = ROOT / "registry" / "id-reservations.json"

ID_PATTERN = re.compile(r"^(OBS|HYP|EXP|RUN|RES|NEG|EVD|CLM|HL|PL|RR|COR|RET|PUB)-[0-9]{4,}$")
OBJECT_TYPES = {
    "OBSERVATION",
    "HYPOTHESIS",
    "EXPERIMENT",
    "RUN",
    "RESULT",
    "NEGATIVE_RESULT",
    "RESEARCH_REPORT",
    "EVIDENCE",
    "CLAIM",
    "HASHLOCK",
    "PROOFLOCK",
    "CORRECTION",
    "RETRACTION",
    "PUBLICATION",
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
CHALLENGE_STATES = {"DRAFT", "RELEASE_CANDIDATE", "OPEN", "SOLVED", "ARCHIVED"}
CHALLENGE_TYPES = {"SYNTHETIC_METHOD_TRAINING", "PUBLIC_RESEARCH_REPRODUCTION", "PUBLIC_PUZZLE"}
REQUIRED_RECORD_FIELDS = {
    "schema_version",
    "id",
    "object_type",
    "title",
    "claim",
    "why_it_matters",
    "scope",
    "classification",
    "publication_status",
    "evidence_status",
    "created_at",
    "updated_at",
    "authors",
    "sources",
    "method",
    "controls",
    "reproduction",
    "limitations",
    "provenance",
    "related_records",
    "supersedes",
    "superseded_by",
    "content_hash",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def canonical_json_sha256(value: dict) -> str:
    """Hash semantic JSON content independently of whitespace and line endings."""
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def canonical_text_sha256(path: Path) -> str:
    """Hash UTF-8 text independently of the checkout's line endings."""
    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


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
        errors.append("id must use a canonical research prefix and at least four digits")
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
    if not isinstance(record.get("controls"), list) or not record.get("controls"):
        errors.append("controls must be a non-empty list")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        if not isinstance(provenance.get("chain_complete"), bool):
            errors.append("provenance.chain_complete must be boolean")
        if not isinstance(provenance.get("input_hashes"), list) or not provenance.get("input_hashes"):
            errors.append("provenance.input_hashes must be a non-empty list")
        environment = provenance.get("environment_manifest")
        if not isinstance(environment, str) or not (ROOT / environment).is_file():
            errors.append("provenance.environment_manifest must resolve to a public manifest")

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
    if manifest.get("schema_version") != "1.1.0":
        errors.append("schema_version must be 1.1.0")
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
        if instrument.get("product_class") not in {
            "DEVELOPER_TOOL", "USER_INSTRUMENT", "PUZZLE_PACKAGE", "PLUGIN", "HOSTED_SERVICE"
        }:
            errors.append(f"{prefix}.product_class is unrecognized")
        if not isinstance(instrument.get("customer_ready"), bool):
            errors.append(f"{prefix}.customer_ready must be boolean")
        delivery_modes = {
            "WEB", "DESKTOP_INSTALLER", "DESKTOP_PORTABLE", "CLI_BINARY",
            "RUNTIME", "PLUGIN", "DEVELOPER_SOURCE",
        }
        targets = instrument.get("target_delivery_modes")
        released = instrument.get("released_delivery_modes")
        if not isinstance(targets, list) or not targets or any(mode not in delivery_modes for mode in targets):
            errors.append(f"{prefix}.target_delivery_modes must contain recognized modes")
        if not isinstance(released, list) or any(mode not in delivery_modes for mode in released):
            errors.append(f"{prefix}.released_delivery_modes must contain only recognized modes")
        if isinstance(released, list) and isinstance(targets, list) and not set(released).issubset(targets):
            errors.append(f"{prefix}.released_delivery_modes must be a subset of target_delivery_modes")
        if instrument.get("customer_ready") and not released:
            errors.append(f"{prefix}.customer_ready requires a released delivery mode")
        platforms = instrument.get("supported_platforms")
        if not isinstance(platforms, list) or any(not isinstance(item, str) or not item for item in platforms):
            errors.append(f"{prefix}.supported_platforms must be a string array")
        if instrument.get("customer_ready") and not platforms:
            errors.append(f"{prefix}.customer_ready requires at least one supported platform")
        download_page = instrument.get("download_page")
        if download_page is not None and (not isinstance(download_page, str) or not download_page.startswith("https://")):
            errors.append(f"{prefix}.download_page must be null or an HTTPS URL")
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
        if status == "POSTED":
            if not isinstance(post.get("published_at"), str):
                errors.append(f"{prefix}.published_at is required when POSTED")
            if not isinstance(post.get("url"), str) or not post["url"].startswith(
                "https://www.patreon.com/"
            ):
                errors.append(f"{prefix}.url is required when POSTED")
        if "file" in post or "body" in post or "content" in post:
            errors.append(f"{prefix} must be metadata-only; post bodies and file pointers are private")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors], len(posts)


def validate_challenge_manifest(path: Path) -> tuple[list[str], int]:
    try:
        manifest = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"], 0

    errors: list[str] = []
    challenges = manifest.get("challenges")
    if manifest.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(challenges, list):
        return [f"{path.relative_to(ROOT)}: challenges must be a list"], 0

    seen_ids: set[str] = set()
    manifest_root = path.parent.resolve()
    for index, challenge in enumerate(challenges):
        prefix = f"challenge[{index}]"
        if not isinstance(challenge, dict):
            errors.append(f"{prefix} must be an object")
            continue
        challenge_id = challenge.get("id")
        if not isinstance(challenge_id, str) or not re.fullmatch(r"XPD-[0-9]{4,}", challenge_id):
            errors.append(f"{prefix}.id is invalid")
        elif challenge_id in seen_ids:
            errors.append(f"duplicate challenge id: {challenge_id}")
        else:
            seen_ids.add(challenge_id)
        if challenge.get("status") not in CHALLENGE_STATES:
            errors.append(f"{prefix}.status is unrecognized")
        if challenge.get("classification") != "PUBLIC":
            errors.append(f"{prefix}.classification must be PUBLIC")
        if challenge.get("access_level") != "OBSERVER":
            errors.append(f"{prefix}.access_level must be OBSERVER")
        if challenge.get("challenge_type") not in CHALLENGE_TYPES:
            errors.append(f"{prefix}.challenge_type is unrecognized")
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(challenge.get("version", ""))):
            errors.append(f"{prefix}.version must be semantic x.y.z")
        if challenge.get("difficulty") not in {"DECKHAND", "PILGRIM", "NAVIGATOR", "CARTOGRAPHER", "ADMIRAL"}:
            errors.append(f"{prefix}.difficulty is unrecognized")
        if challenge.get("source_class") not in {"SYNTHETIC", "KNOWN_CONTROL", "PUBLIC_STRUCTURAL", "PUBLIC_RESEARCH"}:
            errors.append(f"{prefix}.source_class is unrecognized")
        if challenge.get("evidence_ceiling") not in {"TRAINING", "KNOWN_CONTROL", "STRUCTURAL", "BOUNDED_NEGATIVE", "HYPOTHESIS"}:
            errors.append(f"{prefix}.evidence_ceiling is unrecognized")
        if not isinstance(challenge.get("beginner_entry"), bool):
            errors.append(f"{prefix}.beginner_entry must be boolean")
        for field in ("research_concept", "skill_taught"):
            if not isinstance(challenge.get(field), str) or not challenge[field]:
                errors.append(f"{prefix}.{field} must be a non-empty string")
        instrument_used = challenge.get("instrument_used")
        if instrument_used is not None and (not isinstance(instrument_used, str) or not instrument_used):
            errors.append(f"{prefix}.instrument_used must be null or a non-empty string")
        digest = challenge.get("answer_sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
            errors.append(f"{prefix}.answer_sha256 must be a lowercase SHA-256 digest")
        for field in ("entrypoint", "verifier"):
            relative_file = challenge.get(field)
            if not isinstance(relative_file, str) or not relative_file:
                errors.append(f"{prefix}.{field} must be a non-empty string")
                continue
            resolved = (manifest_root / relative_file).resolve()
            if not resolved.is_file():
                errors.append(f"{prefix}.{field} does not resolve to a file")
        solution_status = challenge.get("solution_status")
        public_solution = challenge.get("public_solution")
        if solution_status not in {"SEALED", "PUBLISHED"}:
            errors.append(f"{prefix}.solution_status is unrecognized")
        if solution_status == "SEALED" and public_solution is not None:
            errors.append(f"{prefix}.public_solution must be null while SEALED")
        if solution_status == "PUBLISHED":
            if not isinstance(public_solution, str) or not public_solution:
                errors.append(f"{prefix}.public_solution is required when PUBLISHED")
            elif not (manifest_root / public_solution).resolve().is_file():
                errors.append(f"{prefix}.public_solution does not resolve to a file")
        if challenge.get("status") == "SOLVED" and solution_status != "PUBLISHED":
            errors.append(f"{prefix} cannot be SOLVED while its solution is sealed")
        if not isinstance(challenge.get("research_claim"), bool):
            errors.append(f"{prefix}.research_claim must be boolean")
        hints = challenge.get("public_hints")
        if not isinstance(hints, list) or not hints:
            errors.append(f"{prefix}.public_hints must contain at least one hint record")
        else:
            hint_ids: set[str] = set()
            for hint_index, hint in enumerate(hints):
                hint_prefix = f"{prefix}.public_hints[{hint_index}]"
                if not isinstance(hint, dict):
                    errors.append(f"{hint_prefix} must be an object")
                    continue
                hint_id = hint.get("id")
                if not isinstance(hint_id, str) or not re.fullmatch(r"HINT-[0-9]+", hint_id):
                    errors.append(f"{hint_prefix}.id is invalid")
                elif hint_id in hint_ids:
                    errors.append(f"{hint_prefix}.id is duplicated")
                else:
                    hint_ids.add(hint_id)
                if hint.get("release_state") not in {"PUBLIC", "DELAYED", "SEALED"}:
                    errors.append(f"{hint_prefix}.release_state is unrecognized")
                hint_path = hint.get("path")
                resolved_hint = (manifest_root / hint_path).resolve() if isinstance(hint_path, str) else None
                if resolved_hint is None or not resolved_hint.is_file():
                    errors.append(f"{hint_prefix}.path does not resolve to a file")
                else:
                    actual_hint_hash = canonical_text_sha256(resolved_hint)
                    if hint.get("sha256") != actual_hint_hash:
                        errors.append(f"{hint_prefix}.sha256 does not match the hint file")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors], len(challenges)


def validate_environment_manifests(directory: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    count = 0
    for path in sorted(directory.glob("ENV-*.json")):
        count += 1
        try:
            manifest = load_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        if manifest.get("schema_version") != "1.0.0":
            errors.append(f"{path.relative_to(ROOT)}: schema_version must be 1.0.0")
        if not re.fullmatch(r"ENV-[0-9]{4,}", str(manifest.get("id", ""))):
            errors.append(f"{path.relative_to(ROOT)}: id must use ENV and at least four digits")
        for field in ("hms_version", "engine", "operating_system", "architecture", "encoding", "alphabet_mapping", "page_numbering"):
            if not isinstance(manifest.get(field), str) or not manifest[field]:
                errors.append(f"{path.relative_to(ROOT)}: {field} must be a non-empty string")
        if not isinstance(manifest.get("dependencies"), list):
            errors.append(f"{path.relative_to(ROOT)}: dependencies must be a list")
    return errors, count


def validate_release_gates(directory: Path) -> tuple[list[str], dict[str, dict]]:
    errors: list[str] = []
    gates: dict[str, dict] = {}
    common_checks = {
        "publication_approved", "secret_scan_passed", "rights_reviewed",
        "provenance_complete", "environment_recorded", "links_tested",
        "automated_validation_passed",
    }
    type_checks = {
        "SOFTWARE": ("software", {
            "tests_passed", "package_hashes_present", "dependency_manifest_present",
            "security_scan_passed", "build_reproducible", "release_notes_complete",
        }),
        "RESEARCH": ("research", {
            "claims_bounded", "complete_family_retained", "controls_recorded",
            "corrections_linked", "clean_reproduction_passed",
        }),
        "EXPEDITION": ("expedition", {
            "solution_state_valid", "verifier_tested", "challenge_status_consistent",
            "research_claims_bounded",
        }),
        "PUBLICATION": ("publication", {
            "claims_bounded", "sources_cited", "corrections_linked",
            "evidence_links_complete",
        }),
    }
    for path in sorted(directory.glob("*.json")):
        try:
            gate = load_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        release_id = gate.get("release_id")
        if not isinstance(release_id, str) or not release_id:
            errors.append(f"{path.relative_to(ROOT)}: release_id is required")
            continue
        if release_id in gates:
            errors.append(f"{path.relative_to(ROOT)}: duplicate release gate {release_id}")
        gates[release_id] = gate
        release_type = gate.get("release_type")
        common = gate.get("common_checks")
        selected = gate.get("type_checks")
        subject = gate.get("release_subject")
        approval = gate.get("human_approval")
        if gate.get("schema_version") != "1.1.0":
            errors.append(f"{path.relative_to(ROOT)}: schema_version must be 1.1.0")
        if gate.get("classification") != "PUBLIC":
            errors.append(f"{path.relative_to(ROOT)}: classification must be PUBLIC")
        if gate.get("status") not in {"PENDING", "APPROVED", "REJECTED", "SUPERSEDED"}:
            errors.append(f"{path.relative_to(ROOT)}: status is unrecognized")
        if not isinstance(common, dict) or set(common) != common_checks:
            errors.append(f"{path.relative_to(ROOT)}: common_checks is incomplete or contains unknown checks")
        expected = type_checks.get(release_type)
        if expected is None:
            errors.append(f"{path.relative_to(ROOT)}: release_type is unrecognized")
            selected_key, required_type_checks = None, set()
        else:
            selected_key, required_type_checks = expected
        if not isinstance(selected, dict) or set(selected) != {selected_key}:
            errors.append(f"{path.relative_to(ROOT)}: type_checks must contain only the {selected_key!r} gate")
            selected_checks = {}
        else:
            selected_checks = selected.get(selected_key)
            if not isinstance(selected_checks, dict) or set(selected_checks) != required_type_checks:
                errors.append(f"{path.relative_to(ROOT)}: {selected_key} checks are incomplete or contain unknown checks")
                selected_checks = {}

        subject_digest = None
        if not isinstance(subject, dict):
            errors.append(f"{path.relative_to(ROOT)}: release_subject is required")
        else:
            if subject.get("schema_version") != "1.0.0":
                errors.append(f"{path.relative_to(ROOT)}: release_subject.schema_version must be 1.0.0")
            candidate_sha = subject.get("candidate_commit_sha")
            if not isinstance(candidate_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", candidate_sha):
                errors.append(f"{path.relative_to(ROOT)}: candidate_commit_sha must be a full lowercase Git SHA")
            subject_digest = subject.get("release_manifest_sha256")
            if not isinstance(subject_digest, str) or not re.fullmatch(r"[a-f0-9]{64}", subject_digest):
                errors.append(f"{path.relative_to(ROOT)}: release_manifest_sha256 must be a lowercase SHA-256 digest")
            manifest_rel = subject.get("release_manifest")
            manifest_path = (ROOT / manifest_rel).resolve() if isinstance(manifest_rel, str) else None
            manifest_root = (ROOT / "releases" / "manifests").resolve()
            if manifest_path is None or not manifest_path.is_relative_to(manifest_root) or not manifest_path.is_file():
                errors.append(f"{path.relative_to(ROOT)}: release_manifest must resolve under releases/manifests")
            else:
                try:
                    manifest = load_json(manifest_path)
                except (OSError, json.JSONDecodeError, ValueError) as exc:
                    errors.append(f"{manifest_path.relative_to(ROOT)}: {exc}")
                    manifest = {}
                actual_digest = canonical_json_sha256(manifest)
                if subject_digest != actual_digest:
                    errors.append(f"{path.relative_to(ROOT)}: release subject changed; human approval is invalid")
                comparisons = {
                    "release_id": release_id,
                    "release_type": release_type,
                    "candidate_commit_sha": candidate_sha,
                    "intended_tag": subject.get("intended_tag"),
                    "environment_id": subject.get("environment_id"),
                }
                for field, expected_value in comparisons.items():
                    if manifest.get(field) != expected_value:
                        errors.append(f"{path.relative_to(ROOT)}: release subject {field} disagrees with its manifest")
                notes_path = manifest.get("release_notes")
                if not isinstance(notes_path, str) or not (ROOT / notes_path).resolve().is_file():
                    errors.append(f"{manifest_path.relative_to(ROOT)}: release_notes must resolve to a file")
                artifacts = manifest.get("artifacts")
                if not isinstance(artifacts, list) or not artifacts:
                    errors.append(f"{manifest_path.relative_to(ROOT)}: artifacts must be a non-empty list")
                else:
                    names: set[str] = set()
                    for index, artifact in enumerate(artifacts):
                        name = artifact.get("name") if isinstance(artifact, dict) else None
                        digest = artifact.get("sha256") if isinstance(artifact, dict) else None
                        if not isinstance(name, str) or not name or name in names:
                            errors.append(f"{manifest_path.relative_to(ROOT)}: artifact[{index}] name is missing or duplicated")
                        else:
                            names.add(name)
                        if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
                            errors.append(f"{manifest_path.relative_to(ROOT)}: artifact[{index}] sha256 is invalid")
                        elif isinstance(name, str) and "/" in name and isinstance(candidate_sha, str):
                            completed = subprocess.run(
                                ["git", "show", f"{candidate_sha}:{name}"],
                                cwd=ROOT,
                                check=False,
                                capture_output=True,
                            )
                            if completed.returncode != 0:
                                errors.append(f"{manifest_path.relative_to(ROOT)}: artifact[{index}] is absent from candidate commit")
                            elif hashlib.sha256(completed.stdout).hexdigest() != digest:
                                errors.append(f"{manifest_path.relative_to(ROOT)}: artifact[{index}] hash disagrees with candidate commit")
            environment_id = subject.get("environment_id")
            if not isinstance(environment_id, str) or not (ROOT / "releases" / "environments" / f"{environment_id}.json").is_file():
                errors.append(f"{path.relative_to(ROOT)}: environment_id does not resolve to a public manifest")
            if subject.get("intended_tag") != release_id:
                errors.append(f"{path.relative_to(ROOT)}: intended_tag must equal release_id")

        if not isinstance(approval, dict) or not isinstance(approval.get("approved"), bool):
            errors.append(f"{path.relative_to(ROOT)}: human_approval is incomplete")
        if gate.get("status") == "APPROVED":
            if not all(common.get(item) is True for item in common_checks):
                errors.append(f"{path.relative_to(ROOT)}: APPROVED gate requires every common check")
            if not all(selected_checks.get(item) is True for item in required_type_checks):
                errors.append(f"{path.relative_to(ROOT)}: APPROVED gate requires every type-specific check")
            if approval.get("approved") is not True or not approval.get("approver") or not approval.get("approved_at"):
                errors.append(f"{path.relative_to(ROOT)}: APPROVED gate requires named human approval")
            if approval.get("approved_subject_sha256") != subject_digest:
                errors.append(f"{path.relative_to(ROOT)}: approval is not bound to the current release subject")
        elif gate.get("status") == "PENDING":
            if isinstance(common, dict) and common.get("publication_approved") is not False:
                errors.append(f"{path.relative_to(ROOT)}: PENDING gate requires publication_approved false")
            if isinstance(approval, dict) and (
                approval.get("approved") is not False
                or approval.get("approver") is not None
                or approval.get("approved_at") is not None
                or approval.get("approved_subject_sha256") is not None
            ):
                errors.append(f"{path.relative_to(ROOT)}: PENDING gate cannot contain human approval")
        elif isinstance(approval, dict) and approval.get("approved") is True:
            errors.append(f"{path.relative_to(ROOT)}: human approval true requires APPROVED status")
    return errors, gates


def validate_id_registry(path: Path, required_ids: set[str]) -> tuple[list[str], int]:
    try:
        registry = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"], 0
    errors: list[str] = []
    reservations = registry.get("reservations")
    if registry.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if not isinstance(reservations, list):
        return [f"{path.relative_to(ROOT)}: reservations must be a list"], 0
    seen: set[str] = set()
    canonical = re.compile(r"^(CORP|PAGE|REG|PSET|PIPE|OBS|HYP|EXP|RUN|RES|NEG|EVD|CLM|HL|PL|RR|COR|RET|RC|ENV|PUB|XPD|CAP|RSET)-[0-9]{4,}$")
    for index, reservation in enumerate(reservations):
        item_id = reservation.get("id") if isinstance(reservation, dict) else None
        if not isinstance(item_id, str) or not canonical.fullmatch(item_id):
            errors.append(f"reservation[{index}].id is invalid")
        elif item_id in seen:
            errors.append(f"duplicate reserved ID: {item_id}")
        else:
            seen.add(item_id)
        if not isinstance(reservation, dict) or reservation.get("state") not in {"RESERVED", "ACTIVE", "SUPERSEDED", "RETRACTED", "RETIRED"}:
            errors.append(f"reservation[{index}].state is invalid")
    missing = sorted(required_ids - seen)
    if missing:
        errors.append("active public objects lack permanent ID reservations: " + ", ".join(missing))
    return [f"{path.relative_to(ROOT)}: {error}" for error in errors], len(reservations)


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
    challenge_errors, challenge_count = validate_challenge_manifest(CHALLENGE_MANIFEST)
    errors.extend(challenge_errors)
    environment_errors, environment_count = validate_environment_manifests(ENVIRONMENT_DIR)
    errors.extend(environment_errors)
    gate_errors, release_gates = validate_release_gates(RELEASE_GATE_DIR)
    errors.extend(gate_errors)
    challenge_ids = {
        item.get("id") for item in load_json(CHALLENGE_MANIFEST).get("challenges", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    archive_ids = {
        path.parent.name
        for kind in ("runs", "results", "capsules", "runsets")
        for path in (ROOT / "research" / kind).glob("*/manifest.json")
    }
    registry_errors, reservation_count = validate_id_registry(
        ID_REGISTRY, seen_ids | challenge_ids | archive_ids
    )
    errors.extend(registry_errors)
    errors.extend(f"research archive: {error}" for error in validate_archive())

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
    if patreon_status == "PUBLISHED" and not release_state.get("patreon", {}).get(
        "published_at"
    ):
        errors.append("releases/release-state.json: published Patreon requires published_at")
    public_tag = release_state.get("github", {}).get("current_public_tag")
    if public_tag is not None and release_gates.get(public_tag, {}).get("status") != "APPROVED":
        errors.append("releases/release-state.json: current public tag requires an APPROVED release gate")

    if errors:
        print("Public record validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(seen_ids)} published research record(s) and "
        f"{len(list(PAGES_DIR.glob('page-*/record.json')))} page dossier(s), and "
        f"{instrument_count} instrument status record(s), and {post_count} Patreon post record(s)."
        f" Validated {challenge_count} public challenge record(s), {environment_count} environment manifest(s),"
        f" {len(release_gates)} release gate(s), and {reservation_count} permanent ID reservation(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
