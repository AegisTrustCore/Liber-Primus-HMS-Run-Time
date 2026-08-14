# RUN-0011 — Terminal segment-wide operation known controls

The six-operation family selected the established sequential-prime/totient operator for Page 73 and direct GP for Page 74; both known controls beat 500 full-family shuffles.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0011.zip)

## Reproduce

```text
python research/runs/RUN-0011/evidence/verify_e159_controls.py
```

## Limits

- Both plaintexts and their operations were already known; this is a positive control, not a new translation.
- The public package retains the complete terminal-control ledger but not the private typed event streams needed to rerun transformation from source glyphs, so reproduction is PARTIAL.
- Success on two terminal controls does not prove that every LP2 segment uses one of the six operations.
- This package does not publish the unsolved-segment best-output ledger or forward selector experiments.
