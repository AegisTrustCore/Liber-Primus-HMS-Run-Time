"""Customer-facing Expedition synthetic self-test layer."""

from __future__ import annotations

import hashlib

from hms_tools.expedition_service import VerificationService


def packaged_self_test(verifier_version: str) -> bool:
    service = VerificationService({"XPD-SELF-TEST":"KNOWNCONTROL"}, hashlib.sha256(b"synthetic-packaged-signing-key").digest())
    accepted = service.verify("XPD-SELF-TEST", "known control", verifier_version, "self-test-a", verified_at="2026-01-01T00:00:00Z")
    rejected = service.verify("XPD-SELF-TEST", "deliberate nonmatch", verifier_version, "self-test-b", verified_at="2026-01-01T00:00:00Z")
    return accepted["accepted"] is True and rejected["accepted"] is False and accepted["solution_disclosed"] is False and "receipt_signature" in accepted
