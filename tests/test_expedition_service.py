from __future__ import annotations

import json
import io
import os
import hashlib
import unittest
from unittest.mock import patch

from hms_tools.expedition_service import ExpeditionServiceError, VerificationService
from hms_tools.expedition_api import handle_verification_request
from hms_tools.expedition_client import ExpeditionClientError, verify_remote
from scripts.serve_expedition_verifier import _client_identity, _trusted_proxy_networks, application, create_application_from_environment


class ExpeditionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = VerificationService(
            {"XPD-TEST": "synthetic accepted vector"},
            hashlib.sha256(b"synthetic-test-signing-key").digest(),
            max_attempts=2,
            clock=lambda: 100.0,
        )

    def test_accepts_and_rejects_without_returning_plaintext(self) -> None:
        accepted = self.service.verify("XPD-TEST", "synthetic accepted vector", "0.3.0", "client-a", verified_at="2026-08-14T00:00:00Z")
        rejected = self.service.verify("XPD-TEST", "deliberate nonmatch", "0.3.0", "client-b", verified_at="2026-08-14T00:00:00Z")
        self.assertTrue(accepted["accepted"])
        self.assertFalse(rejected["accepted"])
        rendered = json.dumps([accepted, rejected])
        self.assertNotIn("synthetic accepted vector", rendered)
        self.assertNotIn("deliberate nonmatch", rendered)
        self.assertTrue(accepted["server_verified"])
        self.assertRegex(accepted["receipt_signature"], r"^[A-Za-z0-9+/]{86}==$")

    def test_rate_limit_is_enforced_per_client(self) -> None:
        self.service.verify("XPD-TEST", "wrong-one", "0.3.0", "client-a")
        self.service.verify("XPD-TEST", "wrong-two", "0.3.0", "client-a")
        with self.assertRaisesRegex(ExpeditionServiceError, "RATE_LIMITED"):
            self.service.verify("XPD-TEST", "wrong-three", "0.3.0", "client-a")

    def test_unknown_and_empty_requests_are_rejected(self) -> None:
        with self.assertRaisesRegex(ExpeditionServiceError, "unknown expedition"):
            self.service.verify("XPD-NOPE", "answer", "0.3.0", "client-a")
        with self.assertRaisesRegex(ExpeditionServiceError, "empty"):
            self.service.verify("XPD-TEST", "---", "0.3.0", "client-b")

    def test_json_api_accepts_exact_contract_and_rejects_extra_fields(self) -> None:
        request = json.dumps({"expedition_id":"XPD-TEST","submission":"synthetic accepted vector","client_version":"0.3.0"}).encode()
        status, receipt = handle_verification_request(self.service, request, "client-api")
        self.assertEqual(status, 200)
        self.assertTrue(receipt["accepted"])
        status, error = handle_verification_request(self.service, b'{"expedition_id":"XPD-TEST","submission":"x","client_version":"0.3.0","extra":true}', "client-extra")
        self.assertEqual((status, error), (400, {"error":"INVALID_REQUEST"}))

    def test_public_client_accepts_service_receipt_and_rejects_insecure_endpoint(self) -> None:
        def transport(_endpoint: str, body: bytes):
            status, payload = handle_verification_request(self.service, body, "client-transport")
            return status, json.dumps(payload).encode()
        receipt = verify_remote("https://verify.example.test/v1/expeditions/verify", "XPD-TEST", "synthetic accepted vector", "0.3.0", transport, public_key_b64=self.service.public_key_b64, public_key_id=self.service.public_key_id)
        self.assertTrue(receipt["accepted"])
        with self.assertRaisesRegex(ExpeditionClientError, "HTTPS"):
            verify_remote("http://example.test/verify", "XPD-TEST", "x", "0.3.0", transport, public_key_b64=self.service.public_key_b64, public_key_id=self.service.public_key_id)
        with self.assertRaisesRegex(ExpeditionClientError, "query"):
            verify_remote("https://example.test/verify?debug=1", "XPD-TEST", "x", "0.3.0", transport, public_key_b64=self.service.public_key_b64, public_key_id=self.service.public_key_id)

    def test_public_client_rejects_receipt_replay_for_different_submission(self) -> None:
        receipt = self.service.verify("XPD-TEST", "synthetic accepted vector", "0.3.0", "replay-source")
        def replay_transport(_endpoint: str, _body: bytes):
            return 200, json.dumps(receipt).encode()
        with self.assertRaisesRegex(ExpeditionClientError, "does not match"):
            verify_remote("https://verify.example.test/v1/expeditions/verify", "XPD-TEST", "different", "0.3.0", replay_transport, public_key_b64=self.service.public_key_b64, public_key_id=self.service.public_key_id)

    def test_public_client_rejects_tampered_signed_receipt(self) -> None:
        receipt = self.service.verify("XPD-TEST", "synthetic accepted vector", "0.3.0", "tamper-source")
        receipt["accepted"] = False
        def tamper_transport(_endpoint: str, _body: bytes):
            return 200, json.dumps(receipt).encode()
        with self.assertRaisesRegex(ExpeditionClientError, "signature is invalid"):
            verify_remote("https://verify.example.test/v1/expeditions/verify", "XPD-TEST", "synthetic accepted vector", "0.3.0", tamper_transport, public_key_b64=self.service.public_key_b64, public_key_id=self.service.public_key_id)

    def test_window_recovers_and_client_table_is_bounded(self) -> None:
        now = [100.0]
        service = VerificationService(
            {"XPD-TEST": "answer"},
            hashlib.sha256(b"synthetic-bounded-key").digest(),
            max_attempts=1,
            window_seconds=10,
            max_tracked_clients=2,
            clock=lambda: now[0],
        )
        service.verify("XPD-TEST", "x", "0.3.0", "one")
        with self.assertRaisesRegex(ExpeditionServiceError, "RATE_LIMITED"):
            service.verify("XPD-TEST", "x", "0.3.0", "one")
        now[0] = 111.0
        service.verify("XPD-TEST", "x", "0.3.0", "one")
        service.verify("XPD-TEST", "x", "0.3.0", "two")
        service.verify("XPD-TEST", "x", "0.3.0", "three")
        self.assertLessEqual(len(service._windows), 2)

    def test_wsgi_health_security_headers_and_trusted_proxy_identity(self) -> None:
        app = application(self.service)
        captured = {}
        def start_response(status, headers):
            captured.update(status=status, headers=dict(headers))
        body = b"".join(app({"REQUEST_METHOD":"GET", "PATH_INFO":"/healthz", "wsgi.input":io.BytesIO(b"")}, start_response))
        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(captured["headers"]["Cache-Control"], "no-store")
        self.assertEqual(json.loads(body)["status"], "ok")
        trusted = _trusted_proxy_networks("10.0.0.0/8")
        self.assertEqual(_client_identity({"REMOTE_ADDR":"203.0.113.9", "HTTP_X_FORWARDED_FOR":"198.51.100.1"}, trusted), "203.0.113.9")
        self.assertEqual(_client_identity({"REMOTE_ADDR":"10.0.0.2", "HTTP_X_FORWARDED_FOR":"198.51.100.1, 10.0.0.1"}, trusted), "198.51.100.1")

    def test_environment_factory_fails_closed_and_accepts_base64_key(self) -> None:
        clean = {key: value for key, value in os.environ.items() if not key.startswith("HMS_EXPEDITION_") and key != "HMS_XPD_0001_ANSWER"}
        with patch.dict(os.environ, clean, clear=True):
            with self.assertRaises(ExpeditionServiceError):
                create_application_from_environment()
            os.environ["HMS_XPD_0001_ANSWER"] = "synthetic"
            os.environ["HMS_EXPEDITION_SIGNING_KEY_B64"] = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
            self.assertTrue(callable(create_application_from_environment()))


if __name__ == "__main__":
    unittest.main()
