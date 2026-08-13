# Start Here — RSET-0002

Five signals were examined. Four routes closed under their declared tests; one route never reached an eligible test. This release does **not** claim a new Liber Primus translation.

> **A pattern is not a message. A closed route is not a closed book. Verify before following the signal.**

## The signal in one minute

| Record | Simple result | Evidence level | Can you check it? |
|---|---|---|---|
| `RUN-0003` / `RES-0003` | The historical system could not obtain the exact Common Crawl response bytes needed for the test. | Acquisition boundary | Historical record only |
| `RUN-0004` / `RES-0004` | Reversing the final rune blocks did not pass the preserved scoring test. | Bounded negative | Partly; the ledger is public, but the original model code is missing |
| `RUN-0005` / `RES-0005` | Spiral turns did not align strongly enough with page boundaries under the exact frozen test. | Bounded negative | Yes |
| `RUN-0006` / `RES-0006` | The signed-gap vector matched none of the 15 payload-junction positions. | Bounded negative | Yes |
| `RUN-0007` / `RES-0007` | None of six terminal holdouts were eligible for a new preregistered test. | Correction | Yes |

## Result 1 — The archive route was not actually tested

**Question:** Could exact 2015 Common Crawl response bodies be retrieved and hashed?

**What happened:** The historical environment never obtained the required CDX result and exact WARC byte range. Zero response bodies entered the hash test.

**Result:** `ACQUISITION BLOCKED`

**This proves:** The archived workflow stopped at acquisition.

**This does not prove:** That Common Crawl contains no useful capture.

**Next:** Reconstruct a provenance-safe archive acquisition environment before making a content claim.

## Result 2 — Block reversal was rejected

**Question:** Did negative displacement mean “reverse the final two rune blocks” under the frozen scoring model?

**What happened:** The reversed interpretation failed its declared comparison.

**Result:** `BOUNDED NEGATIVE`

**This proves:** That exact block-reversal interpretation did not pass.

**This does not prove:** That every possible meaning of sign or displacement is wrong.

**Next:** Recover or independently reconstruct the original scoring implementation. Until then, this record remains partially reproducible.

## Result 3 — Spiral turns did not clear the threshold

**Question:** Did exact spiral-turn positions align with page boundaries strongly enough under the frozen test?

**What happened:** The exact hypergeometric probability was `0.0919080919`, which did not clear the declared threshold.

**Result:** `BOUNDED NEGATIVE`

**This proves:** The exact frozen correspondence was not strong enough.

**This does not prove:** That every spiral construction or shifted definition fails.

**Next:** Treat altered turn definitions as new experiments, declared before scoring.

## Result 4 — The two vectors did not match

**Question:** Did the signed prime-gap vector directly encode the 15 payload-junction residues?

**What happened:** `0 of 15` positions matched. Under the frozen binomial calculation, the upper-tail probability is `1`.

**Result:** `BOUNDED NEGATIVE`

**This proves:** The exact position-for-position mapping failed.

**This does not prove:** That every transform, ordering, or related gap construction fails.

**Next:** Any transform must be declared as a separate test before looking at its score.

## Result 5 — The terminal holdout was ineligible

**Question:** Was any unused terminal feature available for a clean holdout test?

**What happened:** `0 of 6` candidates met the eligibility rules.

**Result:** `CORRECTION / ANTI-POST-HOC BOUNDARY`

**This proves:** The earlier retrospective observation cannot be upgraded through these terminal candidates.

**This does not prove:** That the earlier observation is independently false; it remains retrospective.

**Next:** Use a genuinely new, source-authorized feature or leave the claim at retrospective status.

## Three signals for reading the evidence

**Signal 1 — Find the boundary.** Look for `This does not prove` before interpreting a result. The boundary is part of the evidence.

**Signal 2 — Test the echo.** `REPRODUCED`, `PARTIAL`, and `HISTORICAL_ONLY` describe how much of the transmission another researcher can replay.

**Signal 3 — Follow the chain.** A `RUN` records execution, a `RES` states the supported conclusion, and `CAP-0002` groups the investigation. If the chain breaks, stop there.

## The next transmission

1. Collect independent reproductions of `RUN-0005` through `RUN-0007`.
2. Reconstruct missing environment or implementation details for `RUN-0003` and `RUN-0004`.
3. Process the remaining archive inventory one ZIP at a time through the same disclosure review.
4. Publish additional bounded evidence only after its inputs, method, controls, result, limitations, and checksums are complete.

## Downloads

- [Complete public run set](RSET-0002.zip)
- [Machine-readable distribution map](distribution.json)
- [Member-package hashes](downloads.json)
- [Plain-text release summary](RELEASE-NOTES.txt)

The original historical ZIPs are identified by hash but are not distributed because they combine evidence with a complete rune transcription and forward experimental instructions.
