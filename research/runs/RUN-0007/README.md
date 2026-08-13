# RUN-0007 — Page 32 red-edge terminal holdout eligibility audit

All six candidate terminal endpoints were ineligible because they were already used, lacked a predeclared decoder, or were not predicted by the frozen grammar.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0007.zip)

## Reproduce

```text
scripts/reproduce_rset_0002.py
```

## Limits

- This eligibility audit does not independently test the underlying retrospective concordance.
- The forward next-slice instruction is excluded from the public package.
