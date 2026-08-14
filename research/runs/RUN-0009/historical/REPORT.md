# E1477 — Page05 complete board → Page33

**Date:** 2026-08-03  
**Decision:** `PAGE05_BOARD_TO_PAGE33_REJECTED_ROBUST`

## Frozen question

Does the complete, source-authenticated Page05 5×5 GP-prime board act directly on physical Page33 as:

- a periodic key in its D4/readout/register forms; or
- a 25-column transposition schedule?

The restored family contains **640 observed routes** over the exact **267-rune** Page33 stream. It retains raw and lossless transition-29 data, add/subtract/Beaufort operations, continuous and word-reset scopes, optional cipher-F freezing, ascending/descending columnar routes, and the two 1033 scalar controls.

## Dependency boundary

The original E1477 source survived, but its transient imported scorer `lp_e1459_key_payload_crypto_seed.py` did not survive in the Library. Therefore this completion does **not** claim byte-for-byte identity with the vanished E1459 score.

To make the decision falsifiable rather than guessed, the exact E1477 route family was run under three independently calibrated GP language models:

- bigram;
- trigram;
- tetragram.

Each model was trained only on solved LP1 plaintext. Each recovered the planted E1477 route exactly at rank 1 before touching Page33.

## Results

| GP scorer | Calibration | Best score | Solved reference | Same route on both halves? | 999-board control p | Promoted? |
|---|---:|---:|---:|---:|---:|---:|
| 2-gram | exact, rank 1 | -8.080138 | -5.527132 | No | 0.060 | No |
| 3-gram | exact, rank 1 | -10.895217 | -7.367255 | No | 0.827 | No |
| 4-gram | exact, rank 1 | -13.500516 | -10.177486 | No | 1.000 | No |

Primary tetragram best route:

```text
{"family": "periodic", "key": "rot0/mod29/row", "data": "raw", "operation": "sub", "scope": "word", "freeze_on_cipher_F": false}
```

Its GP display prefix is:

```text
WUTHIIXORIAAEJSEOINGUEOPOTGHEOABEOINGTPHAMMLJRRTHCNAIXOEERIGBTHIXCJCIDCIEITGINGPCSOEAEAEOCENWSMMCYPNFWYPOFTHXPLHFTHDIAINGFUAFWPTPEOOGWCGOTHINGELFYGIA
```

This is not stable plaintext.

## Why the lane is closed

E1477 requires all four gates:

1. planted-route recovery;
2. identical independently selected route on both Page33 halves;
3. familywise board-permutation `p <= .01`;
4. observed score at least as high as solved text.

Only the calibration gate passes. The half-transfer gate fails under all three scorers. The solved-reference gate fails by a large margin under all three. The empirical tails are `.060`, `.827`, and `1.000`, so the control gate also fails.

## Interpretation

The Page05 square remains an exact, authored word→GP-prime→number object with magic constant 1033. This experiment rejects only the direct use of its complete numeric board as a Page33 periodic key or 25-column permutation.

The surviving possibilities are narrower:

- Page05 is an **address or selector**, not the key material;
- its **13 half-turn orbits**, center, or lexical equivalence classes are the operative object;
- Page05 supplies a **checksum/construction rule** whose second input lies elsewhere;
- Page33 remains ciphertext/compressed data requiring a separately authenticated key.

No LP2 plaintext, key, wallet/address, onion locator, Page73 preimage, or authenticated terminal object was recovered.
