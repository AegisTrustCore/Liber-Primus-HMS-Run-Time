"""Minimal JSON API adapter for the sealed Expedition verification service."""

from __future__ import annotations

import json
from typing import Any

from hms_tools.expedition_service import ExpeditionServiceError, VerificationService


MAX_REQUEST_BYTES = 4096


def handle_verification_request(
    service: VerificationService,
    body: bytes,
    client_id: str,
) -> tuple[int, dict[str, object]]:
    if len(body) > MAX_REQUEST_BYTES:
        return 413, {"error": "REQUEST_TOO_LARGE"}
    try:
        payload: Any = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 400, {"error": "INVALID_JSON"}
    if not isinstance(payload, dict) or set(payload) != {"expedition_id", "submission", "client_version"}:
        return 400, {"error": "INVALID_REQUEST"}
    if not all(isinstance(payload[field], str) for field in payload):
        return 400, {"error": "INVALID_REQUEST"}
    try:
        return 200, service.verify(
            payload["expedition_id"],
            payload["submission"],
            payload["client_version"],
            client_id,
        )
    except ExpeditionServiceError as error:
        if str(error) == "RATE_LIMITED":
            return 429, {"error": "RATE_LIMITED"}
        return 400, {"error": "INVALID_REQUEST"}
