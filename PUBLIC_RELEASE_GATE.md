# Public Release Gate

Nothing reaches `main`, a GitHub Release, an official HMS public endpoint, or the public evidence ledger merely because automated tests pass.

## Required gate

Every public release requires a machine-readable gate record under `releases/gates/` with all of the following:

1. Classification is `PUBLIC`.
2. Publication status is explicitly approved.
3. The claim and evidence status are correctly bounded.
4. Secrets, credentials, personal data, private paths, and Vault material are absent.
5. Rights and redistribution provenance were reviewed.
6. Source and derived-object hashes are present.
7. The complete provenance chain is present or gaps are disclosed.
8. A deterministic environment manifest is attached.
9. Reproduction instructions passed in a clean environment.
10. Complete search families, controls, limitations, corrections, and superseded records are linked where applicable.
11. Public links were tested.
12. Automated validation passed.
13. A named human explicitly approved the publication.

Automation may reject an incomplete release. It may never supply human approval, change `PENDING` to `APPROVED`, merge a PR, create an official tag, or publish a public claim on its own.

## Separate version systems

- Software uses semantic versions such as `v0.1.0` and `v0.2.0`.
- Research uses permanent object IDs such as `RR-0001`, `RES-0001`, and `PL-0001`.
- Expeditions use `XPD-0001`.
- Patreon transmission IDs are delivery metadata, not research versions.

## Release authenticity

Official releases must include an annotated cryptographically signed Git tag, a `SHA256SUMS` file for distributed packages, a detached signature where the distribution channel supports it, and the signing-key fingerprint in the release notes. Unsigned snapshots, branches, CI artifacts, and Patreon attachments are not official HMS software releases.

The pending foundation gate is [releases/gates/v0.1.0.json](releases/gates/v0.1.0.json).
