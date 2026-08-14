# HMS Corpus Manifest Verifier

Status: **INTERNAL TESTING — development package, not publicly released**

## What it is

The verifier creates canonical inventories for locally held corpus files and checks local bytes against those inventories. It allows HMS to publish identities and verification instructions without redistributing source images or third-party transcriptions.

## Developer use

```text
python scripts/corpus_manifest.py create CORPUS_ROOT --corpus-id LP-LOCAL --version 1 --output manifest.json
python scripts/corpus_manifest.py verify manifest.json CORPUS_ROOT --strict --output verification.json
```

Creation records sorted relative POSIX paths, SHA-256 digests, byte counts, and declared roles. Verification reports matches, mismatches, missing files, unsafe paths, and—under `--strict`—undeclared files.

## Desktop development build

```text
python scripts/corpus_verifier_app.py
python scripts/corpus_verifier_app.py --self-test
python scripts/build_corpus_verifier_windows.py
```

The Windows desktop interface selects a manifest and corpus root, runs strict or non-strict verification, displays the report, and exports JSON. It is offline and read-only.

## Synthetic customer demo

The package includes an invented five-case suite under `demo/corpus-verifier`:

- `GOOD` must pass with two verified files;
- `ALTERED` must report one mismatch;
- `MISSING` must report one missing file;
- `EXTRA` must report one undeclared file in strict mode;
- `TRAVERSAL` must reject an unsafe `../` manifest path before verification.

Run all five without LP material:

```text
python scripts/corpus_manifest.py demo-self-test
```

This closes the synthetic-control portion of the release-candidate gate. Version promotion, the canonical public LP manifest, clean-machine UAT, and exact-subject human approval remain pending.

## Security and privacy boundaries

- Relative paths cannot be absolute, contain backslashes, traverse with `..`, or resolve outside the chosen root.
- Inputs are read but never modified.
- No corpus bytes, filenames, reports, or local paths are uploaded.
- No private corpus manifest is committed automatically.
- A matching hash establishes byte identity only. It does not establish source authenticity, redistribution rights, transcription correctness, or a Liber Primus solution.

## Runtime handoff

The portable `HMS_CORPUS_VERIFICATION_V1` report is the safe Runtime handoff object. Hosted Runtime work should ingest an explicitly shared report, not crawl a member workstation or receive its local root path by default.
