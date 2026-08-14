"""Public Expedition client for the remote sealed-verification contract."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse


class ExpeditionClientError(RuntimeError):
    """Raised when the official verification service cannot return a valid receipt."""


Transport = Callable[[str, bytes], tuple[int, bytes]]


def configured_endpoint(manifest_path: Path) -> str | None:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExpeditionClientError(f"challenge configuration could not be loaded: {error}") from error
    challenge = next((item for item in manifest.get("challenges", []) if item.get("id") == "XPD-0001"), None)
    if not isinstance(challenge, dict):
        raise ExpeditionClientError("XPD-0001 is absent from the challenge configuration")
    endpoint = challenge.get("verification_endpoint")
    return endpoint if isinstance(endpoint, str) and endpoint else None


def _default_transport(endpoint: str, body: bytes) -> tuple[int, bytes]:
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type":"application/json","User-Agent":"HMS-Expedition-Verifier/0.3"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, response.read(8192)
    except urllib.error.HTTPError as error:
        return error.code, error.read(8192)
    except urllib.error.URLError as error:
        raise ExpeditionClientError(f"verification service unavailable: {error.reason}") from error


def _validate_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ExpeditionClientError("verification endpoint must use HTTPS")


def _validate_receipt(receipt: object, expedition_id: str, client_version: str) -> dict[str, object]:
    if not isinstance(receipt, dict):
        raise ExpeditionClientError("verification service returned a non-object receipt")
    required = {"schema","receipt_id","expedition_id","client_version","accepted","submission_sha256","verified_at","verification_authority","server_verified","solution_disclosed","receipt_signature"}
    if set(receipt) != required:
        raise ExpeditionClientError("verification service returned an unexpected receipt contract")
    if receipt.get("schema") != "HMS_EXPEDITION_VERIFICATION_RECEIPT_V2" or receipt.get("expedition_id") != expedition_id:
        raise ExpeditionClientError("verification receipt identity is invalid")
    if receipt.get("client_version") != client_version or receipt.get("server_verified") is not True or receipt.get("solution_disclosed") is not False:
        raise ExpeditionClientError("verification receipt boundary is invalid")
    if not isinstance(receipt.get("accepted"), bool):
        raise ExpeditionClientError("verification receipt acceptance state is invalid")
    signature = receipt.get("receipt_signature")
    if not isinstance(signature, str) or len(signature) != 64 or any(character not in "0123456789abcdef" for character in signature):
        raise ExpeditionClientError("verification receipt signature is malformed")
    return receipt


def verify_remote(endpoint: str, expedition_id: str, submitted: str, client_version: str, transport: Transport = _default_transport) -> dict[str, object]:
    _validate_endpoint(endpoint)
    body = json.dumps({"expedition_id":expedition_id,"submission":submitted,"client_version":client_version}, separators=(",", ":")).encode("utf-8")
    status, response = transport(endpoint, body)
    try:
        payload = json.loads(response.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ExpeditionClientError("verification service returned invalid JSON") from error
    if status == 429:
        raise ExpeditionClientError("too many attempts; wait before trying again")
    if status != 200:
        raise ExpeditionClientError("verification service rejected the request")
    return _validate_receipt(payload, expedition_id, client_version)
