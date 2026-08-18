# HMS Endeavour Runtime Environment v1

Audience: Observer for the local workstation foundation; advanced research content remains separately tiered.

Status: **RELEASE CANDIDATE — runnable `1.0.0-rc.1`, not publicly released**

The former Endeavour Lite development shell is now the bounded Runtime Environment v1 release candidate. It is one private, local-first desktop and CLI workstation with:

- a selectable 29-rune workbench and deterministic GP29 Results;
- canonical 75-page manifest verification without bundling page images;
- an embedded 75-page LP Atlas with page selection, fit/zoom, pan, previous/next navigation, and optional external opening of a privately linked local carrier;
- immutable Notes, Bookmarks, Regions, Page Sets, Rune Selections, Evidence, and Claims;
- bounded declared GP29 experiments and structural Result comparison;
- immutable Runs and Results with evidence labels, limitations, hashes, and explicit JSON export;
- project integrity audit, index recovery, and privacy-safe metadata backups;
- a fail-closed signed Expedition client that stores no submitted plaintext.

## Private project boundary

`project.json`, `settings.json`, `index.json`, `runs/`, `results/`, `objects/`, and `exports/` form the project. The local corpus root exists only in `settings.json`. Safe backups replace it with `null` and exclude corpus images and exports. Nothing is uploaded silently; this build has no account or telemetry service.

## Evidence boundary

GP29 is `CALCULATION_ONLY`, corpus verification is `PROVENANCE_ONLY`, declared experiments are `EXPERIMENTAL`, and Result comparisons are `STRUCTURAL`. A note or numerical match is never promoted automatically into a translation or solve claim.

## Release gate

Automated tests and packaged self-tests pass for the current source. The final candidate must now receive a deterministic Windows rebuild, extracted-package qualification, privacy inspection, Defender scan, human visual UAT, and exact-checksum owner approval. Expedition remains unavailable until its separately qualified HTTPS service and an approved `OPEN` campaign manifest exist.

Developer start:

```text
python scripts/endeavour_lite_app.py
python scripts/endeavour_lite_app.py --self-test
python scripts/endeavour_lite.py --help
python scripts/build_endeavour_lite_windows.py
```

Auto Explore, automatic solving, sockets, accounts, hosted synchronization, plugins, and contextual AEGIS are later increments, not hidden v1 features.
