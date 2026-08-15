#!/usr/bin/env python3
"""Run the local reference Expedition verification API; production requires TLS and edge controls."""

from __future__ import annotations

import json
import os
import sys
import base64
import binascii
import ipaddress
import hashlib
from pathlib import Path
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.expedition_api import MAX_REQUEST_BYTES, handle_verification_request
from hms_tools.expedition_service import ExpeditionServiceError, VerificationService


def _trusted_proxy_networks(value: str) -> tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]:
    if not value.strip():
        return ()
    return tuple(ipaddress.ip_network(item.strip(), strict=False) for item in value.split(",") if item.strip())


def _client_identity(environ, trusted: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]) -> str:
    remote_text = str(environ.get("REMOTE_ADDR", ""))
    try:
        remote = ipaddress.ip_address(remote_text)
    except ValueError:
        return "invalid-peer"
    if not any(remote in network for network in trusted):
        return str(remote)
    forwarded = [item.strip() for item in str(environ.get("HTTP_X_FORWARDED_FOR", "")).split(",") if item.strip()]
    chain = forwarded + [str(remote)]
    for item in reversed(chain):
        try:
            address = ipaddress.ip_address(item)
        except ValueError:
            continue
        if not any(address in network for network in trusted):
            return str(address)
    return str(remote)


def application(service: VerificationService, trusted_proxy_networks=()):
    def app(environ, start_response):
        method = environ.get("REQUEST_METHOD")
        path = environ.get("PATH_INFO")
        if method == "GET" and path == "/healthz":
            status, payload = 200, {"status": "ok", "service": "HMS_EXPEDITION_SERVICE"}
        elif method != "POST" or path != "/v1/expeditions/verify":
            status, payload = 404, {"error": "NOT_FOUND"}
        elif environ.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower() != "application/json":
            status, payload = 415, {"error": "JSON_REQUIRED"}
        else:
            try:
                length = int(environ.get("CONTENT_LENGTH") or "0")
            except ValueError:
                length = MAX_REQUEST_BYTES + 1
            if length < 0:
                length = MAX_REQUEST_BYTES + 1
            body = environ["wsgi.input"].read(min(length, MAX_REQUEST_BYTES + 1))
            status, payload = handle_verification_request(service, body, _client_identity(environ, trusted_proxy_networks))
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        labels = {200:"200 OK",400:"400 Bad Request",404:"404 Not Found",413:"413 Content Too Large",415:"415 Unsupported Media Type",429:"429 Too Many Requests"}
        start_response(labels[status], [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(encoded))),
            ("Cache-Control", "no-store"),
            ("Content-Security-Policy", "default-src 'none'"),
            ("Referrer-Policy", "no-referrer"),
            ("X-Content-Type-Options", "nosniff"),
        ])
        return [encoded]
    return app


def create_application_from_environment():
    answer = os.environ.get("HMS_XPD_0001_ANSWER")
    raw_key = os.environ.get("HMS_EXPEDITION_SIGNING_KEY")
    encoded_key = os.environ.get("HMS_EXPEDITION_SIGNING_KEY_B64")
    if not answer or bool(raw_key) == bool(encoded_key):
        raise ExpeditionServiceError("answer and exactly one signing-key environment variable are required")
    if encoded_key:
        try:
            signing_key = base64.b64decode(encoded_key, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ExpeditionServiceError("signing key is not valid base64") from error
    else:
        signing_key = raw_key.encode("utf-8")
    max_attempts = int(os.environ.get("HMS_EXPEDITION_MAX_ATTEMPTS", "10"))
    window_seconds = int(os.environ.get("HMS_EXPEDITION_WINDOW_SECONDS", "300"))
    max_clients = int(os.environ.get("HMS_EXPEDITION_MAX_TRACKED_CLIENTS", "10000"))
    trusted = _trusted_proxy_networks(os.environ.get("HMS_EXPEDITION_TRUSTED_PROXIES", ""))
    service = VerificationService(
        {"XPD-0001": answer},
        signing_key,
        max_attempts=max_attempts,
        window_seconds=window_seconds,
        max_tracked_clients=max_clients,
    )
    return application(service, trusted)


def service_self_test() -> bool:
    service = VerificationService(
        {"XPD-SELF-TEST": "KNOWNCONTROL"},
        hashlib.sha256(b"synthetic-container-signing-key").digest(),
        max_attempts=3,
    )
    accepted = service.verify("XPD-SELF-TEST", "known control", "0.3.0", "self-test-a", verified_at="2026-01-01T00:00:00Z")
    rejected = service.verify("XPD-SELF-TEST", "deliberate nonmatch", "0.3.0", "self-test-b", verified_at="2026-01-01T00:00:00Z")
    rendered = json.dumps([accepted, rejected], sort_keys=True)
    return (
        accepted["accepted"] is True
        and rejected["accepted"] is False
        and accepted["solution_disclosed"] is False
        and "KNOWNCONTROL" not in rendered
        and "deliberate nonmatch" not in rendered
    )


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        passed = service_self_test()
        print(json.dumps({"service": "HMS_EXPEDITION_SERVICE", "self_test": "PASS" if passed else "FAIL"}))
        return 0 if passed else 1
    host = os.environ.get("HMS_EXPEDITION_BIND")
    if not host:
        print("ERROR: HMS_EXPEDITION_BIND is required; expose this reference only through an approved TLS proxy.", file=sys.stderr)
        return 2
    try:
        app = create_application_from_environment()
        port = int(os.environ.get("HMS_EXPEDITION_PORT", "8765"))
    except (ExpeditionServiceError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"Reference verifier listening on http://{host}:{port}; place behind approved TLS, log-redaction, and edge-rate-limit controls before public use.")
    with make_server(host, port, app) as server:
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
