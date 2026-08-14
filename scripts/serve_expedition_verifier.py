#!/usr/bin/env python3
"""Run the local reference Expedition verification API; production requires TLS and edge controls."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.expedition_api import MAX_REQUEST_BYTES, handle_verification_request
from hms_tools.expedition_service import VerificationService


def application(service: VerificationService):
    def app(environ, start_response):
        if environ.get("REQUEST_METHOD") != "POST" or environ.get("PATH_INFO") != "/v1/expeditions/verify":
            status, payload = 404, {"error": "NOT_FOUND"}
        elif environ.get("CONTENT_TYPE", "").split(";", 1)[0].strip().lower() != "application/json":
            status, payload = 415, {"error": "JSON_REQUIRED"}
        else:
            try:
                length = int(environ.get("CONTENT_LENGTH") or "0")
            except ValueError:
                length = MAX_REQUEST_BYTES + 1
            body = environ["wsgi.input"].read(min(length, MAX_REQUEST_BYTES + 1))
            status, payload = handle_verification_request(service, body, environ.get("REMOTE_ADDR", "unknown"))
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        labels = {200:"200 OK",400:"400 Bad Request",404:"404 Not Found",413:"413 Content Too Large",415:"415 Unsupported Media Type",429:"429 Too Many Requests"}
        start_response(labels[status], [("Content-Type", "application/json"), ("Content-Length", str(len(encoded))), ("Cache-Control", "no-store")])
        return [encoded]
    return app


def main() -> int:
    answer = os.environ.get("HMS_XPD_0001_ANSWER")
    signing_key = os.environ.get("HMS_EXPEDITION_SIGNING_KEY")
    if not answer or not signing_key or len(signing_key) < 32:
        print("ERROR: HMS_XPD_0001_ANSWER and a 32+ character HMS_EXPEDITION_SIGNING_KEY are required.", file=sys.stderr)
        return 2
    service = VerificationService({"XPD-0001": answer}, signing_key.encode("utf-8"))
    host = os.environ.get("HMS_EXPEDITION_BIND")
    if not host:
        print("ERROR: HMS_EXPEDITION_BIND is required; expose this reference only through an approved TLS proxy.", file=sys.stderr)
        return 2
    port = int(os.environ.get("HMS_EXPEDITION_PORT", "8765"))
    print(f"Reference verifier listening on http://{host}:{port}; place behind approved TLS, log-redaction, and edge-rate-limit controls before public use.")
    with make_server(host, port, application(service)) as server:
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
