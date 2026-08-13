# RUN-0001 — Clean replay of the historical Cicada 3301 OpenPGP artifact verification

The public verifier reproduced the recorded SHA-256 identity and both recorded OpenPGP fingerprints for the bundled historical key artifact.

- [Readable result](result.html)
- [Plain text](result.txt)
- [Canonical manifest](manifest.json)
- [Structured result](result.json)
- [Metrics](output/metrics.csv)
- [Provenance](provenance/provenance.json)
- [Download package](RUN-0001.zip)

## Reproduce

```text
python scripts/verify_cicada_key.py
```

## Limits

- This is an artifact-identity reproduction, not a Liber Primus plaintext result.
- A public-key fingerprint does not prove possession of the private key or present-day authority.
- The intake history before the bundled bytes remains bounded by OBS-0001.
