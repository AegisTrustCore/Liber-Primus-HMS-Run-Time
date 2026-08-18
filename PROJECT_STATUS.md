# Project Status

Last reviewed: 2026-08-17

## Released in the `v0.1.0` foundation

- Public repository boundary and release philosophy
- Evidence, publication, and access-status definitions
- Machine-readable research-record and page-dossier schemas
- Public validation script and automated validation workflow
- Audit dossiers for Pages 32, 72, and 73
- Separate ledgers for verified, open, negative, corrected, and retracted work
- A reproducible source-inventory tool and sanitized intake report
- Protected-branch and pull-request governance
- Public research index, known-control ledger, and correction ledger
- Patreon membership boundary and pre-launch publication kit
- Machine-readable instrument status registry
- Historical Cicada 3301 OpenPGP key, full-fingerprint record, and non-affiliation boundary
- GP29 Calculator interface and release boundary; executable release held for post-foundation `v0.1`
- Public status-level roadmap for five LP release candidates; exact research queue retained privately
- Canonical object/provenance model, deterministic environment manifest, and mandatory human-controlled Public Release Gate
- Research privacy, compute-entitlement, discovery disclosure, release-signing, and free-workflow contracts

## Published on `main` after the frozen foundation

The Research Archive now contains 11 published Runs, 11 published Results, 4 published Capsules, and 4 curated Run Set packages:

- `RSET-0001`: `RUN-0001`/`RES-0001`, the historical OpenPGP artifact-identity reproduction, and `RUN-0002`/`RES-0002`, the synthetic Expedition-verifier control.
- `RSET-0002`: `RUN-0003` through `RUN-0007` and `RES-0003` through `RES-0007`, covering one historical acquisition null, three bounded Page 32 negatives, and one anti-post-hoc correction.
- `RSET-0003`: published `RUN-0008`/`RES-0008`, the E1059 default-key OutGuess bounded closure with all 75 extraction ledgers and a portable non-mutating verifier.
- `RSET-0004`: `RUN-0009` through `RUN-0011` and `RES-0009` through `RES-0011`, covering the E1477 direct-board closure, E156 solved-LP1 segment frames, and E159 terminal known controls.
- `CAP-0001` through `CAP-0004`: the public verification foundation, Page 32 manifest-interpretation closures, E1059 OutGuess closure, and the segment-runtime control capsule.
- Distribution and UX standards separating developer source from customer-ready applications.
- An automated public-boundary scan rejecting workstation paths and local endpoints.
- Complete navigation for the 75-page Liber Primus working corpus, including a page index, timeline, source-verification guide, and E1059 ledger cross-reference.

The eleven Runs, eleven Results, and four Capsules are published through the `main`-branch Research Archive. `RSET-0001` remains `STAGED`; `RSET-0002` and `RSET-0003` are `PUBLISHED`, and `RSET-0004` is also `PUBLISHED`. `RSET-0003` is bound to approved gate `RR-0002`, and `RSET-0004` is bound to approved gate `RR-0003`. None claims an LP plaintext recovery, and Expedition 001 remains closed pending its exact-subject release approval.

## Source audit included in the foundation

The first-pass audit covered the complete supplied Personal Research tree, including its nested More research collection:

- 1,322 files totaling 3,837,489,779 bytes
- 876 text files and 266 ZIP archives
- 11,541 archive members inventoried; 5,918 text members scanned
- 1,141 structured claim fragments and 115 explicit decision statements extracted
- 43 duplicate-content groups containing 89 file entries
- 3 potentially sensitive-name flags held outside the public repository

These are intake measurements, not measures of correctness. The public summary is in [SOURCE_AUDIT_2026-08-12.md](audit/SOURCE_AUDIT_2026-08-12.md). The raw inventory remains private because it contains local paths and potentially sensitive metadata.

A separate initial scan of the active HMS/Aegis workspace found 889 Liber Runtime directories plus priority Page 32, 72, and 73 artifacts. Those counts remain a second source stream and are not merged into the totals above.

## Evidence position

No HMS-originated recovery of previously unknown Liber Primus plaintext is currently published as verified in this repository.

The audit did identify publication candidates in four distinct classes:

1. Reproductions on already-solved LP material, suitable as positive controls.
2. Bounded structural observations, especially on Page 32.
3. Negative results that reject named transformation families without claiming universal impossibility.
4. A correction retracting an overly strong Page 73 causal-selector interpretation.

Eleven first-class Results are now packaged in the Research Archive. `RES-0001` is a narrowly verified provenance-artifact result; `RES-0002` is a software known control; `RES-0003` through `RES-0006` are bounded negative/null Results; `RES-0007` is a correction; `RES-0008` is the bounded E1059 default-key OutGuess closure; and `RES-0009` through `RES-0011` add the E1477 bounded closure, E156 structural control, and E159 terminal known controls. None is a recovery of previously unknown LP plaintext.

The 1,322-file inventory will be converted deliberately rather than bulk-published. The target is a small set of exceptionally reproducible public objects, not an inflated ledger of partially structured hypotheses.

## Immediate focus

1. Keep every status surface synchronized with the canonical Research Archive indexes.
2. Build and qualify the new Corpus Manifest Verifier `0.2` nautical viewer package; rc.3 is superseded before publication.
3. Qualify, leak-audit, and approve the Expedition 001 customer package before opening its public campaign.
4. Complete final visual UAT and owner approval for HMS Endeavour Runtime Environment v1; its privacy/recovery controls, embedded Atlas, research objects, bounded experiment, and structural comparison are implemented.
5. Keep approved RR-0003 synchronized while continuing Page 72/73 provenance reconciliation as a separate research lane without displacing the customer-tool sequence.

The staged product, access, dependency, and human-gate architecture is now frozen in the [HMS Product Ladder](docs/HMS_PRODUCT_LADDER.md). The mature application direction is recorded separately and does not change current availability.

## Platform launch state

- GitHub: `v0.1.0` public research foundation, research releases `RR-0002` and `RR-0003`, and the `GP29-v0.1.1` public calculator are released; `RSET-0001` is staged, while `RSET-0002` through `RSET-0004` are published.
- `main`: protected by an active ruleset requiring pull requests and the `validate` check.
- Patreon: creator page live; first public, Pilgrim, Navigator, Cartographer, and Admiral posts published, including the free PUBLIC-005 GP29 v0.1.1 release notice.
- Public Research Archive: eleven Runs, eleven Results, and four Capsules are published; `RSET-0001` is staged, while `RSET-0002`, `RSET-0003`, and owner-approved `RSET-0004` are released portable packages.
- Public GP29 Calculator: v0.1.1 is released as a free Observer-level Windows desktop and CLI download with an approved exact-subject gate and recorded acceptance limitation.
- Expedition verifier: the v0.2.0 offline candidate was rejected after its five-letter digest failed the solution-leak audit. The v0.3.0 sealed-service/client deployment candidate now provides Ed25519-verified receipts, replay binding, bounded application rate controls, trusted-proxy handling, a non-root container, OpenAPI contract, and deterministic Windows packaging. No host, endpoint, production key, or customer download is public; deployment qualification, human UAT, and the campaign-opening decision remain pending.
- Corpus navigation: the complete 75-page working-corpus map, timeline, page index, and verification route are public.
- Corpus Manifest Verifier: the qualified `0.1.0-rc.3` subject is retained for audit but superseded before publication. `0.2.0-dev` adds the Aegis/HMS nautical shell and a selectable embedded 75-page viewer and requires a new package gate.
- HMS Endeavour Lite: `0.2.0-dev` is the bounded free workstation direction for GitHub. Its exact public feature and package boundary are still being frozen.
- HMS Endeavour Runtime Environment: `1.1.0-dev` is now a separate private member prototype with all 75 registered pages, page tabs, fit/zoom/pan, visual regions, page-scoped rune selection, translation notes, and local workspace persistence. It is not a public GitHub download or current Patreon benefit. Hosted Runtime remains separate and not built.
- Sockets/API, add-ons, plugin SDK, and advanced applications: planned; no availability claim is made.
- Scope: public status and identity records reflect the current merged service and workstation candidates; Expedition 001 remains closed pending deployment qualification and its own exact-subject release decision.
