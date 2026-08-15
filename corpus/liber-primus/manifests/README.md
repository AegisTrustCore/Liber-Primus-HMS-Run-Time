# Canonical corpus manifests

`LP-75-IMAGES-v1.0.0.json` is the machine-readable identity manifest for the HMS 75-page Liber Primus working corpus. It declares exactly `00.jpg` through `74.jpg`, with each file's byte count, SHA-256 digest, and `CANONICAL_PAGE_IMAGE` role.

The manifest does not include or license the page images. A match establishes only that local bytes equal the carrier bytes used by the cited HMS work; it does not establish historical authenticity, copyright permission, transcription correctness, or a solve.

## Fixed identity

- Corpus ID: `LP-75-IMAGES`
- Corpus version: `1.0.0`
- Declared files: `75`
- Declared page bytes: `52,248,065`
- Canonical JSON SHA-256: `d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009`
- Manifest file SHA-256: `76d67e34f04b0125ad9b2893cd68b11510bb4e7e37ec2bb1849760e487a31978`

The source archive used for the binding was `pages.zip`, 42,309,414 bytes, SHA-256 `74f96108f98fb8a5ef2d5384d2dadcc8ba08fdd8113597a1da7eac9b0e4f7ec7`. Its 75 extracted page members matched the existing HMS working set byte-for-byte. This identifies the tested acquisition; it is not a redistribution endorsement.

## Verify a legally obtained local set

```text
python scripts/corpus_manifest.py canonical-info
python scripts/corpus_manifest.py verify corpus/liber-primus/manifests/LP-75-IMAGES-v1.0.0.json PATH_TO_PAGES --strict --output verification.json
```

Strict verification passes only when every declared file matches and no undeclared file is present.
