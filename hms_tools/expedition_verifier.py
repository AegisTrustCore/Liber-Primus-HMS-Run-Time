"""Customer-facing Expedition receipt and packaged self-test layer."""

from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from hms_tools.challenge_verifier import VerificationResult, normalize, verify_answer


def submission_sha256(value: str) -> str:
    return hashlib.sha256(normalize(value).encode("utf-8")).hexdigest()


def build_receipt(
    challenge_id: str,
    submitted: str,
    result: VerificationResult,
    verifier_version: str,
    verified_at: str | None = None,
) -> dict[str, object]:
    """Create a non-disclosing portable receipt for a completed verification."""
    digest = submission_sha256(submitted)
    receipt_seed = f"{challenge_id}\0{verifier_version}\0{digest}\0{result.matched}".encode("utf-8")
    receipt_id = "VRF-" + hashlib.sha256(receipt_seed).hexdigest()[:12].upper()
    return {
        "schema": "HMS_EXPEDITION_VERIFICATION_RECEIPT_V1",
        "receipt_id": receipt_id,
        "expedition_id": challenge_id,
        "verifier_version": verifier_version,
        "accepted": result.matched,
        "submission_sha256": digest,
        "verified_at": verified_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "solution_disclosed": False,
    }


def packaged_self_test(verifier_version: str) -> bool:
    with tempfile.TemporaryDirectory() as directory:
        manifest = Path(directory) / "manifest.json"
        manifest.write_text(json.dumps({"challenges": [{
            "id": "XPD-SELF-TEST",
            "answer_sha256": hashlib.sha256(b"KNOWNCONTROL").hexdigest(),
        }]}), encoding="utf-8")
        accepted = verify_answer("XPD-SELF-TEST", "known control", manifest)
        rejected = verify_answer("XPD-SELF-TEST", "deliberate nonmatch", manifest)
        receipt = build_receipt("XPD-SELF-TEST", "known control", accepted, verifier_version, "2026-01-01T00:00:00Z")
        return accepted.matched and not rejected.matched and receipt["accepted"] is True and receipt["solution_disclosed"] is False
