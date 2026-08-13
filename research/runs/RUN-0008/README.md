# RUN-0008 — Corpus-wide default-key OutGuess calibration

Only the ten known LP1 positive controls separated. No tested LP2 page produced a non-attractor header, familywise anomaly, or detector-positive extraction under the frozen default-key OutGuess path.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0008.zip)

## Reproduce

```text
python research/runs/RUN-0008/evidence/verify_e1059.py
```

## Limits

- This closes only OutGuess 0.13 with its default-key path on the declared canonical carriers; it does not close other keys, carrier variants, tools, or steganography generally.
- The normalized package distributes carrier identities, hashes, complete ledgers, controls, and source, but not the 75 JPEG files or large coefficient bitmaps.
- The portable verifier reproduces the ledger checks and conclusion; full coefficient extraction therefore remains outside this package and the reproduction status is PARTIAL.
- The result recovers no LP2 plaintext, key, locator, endpoint, or Page 73 preimage.
