# Public Release Gate

Nothing reaches `main`, a GitHub Release, an official HMS public endpoint, or the public evidence ledger merely because automated tests pass.

## Immutable release subject

Every gate binds approval to one canonical manifest under `releases/manifests/`. The bound subject records:

- the exact candidate commit SHA;
- the canonical release-manifest path and SHA-256;
- the deterministic environment ID;
- the subject schema version;
- the intended tag.

The human approval record repeats the approved manifest digest. The digest is computed from canonical JSON—UTF-8, sorted object keys, compact separators, and no insignificant whitespace—so line-ending and formatting differences cannot change the subject. If the manifest's semantic content, candidate commit, environment, intended tag, or subject digest changes, validation fails and the existing approval is invalid. A modified subject must return to `PENDING` and receive a new named human decision.

## Common and type-specific gates

Every public release requires a machine-readable gate record under `releases/gates/`.

The common gate applies to every release:

1. Classification is `PUBLIC`.
2. Publication status is explicitly approved.
3. Secrets, credentials, personal data, private paths, and Vault material are absent.
4. Rights and redistribution provenance were reviewed.
5. The complete provenance chain is present or gaps are disclosed.
6. A deterministic environment manifest is attached.
7. Public links were tested.
8. Automated validation passed.
9. A named human explicitly approved the exact release subject.

The release then supplies exactly one matching type gate:

- **Software:** tests, package hashes, dependency manifest, security scan, reproducible build, and release notes.
- **Research:** bounded claims, complete-family retention, controls, corrections, and clean reproduction.
- **Expedition:** solution state, verifier, challenge-state consistency, and bounded research claims.
- **Publication:** bounded claims, cited sources, corrections, and evidence links.

Research-only checks are not forced onto software releases, and software packaging checks are not used as substitutes for research evidence.

## Enforced state machine

- `APPROVED` requires every common and selected type check to be `true`, `publication_approved: true`, named human approval, an approval time, and a digest matching the current release subject.
- `PENDING` requires `publication_approved: false`, `human_approval.approved: false`, and null approval identity, time, and subject digest.
- Contradictory states fail both JSON Schema and the standard-library validator.

Automation may reject an incomplete release. It may never supply human approval, change `PENDING` to `APPROVED`, merge a PR, create an official tag, or publish a public claim on its own.

## Separate version systems

- Software uses semantic versions such as `v0.1.0` and `v0.2.0`.
- Research uses permanent object IDs such as `RR-0001`, `RES-0001`, and `PL-0001`.
- Expeditions use `XPD-0001`.
- Patreon transmission IDs are delivery metadata, not research versions.

## Release authenticity

Official releases must include an annotated cryptographically signed Git tag, a `SHA256SUMS` file for distributed packages, a detached signature where the distribution channel supports it, and the signing-key fingerprint in the release notes. Unsigned snapshots, branches, CI artifacts, and Patreon attachments are not official HMS software releases.

The approved foundation gate is [releases/gates/v0.1.0.json](releases/gates/v0.1.0.json), bound to its [canonical release manifest](releases/manifests/v0.1.0.json).
