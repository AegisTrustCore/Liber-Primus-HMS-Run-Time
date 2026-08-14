# RUN-0009 — Page 05 complete-board to Page 33 bounded route-family test

All three calibrated GP language models rejected the declared 640-route direct-board family: the selected route failed half-transfer, solved-reference, and familywise permutation gates.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0009.zip)

## Reproduce

```text
python research/runs/RUN-0009/evidence/verify_e1477.py
```

## Limits

- The original transient E1459 qscore dependency did not survive; the completion uses three disclosed replacement models calibrated on solved LP1 text.
- The public package does not redistribute third-party corpus transcriptions, so its portable verifier audits the complete retained decision ledgers while the full route replay requires separately acquired inputs.
- This does not reject every possible Page 05 to Page 33 relationship, alternate board-derived object, transform, key, or execution model.
- No LP2 plaintext, key, wallet, address, onion locator, endpoint, or Page 73 preimage was recovered.
