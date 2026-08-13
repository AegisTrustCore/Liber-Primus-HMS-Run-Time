# Start here — E1059 default-key OutGuess closure

> The signal is not the shape that repeats. The signal is what survives the control.

## The short version

Earlier tests produced complete 58,152-byte outputs on several LP2 pages. Completion looked interesting, but E1059 tested whether those outputs behaved like intentional, page-specific embeddings.

They did not.

The same `FFFFFFFF` header appeared on 65 of 75 pages. Ten known LP1 positive carriers separated correctly. None of the 58 LP2 pages separated from its matched-null distribution. The complete LP2 cases occurred where the carrier happened to have enough remaining capacity to finish the repeated false-header request.

## What is closed

The exact OutGuess 0.13 **default-key** extraction path on the declared canonical page carriers is no longer an active LP2 lead.

## What remains open

This result says nothing final about:

- other keys;
- other carrier versions or transformations;
- other steganographic systems;
- independently frozen methods; or
- LP2 as a whole.

It is not a plaintext, translation, key, locator, endpoint, or Page 73 preimage.

## Follow the proof

1. Read [`RES-0008`](bundles/RES-0008.zip) for the bounded claim.
2. Read [`RUN-0008`](bundles/RUN-0008.zip) for inputs, parameters, controls, metrics, provenance, and all retained ledgers.
3. From the repository root, run:

   ```text
   python research/runs/RUN-0008/evidence/verify_e1059.py
   ```

   Expected result: 13 checks pass and 0 fail.

4. Verify package identity using `SHA256SUMS` and the hashes in `downloads.json`.

## Why reproduction is PARTIAL

The public package can reproduce the complete ledger audit and branch-closing decision. It cannot recreate coefficient extraction from pixels because the 75 JPEG carriers and large intermediate bitmaps are not redistributed in this package. Their identities and hashes remain recorded so a later carrier-authorized reproduction can close that gap.

## What comes next

The next admissible step is independent carrier-level reproduction against the exact manifest—not a search for English inside the rejected false bodies. E1477 is the next separate bounded-negative candidate after this package.
