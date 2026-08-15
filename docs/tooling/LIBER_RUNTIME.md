# Liber Runtime — v1 contract

Status: **RELEASE CANDIDATE — local Runtime Environment `1.0.0-rc.1` implemented**

Runtime v1 is the persistent local research environment inside HMS Endeavour. It completes the Atlas/Workbench/history foundation without claiming to be an automatic Liber Primus solver.

## Implemented v1 surface

- Canonical 75-page identity manifest and privately configured corpus root.
- Page selection, local carrier opening, Bookmarks, Page Sets, and normalized Regions.
- Reusable immutable Notes, Rune Selections, Evidence, and Claims.
- Versioned jobs for GP29, corpus-report validation, bounded GP29 experiments, and structural Result comparison.
- Immutable Run and Result envelopes with provenance, visibility, evidence labels, limitations, and canonical hashes.
- Local history, explicit export, integrity audit, index rebuild, and metadata-only backup.
- CLI parity for projects, calculations, corpus verification, experiments, research objects, comparison, audit, backup, and corpus settings.
- Private-by-default operation with no telemetry, account, hosted synchronization, Vault access, or silent export.

Canonical contracts include `schemas/runtime-job.schema.json`, `schemas/runtime-result.schema.json`, `schemas/hms-project.schema.json`, `schemas/project-settings.schema.json`, `schemas/research-object.schema.json`, and `schemas/result-envelope.schema.json`.

## Explicitly deferred

Auto Explore, candidate decryption, broad transform families, automated ranking, solver claims, network sockets/API, entitlements, plugins, contextual AEGIS, hosted compute, and Admiral workflows remain separate reviewed releases. Tier access never changes an evidence label or bypasses provenance controls.

## Release gate

`1.0.0-rc.1` is code-complete for the bounded v1 surface but not approved for public distribution until the deterministic Windows artifact passes clean-environment qualification and human UAT and is approved by exact SHA-256.
