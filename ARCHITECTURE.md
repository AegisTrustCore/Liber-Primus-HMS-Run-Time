# Public Architecture Boundary

This repository documents the boundary now so future tools can be built without mixing public evidence, membership delivery, application secrets, or unreleased research.

| Layer | Responsibility | Must not contain |
|---|---|---|
| GitHub / Observer | Public evidence, schemas, verifiers, stable public tools, approved reports, reproduction packages | Credentials, premium entitlement logic, unpublished hypotheses, private correspondence |
| Patreon | Membership, dispatches, previews, release communication, community access | Authoritative application authorization or private Git branches as entitlements |
| HMS Runtime | Hosted living research station, user workspaces, tier-capability enforcement | Client-trusted authorization decisions or embedded secrets |
| Aegis Trust Core | Server-side identity, entitlement, policy, provenance, and trust services | Public disclosure of sensitive policy data or credentials |
| Vault | Unreleased research, private datasets, active validation, proprietary systems | Automatic publication to any tier |

## Future application families

- Liber Runtime and personal research workspace
- Public GP29 calculator and advanced GP Laboratory
- GP Solver and batch experiment engine
- Atlas, page regions, Page Sets, and comparison workspace
- Reproduction, checksum, manifest, ProofLock, and notary systems
- Add-ons and instrument modules
- Socket/API services for authorized integrations
- Plugin SDK and developer tooling

No item in this list is considered available merely because its architecture is acknowledged. Current status is authoritative only in [`instruments/manifest.json`](instruments/manifest.json).

## Security invariants

1. Patreon membership is translated into server-side capabilities; it is not enforced by hiding a GitHub repository.
2. Sockets and APIs authenticate every connection and authorize every operation server-side.
3. Add-ons and plugins receive explicit capabilities, versioned interfaces, scoped data access, and revocable credentials.
4. Public tools never embed production secrets, private datasets, or premium server logic.
5. Research publication and software release remain separate approval tracks.
6. User research remains exportable and is not silently promoted into public evidence.
7. New user research is `PRIVATE` by default and moves through `PROJECT`, `GROUP`, `HMS_REVIEW`, and `PUBLIC` only by explicit action.
8. Capability access and compute allowance are separate entitlements enforced server-side.
9. Local/private projects do not upload source material, notes, or results without an explicit bundle submission.
10. Locked-tool previews expose documentation and sample output, never protected execution or results.

See [PRIVACY.md](PRIVACY.md) for the user-data, local-mode, sharing, and compute contract.
