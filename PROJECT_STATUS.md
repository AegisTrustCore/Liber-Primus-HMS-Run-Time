# Project Status

Last reviewed: 2026-08-13

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

The Research Archive now contains 8 published Runs, 8 published Results, 3 published Capsules, and 3 curated Run Set packages:

- `RSET-0001`: `RUN-0001`/`RES-0001`, the historical OpenPGP artifact-identity reproduction, and `RUN-0002`/`RES-0002`, the synthetic Expedition-verifier control.
- `RSET-0002`: `RUN-0003` through `RUN-0007` and `RES-0003` through `RES-0007`, covering one historical acquisition null, three bounded Page 32 negatives, and one anti-post-hoc correction.
- `RSET-0003`: published `RUN-0008`/`RES-0008`, the E1059 default-key OutGuess bounded closure with all 75 extraction ledgers and a portable non-mutating verifier.
- `CAP-0001` through `CAP-0003`: the public verification foundation, Page 32 manifest-interpretation closures, and E1059 OutGuess closure.
- Distribution and UX standards separating developer source from customer-ready applications.
- An automated public-boundary scan rejecting workstation paths and local endpoints.

The eight Runs, eight Results, and three Capsules are published through the `main`-branch Research Archive. `RSET-0001` remains `STAGED`; `RSET-0002` and `RSET-0003` are `PUBLISHED` on `main`. `RSET-0003` is also bound to approved gate `RR-0002`. None claims an LP plaintext recovery, and Expedition 001 remains closed pending its exact-subject release approval.

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

Eight first-class Results are now packaged in the Research Archive. `RES-0001` is a narrowly verified provenance-artifact result, `RES-0002` is a software known control, `RES-0003` through `RES-0006` are bounded negative/null Results, `RES-0007` is a correction, and `RES-0008` is the bounded E1059 default-key OutGuess closure. None is a recovery of previously unknown LP plaintext.

The 1,322-file inventory will be converted deliberately rather than bulk-published. The target is a small set of exceptionally reproducible public objects, not an inflated ledger of partially structured hypotheses.

## Immediate focus

1. Keep every status surface synchronized with the canonical Research Archive indexes.
2. Normalize E1477 as the next bounded-rejection candidate while beginning the GP29/Runtime implementation slice.
3. Reconcile Page 72/73 numbering, known-control provenance, and corpus-edition differences before another control publication.
4. Complete GP29 as the reference customer-ready instrument and release it separately.
5. Open Expedition 001 only after its Windows portable verifier is signed and bound to an approved campaign subject.
6. Release HMS Endeavour Lite alpha through a separate capability review.

## Platform launch state

- GitHub: `v0.1.0` public research foundation released; `RSET-0001` is staged, and `RSET-0002` and approved `RSET-0003` are published.
- `main`: protected by an active ruleset requiring pull requests and the `validate` check.
- Patreon: creator page live; first public, Pilgrim, Navigator, Cartographer, and Admiral posts published.
- Public Research Archive: eight Runs, eight Results, and three Capsules are published; `RSET-0001` is staged, while `RSET-0002` and `RSET-0003` are published portable packages.
- Public GP29 Calculator: in development and intentionally excluded from the frozen foundation candidate; planned as a separate tool release.
- Expedition verifier: canonical core, GUI, CLI, tests, and a private Windows portable candidate exist; public download remains unavailable while the campaign is closed.
- Endeavour Lite and Liber Runtime: architecture started; runnable applications remain planned.
- Sockets/API, add-ons, plugin SDK, and advanced applications: planned; no availability claim is made.
- Scope: foundation content merged through PR #1; Expedition 001 remains closed pending its own release.
