# Release Policy

## Hard boundary

This public repository contains intentionally released public material only. Folder location alone is never treated as sufficient classification.

Every publishable research record has two independent release fields:

```text
classification: PUBLIC
publication_status: PUBLISHED
```

No other combination may be committed under `research/records/`.

## Material that stays outside this repository

- Unreleased or supporter-only research
- Active notebooks and raw experiment exhaust
- Premium Runtime source and server-side entitlement logic
- Proprietary solvers, search heuristics, or private datasets
- Unreleased candidate decryptions
- Private correspondence or personal information
- Credentials, tokens, keys, and secrets
- Vault material of any kind

Private material must not be placed on a hidden or secondary branch of this public repository.

## Research publication stages

```text
DISCOVERY → VALIDATION → REPRODUCTION → PUBLICATION REVIEW → APPROVAL → RELEASE
```

## Software publication stages

```text
IDEA → PROTOTYPE → INTERNAL → EXPERIMENTAL → BETA → STABLE → RELEASED
```

These tracks are separate. A software release does not publish private research, and a research publication does not release private tool source.

## Distribution decision

Every approved item also receives an explicit destination:

```text
PUBLIC GITHUB
PATREON — PILGRIM
PATREON — NAVIGATOR
PATREON — CARTOGRAPHER
PATREON — ADMIRAL
HOSTED RUNTIME
KEEP INTERNAL
KEEP IN VAULT
```

GitHub is the stable public evidence and public-tool layer. Patreon is the advanced material, early-access, participation, and member-build layer. Patreon access does not replace public publication review for an approved truth claim.

## Publication checklist

Before release, confirm:

- [ ] The record is classified `PUBLIC`.
- [ ] The record is explicitly `PUBLISHED`.
- [ ] The claim is bounded and uses approved evidence language.
- [ ] Inputs, provenance, versions, and hashes are present.
- [ ] The method and material parameters are disclosed.
- [ ] Reproduction instructions have been run from a clean environment.
- [ ] Controls and limitations are documented.
- [ ] No private paths, credentials, personal data, or Vault references are present.
- [ ] Redistribution rights have been checked.
- [ ] Related negative results, corrections, and superseded records are linked.
- [ ] Automated validation passes.
