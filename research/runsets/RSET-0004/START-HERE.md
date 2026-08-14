# RSET-0004 — Start Here

## What this release adds

This package adds three small, inspectable pieces of the HMS research record. It deliberately mixes one closed route with two controls so readers can see how negative, structural, and positive evidence differ.

| Object | Plain-language result | Evidence state |
|---|---|---|
| [RUN-0009 / RES-0009](../../runs/RUN-0009/README.md) | The complete Page 05 board did not work as a direct Page 33 key or 25-column permutation in the declared 640-route family. | Bounded negative |
| [RUN-0010 / RES-0010](../../runs/RUN-0010/README.md) | On solved LP1, the seven `$` segments align exactly with known operation frames. | Structural control |
| [RUN-0011 / RES-0011](../../runs/RUN-0011/README.md) | The segment-wide runtime selects the established Page 73 and Page 74 operators when those controls are present. | Known control |

## What to read first

1. Read each Result for the smallest supported claim.
2. Open its supporting Run for parameters, controls, limitations, and provenance.
3. Run the included verifier with CPython 3.12; it modifies no evidence files and requires no network access.
4. Use `SHA256SUMS` inside each package to check the distributed files.

## The important boundary

This release publishes **no newly recovered Liber Primus plaintext**.

- Page 73 and Page 74 are already-established public plaintext controls.
- E1477 closes only the declared complete-board direct-use family.
- E156 supports operation scope on solved LP1; it does not reveal the LP2 operation selector.
- Unsolved best outputs, exploratory modulus signals, active selector routes, and forward experiment queues are not included.

## Why reproduction is marked partial

The original packages depend on corpus transcriptions and typed event streams that are not redistributed here. The public verifiers reproduce the retained ledger logic, cross-file agreement, combinatorial controls, empirical-p arithmetic, and final bounded decisions. Full transformation from source glyphs requires separately acquired inputs with the recorded identities.

## Next admissible step

Use these objects as regression tests for the future Runtime. A new unsolved-segment candidate may be promoted only after its selector and operation are declared without using the candidate output to choose them.
