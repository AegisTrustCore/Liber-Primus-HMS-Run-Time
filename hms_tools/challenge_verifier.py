"""Deterministic, local-only challenge answer verification."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VerificationResult:
    code: int
    message: str
    matched: bool = False


def application_root() -> Path:
    """Return the bundled resource root or repository root."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def default_manifest() -> Path:
    return application_root() / "challenges" / "manifest.json"


def normalize(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def verify_answer(
    challenge_id: str,
    submitted: str,
    manifest_path: Path | None = None,
) -> VerificationResult:
    path = manifest_path or default_manifest()
    try:
        with path.open("r", encoding="utf-8") as handle:
            challenges = json.load(handle).get("challenges", [])
    except (OSError, json.JSONDecodeError) as exc:
        return VerificationResult(2, f"Verifier data could not be loaded: {exc}")

    challenge = next((item for item in challenges if item.get("id") == challenge_id), None)
    if challenge is None:
        return VerificationResult(2, f"Unknown challenge: {challenge_id}")

    normalized = normalize(submitted)
    if not normalized:
        return VerificationResult(2, "Answer is empty after normalization.")

    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if digest == challenge.get("answer_sha256"):
        return VerificationResult(0, f"PASS — {challenge_id} answer matches the sealed digest.", True)

    return VerificationResult(1, f"NO MATCH — {challenge_id} remains unsolved by this submission.")
