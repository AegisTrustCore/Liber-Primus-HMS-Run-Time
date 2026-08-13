# RUN-0005 — Page 32 spiral-turn versus payload-page-boundary holdout

Four of six spiral turns overlapped the six boundary-containing blocks, but the exact upper-tail p-value was 0.091908092 and failed the frozen 0.01 threshold.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0005.zip)

## Reproduce

```text
scripts/reproduce_rset_0002.py
```

## Limits

- This rejects only the exact positionwise definition and threshold.
- The full rune transcription and forward next-slice instructions are excluded from the public package.
