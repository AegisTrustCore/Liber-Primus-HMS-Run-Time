from __future__ import annotations

import json
import unittest

from hms_tools.expedition_service import ExpeditionServiceError, VerificationService
from hms_tools.expedition_api import handle_verification_request
from hms_tools.expedition_client import ExpeditionClientError, verify_remote


class ExpeditionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = VerificationService(
            {"XPD-TEST": "synthetic accepted vector"},
            b"synthetic-test-signing-key",
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
        self.assertRegex(accepted["receipt_signature"], r"^[a-f0-9]{64}$")

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
        receipt = verify_remote("https://verify.example.test/v1/expeditions/verify", "XPD-TEST", "synthetic accepted vector", "0.3.0", transport)
        self.assertTrue(receipt["accepted"])
        with self.assertRaisesRegex(ExpeditionClientError, "HTTPS"):
            verify_remote("http://example.test/verify", "XPD-TEST", "x", "0.3.0", transport)


if __name__ == "__main__":
    unittest.main()
