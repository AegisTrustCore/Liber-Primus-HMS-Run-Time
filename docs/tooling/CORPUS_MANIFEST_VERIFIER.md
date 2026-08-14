# HMS Corpus Manifest Verifier

Status: **RELEASE CANDIDATE `0.1.0-rc.1` — NOT AN APPROVED PUBLIC RELEASE**

## What it is

The verifier checks a locally held corpus against a declared JSON inventory. It reports path-safety failures, matching files, altered files, missing files, and—when strict mode is selected—extra files. It is offline and read-only.

The RC is bound to the [canonical 75-page LP image manifest](../../corpus/liber-primus/manifests/LP-75-IMAGES-v1.0.0.json) without redistributing page images.

## Download

There is no public download yet. The exact Windows candidate is retained only as a short-lived CI review artifact until clean-environment human UAT and release approval are complete. A public release must link one immutable, checksum-identified package.

## Quick start

1. Verify the published ZIP checksum before extraction.
2. Extract the complete ZIP to a new folder.
3. Double-click `HMS-Corpus-Verifier.exe`.
4. Keep the preselected canonical manifest, then choose the folder containing exactly `00.jpg` through `74.jpg`.
5. Leave strict mode enabled and select **Verify corpus**.
6. Save the JSON report when a durable verification record is needed.

Power users may run:

```text
HMS-Corpus-Verifier-CLI.exe canonical-info
HMS-Corpus-Verifier-CLI.exe verify canonical/LP-75-IMAGES-v1.0.0.json PATH_TO_PAGES --strict --output verification.json
```

## Supported systems

The packaged RC targets 64-bit Windows. It requires no Python installation. Developer-source operation uses CPython 3.12.

## Examples

The package contains invented `GOOD`, `ALTERED`, `MISSING`, `EXTRA`, and `TRAVERSAL` cases. Run all five without LP files:

```text
HMS-Corpus-Verifier-CLI.exe demo-self-test
```

Expected behavior: GOOD passes; ALTERED reports a mismatch; MISSING reports a missing file; EXTRA fails in strict mode; TRAVERSAL is rejected before filesystem verification.

## Output

The portable `HMS_CORPUS_VERIFICATION_V1` JSON report records the manifest identity, verification status, summary counts, and per-file findings. It deliberately excludes the selected local root path. This report is the safe handoff to the future HMS Runtime.

## Limitations

- A matching hash establishes byte identity only.
- The tool does not establish historical authenticity, redistribution rights, transcription correctness, steganographic meaning, or a Liber Primus solution.
- The canonical manifest identifies one declared HMS working set; it does not distribute that set.
- This RC is not customer-approved until the remaining release gate is signed.

## Verify the verifier

Run both executable self-tests and check every member against `SHA256SUMS`:

```text
HMS-Corpus-Verifier-CLI.exe demo-self-test
HMS-Corpus-Verifier.exe --self-test
```

The release page must publish the ZIP SHA-256, qualification record, environment record, and release-gate decision for the exact approved package.

## Developer setup

```text
python scripts/corpus_manifest.py canonical-info
python scripts/corpus_manifest.py demo-self-test
python scripts/corpus_verifier_app.py --self-test
python scripts/build_corpus_verifier_windows.py
python -m unittest tests.test_corpus_manifest tests.test_corpus_package -v
```

Manifest creation records sorted relative POSIX paths, SHA-256 digests, byte counts, and declared roles. Unsafe or duplicate paths and unsorted manifests are rejected.

## Changelog

- `0.1.0-rc.1`: bound the canonical 75-page manifest; added canonical identity inspection; promoted Windows GUI/CLI packaging and five-case qualification to release-candidate status.
- `0.1.0-dev`: initial deterministic core, GUI/CLI, report contract, packaging, and synthetic controls.
