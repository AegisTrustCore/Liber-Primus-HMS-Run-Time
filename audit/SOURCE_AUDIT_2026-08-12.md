# Liber Primus Source Audit — 2026-08-12

Status: **FIRST-PASS INVENTORY AND TEXT-RECORD AUDIT COMPLETE**

This report summarizes the complete supplied Personal Research tree, including the nested More research collection. It does not publish the raw inventory, private paths, credentials, or potentially identifying metadata.

## Coverage

| Measure | Count |
|---|---:|
| Files hashed and classified | 1,322 |
| Total bytes | 3,837,489,779 |
| Text files | 876 |
| ZIP archives | 266 |
| Images | 149 |
| Documents | 11 |
| Executables | 6 |
| Spreadsheets | 2 |
| ZIP members inventoried | 11,541 |
| Text members scanned | 5,918 |
| Structured claim fragments extracted | 1,141 |
| Explicit decision statements extracted | 115 |
| Duplicate-content groups | 43 |
| Duplicate file entries | 89 |

Every source file received a SHA-256 digest. ZIP contents were enumerated without executing code. Text-like files inside archives were scanned for experiment decisions, evidence boundaries, recovery flags, and page references.

## Claim-level findings

The most important negative control on interpretation is consistent across the structured records:

| Structured field | Explicit true | Explicit false |
|---|---:|---:|
| `plaintext_recovered` | 0 | 92 |
| `plaintext_claimed` | 0 | 9 |
| `plaintext_execution_authorized` | 0 | 11 |
| `key_material_recovered` | 0 | 19 |
| `locator_or_endpoint_recovered` | 0 | 6 |

Some records contain a generic field named `verified: true`. Inspection showed that these values refer to local checks, structural objects, matrices, or implementation conditions. A generic boolean is not treated as evidence of plaintext recovery or as public verification.

## Strongest publication candidates

### Known-control reproductions

- **E143-E145:** reports held-out recovery on already-solved LP1 material: 5/5 F decisions and 319/319 GP tokens for one held-out pair, plus 25/25 and 515/515 on another pair. The correct key reportedly ranked first. This can validate an implementation against known material; it is not a new LP2 solution.
- **E156-E160:** reports homogeneous cipher segmentation on solved LP1 material and replays already-known terminal plaintext for Pages 73 and 74. The Page 73 transform reportedly ranked first among six tested operators. These are control candidates pending provenance and clean reproduction.

### Page 32 structural candidates

- A numeric-grid generator and spiral ordering are documented while explicitly labeling the rune prose unsolved.
- A phase-channel decomposition reports counts of 45, 28, 30, and 37 and a rare width pattern in a stated corpus search.
- E161-E165 reports red-rune grouping, five quartets, black-stream widths `75|4|28|3|23|6`, and a `16 × 109` payload relationship, while explicitly reporting no operation selector, plaintext, key, address, wallet, or terminal object.

These observations may be reproducible and useful without being translations.

### Bounded negative results

Reviewed packages contain explicit failures when candidate rules are transferred to unsolved material, including Page 72 prime/totient output described as gibberish and several rejected routing, feedback, transposition, and checksum families. A negative record establishes only that its fully disclosed family failed its stated gate.

### Correction and retraction

An earlier branch interpreted a visible Page 73 hash object as selecting a prime/totient operation. A later package retracts that causal interpretation: the operation may reproduce known control text, but the visible object was not shown to select it and the initializer provenance was not locally recovered. The public record must preserve this correction.

## Contradictions requiring resolution

One archive-level decoded-pages report states that all referenced LP2 pages remained unsolved and that terminal-page solutions were not verified in the primary material it reviewed. Later experiment packages use terminal plaintext as a known control. This may reflect provenance, corpus-edition, or page-numbering differences; it must be resolved before those controls are published as canonical.

## Publication boundary

- No reviewed structured record explicitly reports recovered new plaintext, key material, locator, or endpoint.
- The audit does not claim the entire Liber Primus corpus has been solved.
- Raw archives, executables, private paths, and sensitive-name flags remain outside this repository.
- Binary/reference artifacts were hash-inventoried, but relevant PDFs, spreadsheets, images, and media still require targeted content review.
- A candidate becomes verified here only after canonical-input review, rights review, clean reproduction, controls, and public evidence packaging.

The generic audit tool is published at [`scripts/audit_lp_sources.py`](../scripts/audit_lp_sources.py). Its raw output is intentionally excluded from version control.
