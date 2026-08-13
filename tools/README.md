# Public Developer Utilities

Released as source in the historical `v0.1.0` foundation:

- [`scripts/validate_records.py`](../scripts/validate_records.py) enforces public research-record, dossier, instrument, release-state, metadata-only Patreon, environment-manifest, challenge, and release-gate invariants.
- [`scripts/audit_lp_sources.py`](../scripts/audit_lp_sources.py) creates a private hash-aware source inventory whose raw output must remain outside version control.
- [`scripts/verify_cicada_key.py`](../scripts/verify_cicada_key.py) verifies the bundled historical OpenPGP artifact and its recorded fingerprints.

These are `DEVELOPER_TOOL` source distributions. They require CPython and are not customer-ready applications. Their presence does not mean an ordinary user has a double-click tool, supported binary, installer, or web application.

The authoritative status and delivery reality of every acknowledged tool is maintained in the [instrument registry](../instruments/README.md). The [distribution standard](../docs/DISTRIBUTION_STANDARD.md) defines the gate between source availability and a usable customer release. A roadmap entry or Patreon benefit does not make a tool available.
