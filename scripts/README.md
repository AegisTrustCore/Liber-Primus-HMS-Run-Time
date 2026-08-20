# Maintainer and application scripts

Run these entry points from the repository root. Customer downloads come from approved GitHub releases—not directly from this directory.

## Validate and audit

- `validate_records.py` — validate public manifests, records, releases, posts, and challenges
- `check_public_boundary.py` — reject workstation paths and local endpoints in public material
- `verify_cicada_key.py` — verify the preserved historical OpenPGP artifact
- `audit_lp_sources.py` — inventory declared Liber Primus sources
- `inventory_research_archives.py` — inspect private archive candidates without publishing them

## Public applications

- `gp29_app.py` — GP29 desktop application
- `corpus_manifest.py` and `corpus_verifier_app.py` — Corpus Manifest Verifier CLI and GUI
- `endeavour_lite.py` and `endeavour_lite_app.py` — Endeavour Lite CLI and GUI candidate
- `verify_challenge.py` and `verify_challenge_gui.py` — Expedition client interfaces

## Build and reproduce

- `build_*_windows.py` — deterministic Windows package builders
- `build_research_archive.py` — regenerate the public research archive
- `reproduce_rset_0002.py` — reproduce the public RSET-0002 ledgers
- `serve_expedition_verifier.py` — closed-state service development entry point

Consult [Public Releases](../PUBLIC_RELEASES.md) before treating any built artifact as distributable.

