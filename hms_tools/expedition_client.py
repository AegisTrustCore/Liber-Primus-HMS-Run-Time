"""Public Expedition client for the remote sealed-verification contract."""

from __future__ import annotations

import json
import hashlib
import re
import base64
import binascii
import urllib.error
import urllib.request
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from hms_tools.challenge_verifier import normalize


class ExpeditionClientError(RuntimeError):
    """Raised when the official verification service cannot return a valid receipt."""


Transport = Callable[[str, bytes], tuple[int, bytes]]


@dataclass(frozen=True)
class ServiceConfiguration:
    endpoint: str
    public_key_b64: str
    public_key_id: str


def configured_service(manifest_path: Path) -> ServiceConfiguration | None:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExpeditionClientError(f"challenge configuration could not be loaded: {error}") from error
    challenge = next((item for item in manifest.get("challenges", []) if item.get("id") == "XPD-0001"), None)
    if not isinstance(challenge, dict):
        raise ExpeditionClientError("XPD-0001 is absent from the challenge configuration")
    values = (
        challenge.get("verification_endpoint"),
        challenge.get("verification_public_key"),
        challenge.get("verification_public_key_id"),
    )
    if values == (None, None, None):
        return None
    if not all(isinstance(value, str) and value for value in values):
        raise ExpeditionClientError("verification service configuration is incomplete")
    _validate_endpoint(values[0])
    return ServiceConfiguration(*values)


def configured_endpoint(manifest_path: Path) -> str | None:
    configuration = configured_service(manifest_path)
    return None if configuration is None else configuration.endpoint


def _default_transport(endpoint: str, body: bytes) -> tuple[int, bytes]:
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type":"application/json","User-Agent":"HMS-Expedition-Verifier/0.3"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read(8193)
            if len(payload) > 8192:
                raise ExpeditionClientError("verification service response is too large")
            return response.status, payload
    except urllib.error.HTTPError as error:
        return error.code, error.read(8192)
    except urllib.error.URLError as error:
        raise ExpeditionClientError(f"verification service unavailable: {error.reason}") from error


def _validate_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ExpeditionClientError("verification endpoint must use HTTPS")
    if parsed.query or parsed.fragment:
        raise ExpeditionClientError("verification endpoint cannot contain a query or fragment")


def _validate_receipt(
    receipt: object,
    expedition_id: str,
    client_version: str,
    submitted: str,
    public_key_b64: str,
    public_key_id: str,
) -> dict[str, object]:
    if not isinstance(receipt, dict):
        raise ExpeditionClientError("verification service returned a non-object receipt")
    required = {"schema","receipt_id","expedition_id","client_version","accepted","submission_sha256","verified_at","verification_authority","signature_algorithm","public_key_id","server_verified","solution_disclosed","receipt_signature"}
    if set(receipt) != required:
        raise ExpeditionClientError("verification service returned an unexpected receipt contract")
    if receipt.get("schema") != "HMS_EXPEDITION_VERIFICATION_RECEIPT_V2" or receipt.get("expedition_id") != expedition_id:
        raise ExpeditionClientError("verification receipt identity is invalid")
    if receipt.get("client_version") != client_version or receipt.get("server_verified") is not True or receipt.get("solution_disclosed") is not False:
        raise ExpeditionClientError("verification receipt boundary is invalid")
    if not isinstance(receipt.get("accepted"), bool):
        raise ExpeditionClientError("verification receipt acceptance state is invalid")
    if receipt.get("signature_algorithm") != "ED25519" or receipt.get("public_key_id") != public_key_id:
        raise ExpeditionClientError("verification receipt signing identity is invalid")
    normalized = normalize(submitted)
    expected_submission_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if not normalized or receipt.get("submission_sha256") != expected_submission_digest:
        raise ExpeditionClientError("verification receipt does not match this submission")
    receipt_id = receipt.get("receipt_id")
    if not isinstance(receipt_id, str) or not re.fullmatch(r"VRF-[A-F0-9]{16}", receipt_id):
        raise ExpeditionClientError("verification receipt ID is malformed")
    verified_at = receipt.get("verified_at")
    if not isinstance(verified_at, str):
        raise ExpeditionClientError("verification receipt timestamp is malformed")
    try:
        datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ExpeditionClientError("verification receipt timestamp is malformed") from error
    signature_text = receipt.get("receipt_signature")
    try:
        public_key_bytes = base64.b64decode(public_key_b64, validate=True)
        signature = base64.b64decode(signature_text, validate=True) if isinstance(signature_text, str) else b""
    except (binascii.Error, ValueError) as error:
        raise ExpeditionClientError("verification receipt signature is malformed") from error
    derived_key_id = "ED25519-" + hashlib.sha256(public_key_bytes).hexdigest()[:16].upper()
    if len(public_key_bytes) != 32 or len(signature) != 64 or derived_key_id != public_key_id:
        raise ExpeditionClientError("verification receipt signing key is invalid")
    signed_core = {key: value for key, value in receipt.items() if key not in {"receipt_id", "receipt_signature"}}
    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
            signature,
            json.dumps(signed_core, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        )
    except (InvalidSignature, ValueError) as error:
        raise ExpeditionClientError("verification receipt signature is invalid") from error
    return receipt


def verify_remote(
    endpoint: str,
    expedition_id: str,
    submitted: str,
    client_version: str,
    transport: Transport = _default_transport,
    *,
    public_key_b64: str,
    public_key_id: str,
) -> dict[str, object]:
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
    return _validate_receipt(payload, expedition_id, client_version, submitted, public_key_b64, public_key_id)
