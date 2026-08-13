# Public Reproduction Runs 001

This drop publishes two bounded, independently runnable proof records. It contains no candidate LP plaintext, active route, parameter family, private path, or paid-tier research packet.

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

## Records

- [RUN-0001](../research/records/RUN-0001.json)
- [RUN-0002](../research/records/RUN-0002.json)
- [Environment ENV-0002](../releases/environments/ENV-0002.json)
