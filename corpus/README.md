# Corpus Verification

The [complete Liber Primus corpus guide](liber-primus/README.md) now registers all 75 pages in the HMS working set and provides a start path, timeline, page-by-page ledger index, and carrier-verification procedure.

This directory holds public provenance, ordering, transcription-version, metadata, and hash manifests.

Source images or third-party transcriptions must not be committed until redistribution rights are clear. Where necessary, HMS will publish hashes, source references, and local import instructions instead.

HMS treats the source image, canonical transcription, alternative transcription, and user transcription as separate immutable, versioned objects. A corrected transcription receives a new ID and hash; historic experiments continue to reference the exact transcription version they used. See [OBJECT_MODEL.md](../OBJECT_MODEL.md).

## Current coverage

- Page identities registered: **75 of 75**
- LP1/earlier segment: pages `00`-`16` (**17** pages)
- LP2 segment: pages `17`-`74` (**58** pages)
- Source image bytes redistributed here: **no**, pending rights clearance

Corpus navigation status: **PUBLIC**

Verifier status: **INTERNAL TESTING**

The deterministic verifier core, CLI, desktop interface, JSON report contract, and Windows portable development build now exist. No canonical Liber Primus corpus manifest or customer release has been approved yet.

See [Corpus Manifest Verifier](../docs/tooling/CORPUS_MANIFEST_VERIFIER.md).
