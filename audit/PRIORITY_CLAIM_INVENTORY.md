# Priority Claim Inventory — Initial Triage

Date: 2026-08-12
Status: **FIRST-PASS SOURCE AUDIT COMPLETE; REPRODUCTION PENDING**

This is a public audit-status report, not a research release. It records bounded readings of selected high-priority artifacts after the supplied source tree was hash-inventoried and its text records scanned. Every item still requires canonical-input review, clean reproduction, rights review, and explicit publication approval.

## Status language

- **Known control** — independently available solved material used to test HMS behavior
- **Local promotion** — an internal experiment passed its own declared local gate
- **Negative candidate** — an internal experiment declared a bounded family rejected
- **Post-discovery candidate** — a relationship was identified after inspecting the target and requires especially careful holdout review
- **Unreviewed** — not yet examined in this publication audit

“Local promotion” is not equivalent to public verification.

## Page 32

| Artifact | Internal decision | Initial public triage | Boundary |
|---|---|---|---|
| E865 | Direct base-29 N/Q subset route rejected | Negative candidate | Rejected four frozen direct selector families under matched shuffled-cell controls |
| E866 | Address/state word board rejected | Negative candidate | Best language-like surface was common under shuffled-board controls |
| E868 | Known LP1 transform then whole-block checksum rejected | Negative candidate | Zero of sixteen checksum matches; controls did not support closure |

Initial finding: the reviewed Page 32 documents contain useful bounded rejections. They do not report Page 32 plaintext recovery. Many other Page 32 artifacts remain unreviewed.

Additional structural candidates were located in the larger source audit:

- A numeric-grid generator and spiral order accompanied by the explicit warning that the rune prose remains unsolved.
- A phase-channel decomposition of the black stream with reported counts `45, 28, 30, 37` and a stated corpus rarity check.
- E161-E165 red-rune grouping, five quartets, black-stream widths `75|4|28|3|23|6`, and a `16 × 109` payload relation. The same report states that it found no operation selector, plaintext, key, address, wallet, or terminal object.

## Page 72

| Artifact | Internal decision | Initial public triage | Boundary |
|---|---|---|---|
| E943 | Terminal three-role instruction locally promoted | Local-promotion candidate | Structural/state-role result; artifact says no plaintext, key, locator, or endpoint recovered |
| E944 | Base-29 operation-address vector locally promoted | Local-promotion candidate | Address-vector result; artifact says no plaintext, key, locator, or endpoint recovered |
| E946 | 274-rune payload segmentation locally promoted | Local-promotion candidate | Control-removal and dimension result; artifact says no plaintext, key, locator, or endpoint recovered |
| E1297 | Bounded feedback family rejected | Negative candidate | Reported order p=0.4420 and label p=0.4830 |
| E1298 | Structural transposition rejected | Negative candidate | Reported order p=0.0500 and label p=0.0260; rejection rationale requires reproduction review |
| E1322 | Repeated group-9 phase checksum locally promoted post-discovery | Post-discovery candidate | Aggregate checksum only; explicitly not rune order or plaintext |

Initial finding: the reviewed Page 72 artifacts make bounded structural, routing, segmentation, and checksum claims. They explicitly do not claim recovered plaintext. This does not rule out stronger Page 72 evidence elsewhere; it defines what these artifacts establish.

The larger structured-record scan found no explicit `plaintext_recovered: true` or `plaintext_claimed: true` entry. A displayed token such as `CX DJU BEI` is therefore being triaged as a typed descriptor or structural object, not promoted as translated prose.

## Page 73

| Artifact | Internal decision | Initial public triage | Boundary |
|---|---|---|---|
| Known Page 73 plaintext | Independently solved material | Known control | Provenance and canonical transcription still need public packaging |
| E402 | Diagnostic language probe | Experimental/diagnostic | Candidate fragments were not to be promoted without control separation and validator agreement |
| E952 | Emitted-77 terminal check locally promoted | Local-promotion candidate against known control | Links a selector to the known control; does not recover the SHA-512 preimage or identify the referenced page |
| E159 | Prime/totient replay | Known-control candidate | Reports reproduction of already-known terminal plaintext and rank 1 among six operators; provenance and clean replay still required |
| E256-E260 / E258 | Visible-hash operation selector | Correction/retraction | Later analysis says the printed hash does not establish selection of prime/totient and the initializer source was not locally recovered |

Initial finding: terminal plaintext is used in later HMS packages as a known control. The reviewed HMS artifacts replay or link to that control; they do not establish a new translation of the page. An archive-level report disputes whether the terminal-page text was verified in the primary material it reviewed, so corpus provenance and numbering must be resolved before public packaging.

## Cross-page positive controls

| Artifact | Reported result | Initial public triage | Boundary |
|---|---|---|---|
| E143-E145 | Held-out recovery of 5/5 F decisions and 319/319 GP tokens; second pair 25/25 and 515/515; correct key rank 1 | Positive-control candidate | Uses already-solved LP1 material; validates a declared implementation path, not an LP2 solve |
| E156-E160 | `$` segment cipher homogeneity and rare source-boundary result on solved material | Structural-control candidate | Requires canonical inputs, exact family disclosure, and clean replay |
| E156-E160 Page 74 | Direct GP reproduction of known terminal parable | Positive-control candidate | Known text; provenance and page numbering require reconciliation |

## Required next audit actions

1. Locate the canonical input and transcription version used by each artifact.
2. Verify every referenced source hash from a normalized public manifest.
3. Re-run the selected experiment from a clean environment.
4. Reconstruct the full tested family, including discarded and failed branches.
5. Confirm that the claimed control family matches the search process actually used.
6. Separate pre-registered relationships from post-discovery observations.
7. Package negative results with the exact scope of rejection.
8. Promote only the smallest claim supported by the reproduction.

See the [full source audit](SOURCE_AUDIT_2026-08-12.md) and [release candidate queue](RELEASE_CANDIDATE_QUEUE.md).
