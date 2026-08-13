# Corpus Verification

This directory will hold public provenance, ordering, transcription-version, metadata, and hash manifests.

Source images or third-party transcriptions must not be committed until redistribution rights are clear. Where necessary, HMS will publish hashes, source references, and local import instructions instead.

HMS treats the source image, canonical transcription, alternative transcription, and user transcription as separate immutable, versioned objects. A corrected transcription receives a new ID and hash; historic experiments continue to reference the exact transcription version they used. See [OBJECT_MODEL.md](../OBJECT_MODEL.md).

Status: **INTERNAL TESTING**

The deterministic verifier core, CLI, desktop interface, JSON report contract, and Windows portable development build now exist. No canonical Liber Primus corpus manifest or customer release has been approved yet.

See [Corpus Manifest Verifier](../docs/tooling/CORPUS_MANIFEST_VERIFIER.md).
