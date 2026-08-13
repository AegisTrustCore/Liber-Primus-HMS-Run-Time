# Liber Runtime Slice E1059 — Corpus-Wide OutGuess Calibration and LP2 Retraction

**Date:** 2026-07-31  
**Status:** FROZEN COMPLETE  
**Decision:** **No LP2 page remains an active OutGuess lead.**

## 1. Question

E1059 ran the exact E1058 coefficient extractor and default-key OutGuess 0.13 retrieval path across all **75 canonical Liber Primus pages**. It tested whether any LP2 page produces a genuine, complete, independently reproducible extraction that separates from the repeated false-header distribution.

## 2. Corpus and reproducibility

- 75/75 canonical pages were processed: LP1 pages 00–16 and LP2 pages 17–74.
- The seven E1058 overlap carriers (08, 17, 18, 20, 21, 22, 43) matched their frozen SHA-256 values byte-for-byte.
- A clean-room Python retrieval implementation independently reproduced every header, seed, declared length, recovered length, terminal offset, raw-body hash, and decoded-output hash: **75/75 matches; 0 mismatches**.
- The coefficient-metadata extractor reproduced the frozen bitmap exactly on all 75 pages while adding page-specific parity strata.

## 3. Header-family classification

The corpus contains **11 raw header values**, but one family dominates:

- `FFFFFFFF`: **65/75 pages**
- Decodes under the frozen default-key path to seed **41,408** and length **58,152 bytes**.
- All remaining ten headers are singletons, and all ten occur on historically positive LP1 carriers: pages 00, 01, 02, 03, 04, 08, 10, 11, 12, and 13.

This is decisive calibration evidence: `FFFFFFFF` is not a page-specific payload header. It is the coefficient-selection attractor produced by ordinary carriers under this exact default-key path.

## 4. Partial versus complete threshold

Within the 65-page `FFFFFFFF` family:

- **19** extractions happen to reach the declared 58,152-byte length.
- **46** are partial.
- **41/46 partials stop at 58,151 bytes**, exactly one byte short.
- The 19 “complete” cases terminate with only **35–74 usable coefficient bits** remaining.

Therefore, completeness is controlled by the final capacity boundary. It does not convert the repeated header into evidence of an embedded object.

Three LP1 pages (06, 07, 09) also produce complete `FFFFFFFF` artifacts, proving that this false-completion behavior is not unique to LP2.

## 5. Positive-control and held-out validation

Page 08 was held out from detector construction. The final detector accepted a page when extraction was complete and either its header was not the dominant `FFFFFFFF` attractor or it showed a familywise matched-null anomaly.

| Page | Raw header | Declared bytes | Printable fraction | Minimum familywise p | Detector |
|---:|---|---:|---:|---:|---|
| 00 | `9c5e8417` | 2,899 | 1.000 | 0.0274658 | PASS |
| 01 | `4c5e8417` | 2,899 | 1.000 | 0.0274658 | PASS |
| 02 | `615e8417` | 2,899 | 1.000 | 0.0274658 | PASS |
| 03 | `405e9660` | 31,809 | 1.000 | 0.0274658 | PASS |
| 04 | `ddcbb301` | 7,524 | 0.386 | 1 | PASS |
| 08 | `195e5b1c` | 140 | 1.000 | 0.0274658 | PASS |
| 10 | `5c5e0518` | 1,234 | 1.000 | 0.0274658 | PASS |
| 11 | `995e0518` | 1,234 | 1.000 | 0.0274658 | PASS |
| 12 | `a95e0518` | 1,234 | 1.000 | 0.0274658 | PASS |
| 13 | `be5e0518` | 1,234 | 1.000 | 0.0274658 | PASS |

Results:

- **10/10** historically positive LP1 carriers were recognized as complete non-attractor extractions.
- The held-out Page 08 control passed with familywise **p = 0.027466**.
- All six frozen false controls (17, 18, 20, 21, 22, 43) were rejected.
- Page 04 is a known high-entropy binary output. Its body does not trigger the generic printable/PGP statistics, but its complete singleton header remains a genuine non-attractor control.

## 6. Page-specific matched nulls

Each page received **8,191** exact conditional randomizations. Parity was permuted without replacement inside:

`component × DCT index × 3×3 page region × adjacent-magnitude-pair bin`

This preserves the page's coefficient/magnitude composition while destroying the exact selected parity order used by retrieval. Three statistics were predeclared: header zero count, first-64-byte printable count, and PGP-armored prefix. Bonferroni correction covered **75 pages × 3 statistics = 225 tests**.

- Textual positive controls and held-out Page 08 reached the minimum attainable empirical tail and remained significant after correction: familywise **p = 0.027466**.
- **Every LP2 page had minimum familywise p = 1.0.**
- No LP2 body, header, or signature separated from its own matched null.

## 7. Coefficient-parity evidence

Corpus-level parity summaries differ between known positive carriers and LP2:

- Global odd fraction: known-positive median **0.581386**, LP2 median **0.621912**, Mann–Whitney two-sided **p = 1.97e-05**.
- Stratified parity statistic: known-positive median **1059.543**, LP2 median **1769.688**, **p = 0.00025**.

These aggregate differences support intentional coefficient manipulation in the known-positive control population, but they are not a standalone detector: Page 08's global odd fraction overlaps LP2. Exact header/order recovery and page-specific matched nulls are the stronger evidence.

## 8. LP2 complete-attractor cases

| Page | Capacity margin (bits) | Minimum familywise p | Classification |
|---:|---:|---:|---|
| 17 | 38 | 1 | rejected: FFFFFFFF attractor |
| 21 | 59 | 1 | rejected: FFFFFFFF attractor |
| 43 | 53 | 1 | rejected: FFFFFFFF attractor |
| 57 | 55 | 1 | rejected: FFFFFFFF attractor |
| 58 | 72 | 1 | rejected: FFFFFFFF attractor |
| 59 | 74 | 1 | rejected: FFFFFFFF attractor |
| 60 | 72 | 1 | rejected: FFFFFFFF attractor |
| 61 | 55 | 1 | rejected: FFFFFFFF attractor |
| 62 | 73 | 1 | rejected: FFFFFFFF attractor |
| 63 | 70 | 1 | rejected: FFFFFFFF attractor |
| 64 | 72 | 1 | rejected: FFFFFFFF attractor |
| 65 | 59 | 1 | rejected: FFFFFFFF attractor |
| 68 | 53 | 1 | rejected: FFFFFFFF attractor |
| 69 | 55 | 1 | rejected: FFFFFFFF attractor |
| 70 | 55 | 1 | rejected: FFFFFFFF attractor |
| 71 | 71 | 1 | rejected: FFFFFFFF attractor |

All 16 are capacity-threshold completions of the same repeated attractor. None is a structured extraction.

## 9. Frozen conclusion

E1059 satisfies the retraction condition established in E1058:

> Only known LP1 positive carriers separate. All LP2 pages remain inside the repeated false-header/null distribution.

Accordingly:

1. **Active LP2 OutGuess leads: none.**
2. **Default-key OutGuess extraction is removed from the active LP2 key-channel hypothesis set.**
3. The extractor remains useful only as a regression control and as a test that future page files are the same canonical JPEG carriers.
4. Page 43 is closed as an OutGuess lead; its complete 58,152-byte object is a capacity-bound `FFFFFFFF` artifact, not an extracted payload.

## 10. Guardrails

- This result closes the frozen **default-key OutGuess 0.13 path** on the canonical carriers. It does not prove that no conceivable steganographic scheme exists.
- No alternative keys, recompressions, crops, rotations, or post-hoc decoding rules were introduced.
- LP2 pages were excluded from detector tuning; Page 08 was held out for transfer validation.
