# Expedition 001 solution-leak audit

Date: 2026-08-14

Decision: **XPD-0001 v0.2.0 OFFLINE CANDIDATE REJECTED**

## Finding

The public v0.2.0 manifest contains an unkeyed SHA-256 digest of an answer constrained to exactly five letters. That space contains only 26^5, or 11,881,376, candidates. A determined participant can enumerate the complete space and compare each digest locally.

SHA-256 is operating correctly; the failure is the low-entropy input space. Calling this representation non-reversible would be misleading. Obfuscating the digest inside an executable would not repair the boundary because a public offline verifier necessarily contains an extractable or queryable acceptance predicate.

## Required architecture

- No answer, answer digest, keyed answer commitment, or equivalent acceptance secret ships in public source or binaries.
- The downloadable client sends an explicit submission to a TLS-protected verification service.
- The service normalizes and compares against a deployment secret using constant-time comparison.
- The service enforces both application and edge rate limits and returns only accepted/rejected state plus a signed, non-plaintext receipt.
- Request bodies and normalized answers must not be logged.
- Public clients disclose that submission verification requires a network request.
- The campaign remains closed until the exact service deployment and configured client package pass accepted/rejected, abuse-control, privacy, clean-environment UAT, and human approval gates.

## Residual limits

No public puzzle can prevent participants from solving or sharing its answer. The service boundary prevents the official verifier from becoming a cheap offline oracle; it does not promise absolute secrecy against collaboration, distributed guessing, endpoint compromise, or inference from the puzzle itself.

## Release consequence

The v0.2.0 package must not be published. Its release gate is superseded by the v0.3.0 secure-verification redesign. Tiered posts, timed hints, badges, and the full solution remain inactive.

Because the rejected digest persists in public Git history, v0.3.0 also rotates the extraction positions. The value accepted by v0.2.0 can never pass the new verification service.
