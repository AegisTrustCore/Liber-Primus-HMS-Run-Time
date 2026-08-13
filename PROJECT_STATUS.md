# Project Status

Last reviewed: 2026-08-12

## Present in the foundation release candidate

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

## Source audit completed in the candidate branch

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

These candidates remain outside the verified ledger until their inputs, hashes, implementation, controls, and clean reproduction are packaged here.

## Immediate focus

1. Complete the publication-boundary audit and merge the frozen foundation candidate.
2. Tag the reviewed foundation as `v0.1.0`.
3. Release GP29 `v0.1` separately.
4. Open Expedition 001 after the foundation is live.
5. Publish `RC-001` only after clean reproduction and evidence packaging.
6. Release HMS Endeavour Lite alpha through a separate capability review.

## Platform launch state

- GitHub: public repository connected; foundation changes remain in draft PR review.
- `main`: protected by an active ruleset requiring pull requests and the `validate` check.
- Patreon: creator page live; first public, Pilgrim, Navigator, Cartographer, and Admiral posts published.
- Public GP29 Calculator: in development and intentionally excluded from the frozen foundation candidate; planned as the next separate tool release.
- Endeavour Lite and Liber Runtime: architecture started; runnable applications remain planned.
- Sockets/API, add-ons, plugin SDK, and advanced applications: planned; no availability claim is made.
- Scope freeze: PR #1 accepts only foundation-boundary corrections until merge; Expedition 001 remains closed.
