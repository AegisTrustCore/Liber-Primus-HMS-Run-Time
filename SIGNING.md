# Official Release Signing

Official HMS software releases must be attributable to a documented HMS signing identity.

## Current signing identity

The `v0.1.x` release series uses OpenPGP fingerprint:

`7B4E 8795 A984 2FB0 4301 114B 7A7B 2779 E2F1 8AE6`

This HMS release key is distinct from the historical Cicada 3301 evidence key. Verification material is attached to the GitHub Release; the private key remains outside the repository and publication workflow.

## Required artifacts

- Annotated, cryptographically signed Git tag.
- `SHA256SUMS` covering every distributed package.
- Detached signature for `SHA256SUMS` where supported.
- Signing-key fingerprint and verification commands in the GitHub Release notes.
- Immutable link to the approved Public Release Gate record.

## Operational boundary

Private signing keys never enter this repository, CI logs, Patreon, the Runtime client, or Codex context. Signing is an explicit human-controlled release action. Key rotation publishes the old and new fingerprints, effective time, reason, and cross-signature when available.

Branches, pull requests, source archives generated automatically by GitHub, CI artifacts, and Patreon attachments are not official releases unless the release notes explicitly bind their hashes to a signed release.

The historical Cicada 3301 public key is an evidence artifact only and must never be used or presented as an HMS signing identity.
