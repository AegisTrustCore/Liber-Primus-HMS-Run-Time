# Test suite

The test suite covers deterministic calculations, corpus verification, research packaging, project integrity, Expedition security contracts, service behavior, and public-record validation.

Run the complete suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

Then run the publication checks:

```powershell
python scripts/validate_records.py
python scripts/check_public_boundary.py
```

Passing tests do not approve a release or research claim. Human approval and the applicable immutable release gate remain mandatory.
