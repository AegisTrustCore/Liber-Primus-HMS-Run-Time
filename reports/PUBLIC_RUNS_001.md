# Public Reproduction Runs 001 — Legacy Presentation

This Markdown page is retained as the original presentation layer. The canonical research objects now live in [`RSET-0001`](../research/runsets/RSET-0001/README.md). They contain no candidate LP plaintext, active route, parameter family, private path, or paid-tier research packet.

## RUN-0001 — OpenPGP artifact replay

Run:

```bash
python scripts/verify_cicada_key.py
```

Expected output:

```text
PASS — SHA-256 and 2 OpenPGP fingerprint(s) match the manifest.
```

This reproduces the byte and fingerprint claim in `OBS-0001`. It does not authenticate a message or establish current Cicada authority.

## RUN-0002 — Expedition verifier synthetic tests

Run:

```bash
python -m unittest discover -s tests -v
```

Expected result: five tests pass, covering normalization, acceptance, rejection, empty input, and an unknown challenge ID.

The tests use a synthetic manifest and do not contain the sealed XPD-0001 answer. Desktop packaging and private sealed-answer acceptance remain separate gates.

## Structured packages

- [RUN-0001](../research/runs/RUN-0001/README.md)
- [RUN-0002](../research/runs/RUN-0002/README.md)
- [RES-0001](../research/results/RES-0001/README.md)
- [RES-0002](../research/results/RES-0002/README.md)
- [RSET-0001 staged bundle](../research/runsets/RSET-0001/README.md)
- [Environment ENV-0002](../releases/environments/ENV-0002.json)
