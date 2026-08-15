# Expedition verification service deployment gate

Status: **REQUIRED BEFORE XPD-0001 CAN OPEN**

This gate applies jointly to the deployed v0.3.0 verification service and the exact Windows client configured to call it. Neither subject may be approved alone.

## Secret preparation

- Derive the rotated v0.3.0 answer independently from the approved puzzle package.
- Store it only in the deployment secret manager as `HMS_XPD_0001_ANSWER`.
- Generate a separate random 32-byte Ed25519 private key and store its base64 form as `HMS_EXPEDITION_SIGNING_KEY_B64`.
- Derive the Ed25519 public key and key ID, then bind both into the exact client manifest before packaging. The client must verify every receipt signature locally.
- Never place either value in Git, CI logs, build arguments, container layers, screenshots, Patreon drafts, or client configuration.
- Record secret custody and rotation authority privately.

## Service boundary

- Terminate TLS at an approved proxy and expose only `POST /v1/expeditions/verify`.
- Limit bodies to 4,096 bytes and require `application/json`.
- Disable request-body, query-string, header, environment, and exception dumps that could retain submissions or secrets.
- Apply edge rate limits in addition to the application limit; document the effective attempt budget and reset period.
- Ensure proxy-derived client identity cannot be spoofed by an untrusted header.
- Return `Cache-Control: no-store` and no proximity, spelling, length, or normalization hints.
- Restrict deployment and secret access by least privilege; enable audit and revocation.

## Exact tests

- Synthetic service self-tests pass without production secrets.
- One private rotated-answer submission is accepted.
- At least two deliberate nonmatches are rejected identically.
- Empty, malformed, oversized, unknown-expedition, extra-field, and wrong-content-type requests are rejected.
- Rate limiting returns HTTP 429 and recovers after the declared window.
- Service outage, invalid TLS, invalid JSON, and malformed receipts make the client fail closed.
- Receipts contain no submitted plaintext and validate against the v2 schema.
- Replayed receipts, altered acceptance states, mismatched submission hashes, wrong public keys, and malformed signatures fail closed in the client.
- Server logs, proxy logs, traces, metrics, alerts, and crash records contain neither test plaintext nor secrets.
- The old v0.2.0 accepted value is rejected.

## Client/package tests

- The public manifest contains no answer digest and binds only the approved HTTPS endpoint, Ed25519 public key, and derived key ID.
- The package contains no production secret, answer commitment, tier-only content, or private route.
- CLI and GUI accepted/rejected flows agree.
- Instructions and synthetic self-tests remain usable during a service outage.
- The user is told before submission that the answer is sent to the official service.
- ZIP member checksums, Defender scan, reproducible build, clean-environment Windows UAT, and exact-subject approval pass.

## Opening decision

Only after every item passes may the challenge status change from `DRAFT` to `OPEN`, the configured package receive an approved release gate, the GitHub asset be uploaded, or scheduled Patreon materials be activated. The complete solution remains sealed until the separately approved campaign-close release.
