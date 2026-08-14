# RUN-0010 — Solved-LP1 dollar-segment operation-frame audit

The seven source dollar segments are operation-homogeneous, and their six boundaries exactly equal the six known operation-change gaps across the fifteen rune-bearing solved LP1 pages.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0010.zip)

## Reproduce

```text
python research/runs/RUN-0010/evidence/verify_e156.py
```

## Limits

- This is a structural known-control observation on solved LP1, not a new plaintext recovery.
- The public package verifies the retained normalized ledger; it does not redistribute the complete third-party LP1 transcription or source imagery.
- The result identifies where known operations change, not which unknown operation applies to an LP2 segment.
- Transfer of the frame model from LP1 to unsolved LP2 requires separate tests.
