# Project Status

Last reviewed: 2026-08-12

## Available now

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

## Source audit completed

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

1. Resolve corpus provenance and page-numbering differences.
2. Package the E143-E145 solved-page decoder replay as a positive control.
3. Package the E156-E160 Page 73 and Page 74 replays as known controls.
4. Reproduce the strongest Page 32 structural claim from canonical input.
5. Publish the Page 73 correction beside any retained transform result.
6. Package the first bounded negative-result record.

## Platform launch state

- GitHub: public repository connected; foundation changes remain in draft PR review.
- `main`: protected by an active ruleset requiring pull requests and the `validate` check.
- Patreon: tiers configured, creator page still unpublished.
- Runtime, GP Calculator, sockets/API, add-ons, plugin SDK, and advanced applications: planned; no availability claim is made.
