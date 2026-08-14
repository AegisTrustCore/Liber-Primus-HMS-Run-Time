"""Server-side Expedition verification primitives with no public answer material."""

from __future__ import annotations

import hashlib
import hmac
import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from hms_tools.challenge_verifier import normalize


class ExpeditionServiceError(ValueError):
    """Raised for invalid or rate-limited verification requests."""


@dataclass
class AttemptWindow:
    started_at: float
    attempts: int


class VerificationService:
    """In-process verification authority; production also requires edge rate limiting."""

    def __init__(
        self,
        answers: dict[str, str],
        signing_key: bytes,
        *,
        max_attempts: int = 10,
        window_seconds: int = 300,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not answers or not signing_key:
            raise ExpeditionServiceError("answers and signing_key are required")
        self._answers = {key: normalize(value) for key, value in answers.items()}
        if any(not value for value in self._answers.values()):
            raise ExpeditionServiceError("answers must remain non-empty after normalization")
        self._signing_key = signing_key
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._clock = clock
        self._windows: dict[str, AttemptWindow] = {}
        self._lock = threading.Lock()

    def _consume_attempt(self, client_id: str) -> None:
        if not client_id:
            raise ExpeditionServiceError("client identity is required")
        now = self._clock()
        with self._lock:
            window = self._windows.get(client_id)
            if window is None or now - window.started_at >= self._window_seconds:
                self._windows[client_id] = AttemptWindow(now, 1)
                return
            if window.attempts >= self._max_attempts:
                raise ExpeditionServiceError("RATE_LIMITED")
            window.attempts += 1

    def verify(
        self,
        expedition_id: str,
        submitted: str,
        client_version: str,
        client_id: str,
        *,
        verified_at: str | None = None,
    ) -> dict[str, object]:
        self._consume_attempt(client_id)
        expected = self._answers.get(expedition_id)
        if expected is None:
            raise ExpeditionServiceError("unknown expedition")
        normalized = normalize(submitted)
        if not normalized:
            raise ExpeditionServiceError("submission is empty after normalization")
        accepted = hmac.compare_digest(normalized, expected)
        submission_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        core: dict[str, object] = {
            "schema": "HMS_EXPEDITION_VERIFICATION_RECEIPT_V2",
            "expedition_id": expedition_id,
            "client_version": client_version,
            "accepted": accepted,
            "submission_sha256": submission_digest,
            "verified_at": verified_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "verification_authority": "HMS_EXPEDITION_SERVICE",
            "server_verified": True,
            "solution_disclosed": False,
        }
        signature = hmac.new(
            self._signing_key,
            json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        receipt_id = "VRF-" + hashlib.sha256(signature.encode("ascii")).hexdigest()[:16].upper()
        return {**core, "receipt_id": receipt_id, "receipt_signature": signature}
