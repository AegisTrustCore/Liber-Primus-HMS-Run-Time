# Expedition sealed verification service

Status: **deployment candidate; campaign remains closed**

This directory packages the v0.3 verification authority as a non-root, platform-neutral container. It exposes:

- `GET /healthz` for an unprivileged liveness check;
- `POST /v1/expeditions/verify` for the exact JSON verification contract.

The container does not contain an answer, signing key, endpoint, TLS private key, or deployment credential. Inject the answer and signing key from the chosen host's secret manager at runtime. Prefer `HMS_EXPEDITION_SIGNING_KEY_B64` containing exactly 32 random decoded bytes. Never set both signing-key variables.

Required runtime values:

- `HMS_XPD_0001_ANSWER`
- exactly one of `HMS_EXPEDITION_SIGNING_KEY_B64` or `HMS_EXPEDITION_SIGNING_KEY`

Optional bounded controls:

- `HMS_EXPEDITION_MAX_ATTEMPTS` (default `10`)
- `HMS_EXPEDITION_WINDOW_SECONDS` (default `300`)
- `HMS_EXPEDITION_MAX_TRACKED_CLIENTS` (default `10000`)
- `HMS_EXPEDITION_TRUSTED_PROXIES` (comma-separated proxy CIDRs; empty by default)

The TLS gateway must strip or replace incoming forwarding headers, suppress bodies and query strings from logs, apply an additional edge rate limit, and pass only trusted proxy traffic to the container. The application ignores forwarded identity unless the immediate peer is inside a configured trusted network.

Build from the repository root:

```text
docker build --file deploy/expedition-service/Dockerfile --tag hms-expedition-service:0.3.0 .
```

Deployment is not approval. Bind the immutable image digest, endpoint, edge policy, redacted-log inspection, accepted/rejected private UAT, client package checksum, and human decision in the joint deployment gate before opening the campaign.

Receipt authenticity uses Ed25519. Derive the public key from the deployment private key, record its `ED25519-…` identifier, and place only those public values in the client manifest. The public client rejects altered, replayed-for-another-submission, or incorrectly signed receipts.
