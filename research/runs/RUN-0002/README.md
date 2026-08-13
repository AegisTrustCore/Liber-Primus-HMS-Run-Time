# RUN-0002 — Synthetic acceptance and rejection tests for the Expedition verifier core

Five frozen synthetic tests established the verifier core's normalization, acceptance, rejection, empty-input, and unknown-challenge behavior without disclosing the sealed Expedition answer.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0002.zip)

## Reproduce

```text
python -m unittest tests.test_challenge_verifier -v
```

## Limits

- Unit tests establish deterministic core behavior, not desktop usability.
- The sealed XPD-0001 acceptance test is performed privately against the packaged candidate.
- This is not Liber Primus source evidence or a plaintext claim.
