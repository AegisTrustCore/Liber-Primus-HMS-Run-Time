"""Server-side Expedition verification primitives with no public answer material."""

from __future__ import annotations

import hashlib
import base64
import hmac
import json
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

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
        max_tracked_clients: int = 10_000,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not answers or len(signing_key) != 32:
            raise ExpeditionServiceError("answers and a 32-byte Ed25519 private key are required")
        if max_attempts < 1 or window_seconds < 1 or max_tracked_clients < 1:
            raise ExpeditionServiceError("rate-limit settings must be positive")
        if any(not re.fullmatch(r"XPD-[A-Z0-9-]+", key) for key in answers):
            raise ExpeditionServiceError("expedition IDs are invalid")
        self._answers = {key: normalize(value) for key, value in answers.items()}
        if any(not value for value in self._answers.values()):
            raise ExpeditionServiceError("answers must remain non-empty after normalization")
        self._signing_key = Ed25519PrivateKey.from_private_bytes(signing_key)
        self.public_key_bytes = self._signing_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.public_key_b64 = base64.b64encode(self.public_key_bytes).decode("ascii")
        self.public_key_id = "ED25519-" + hashlib.sha256(self.public_key_bytes).hexdigest()[:16].upper()
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._max_tracked_clients = max_tracked_clients
        self._clock = clock
        self._windows: dict[str, AttemptWindow] = {}
        self._lock = threading.Lock()

    def _consume_attempt(self, client_id: str) -> None:
        if not client_id or len(client_id) > 256:
            raise ExpeditionServiceError("client identity is required")
        now = self._clock()
        with self._lock:
            window = self._windows.get(client_id)
            if window is None or now - window.started_at >= self._window_seconds:
                expired = [key for key, value in self._windows.items() if now - value.started_at >= self._window_seconds]
                for key in expired:
                    self._windows.pop(key, None)
                if client_id not in self._windows and len(self._windows) >= self._max_tracked_clients:
                    oldest = min(self._windows, key=lambda key: self._windows[key].started_at)
                    self._windows.pop(oldest, None)
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
        if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", client_version):
            raise ExpeditionServiceError("invalid client version")
        expected = self._answers.get(expedition_id)
        if expected is None:
            raise ExpeditionServiceError("unknown expedition")
        normalized = normalize(submitted)
        if not normalized:
            raise ExpeditionServiceError("submission is empty after normalization")
        if len(normalized) > 128:
            raise ExpeditionServiceError("submission is too long")
        accepted = hmac.compare_digest(
            hashlib.sha256(normalized.encode("utf-8")).digest(),
            hashlib.sha256(expected.encode("utf-8")).digest(),
        )
        submission_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        core: dict[str, object] = {
            "schema": "HMS_EXPEDITION_VERIFICATION_RECEIPT_V2",
            "expedition_id": expedition_id,
            "client_version": client_version,
            "accepted": accepted,
            "submission_sha256": submission_digest,
            "verified_at": verified_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "verification_authority": "HMS_EXPEDITION_SERVICE",
            "signature_algorithm": "ED25519",
            "public_key_id": self.public_key_id,
            "server_verified": True,
            "solution_disclosed": False,
        }
        signature = base64.b64encode(
            self._signing_key.sign(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        ).decode("ascii")
        receipt_id = "VRF-" + hashlib.sha256(signature.encode("ascii")).hexdigest()[:16].upper()
        return {**core, "receipt_id": receipt_id, "receipt_signature": signature}
