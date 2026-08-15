# Source, rights, and carrier verification

## Public boundary

HMS Endeavour does not claim ownership of Liber Primus. The repository's Apache-2.0 license covers original HMS work only; it does not grant redistribution rights for Cicada 3301 material or third-party archive contents.

The working source set was compared with the publicly accessible community archive at [krisyotam/cicada3301](https://github.com/krisyotam/cicada3301). That reference is an acquisition and provenance lead, not an HMS warranty of authenticity, completeness, safety, copyright status, or permission to redistribute.

Because no source-specific license has been established for the 75 JPEG files, HMS publishes their identifiers, metadata, and derived ledgers without copying the image bytes into this repository.

## Canonical identity

The authoritative HMS carrier registry is:

- [LP-75-IMAGES-v1.0.0.json](manifests/LP-75-IMAGES-v1.0.0.json), the machine-readable verifier manifest; and
- [canonical_page_manifest.csv](../../research/runs/RUN-0008/historical/canonical_page_manifest.csv)

It declares exactly 75 files, `00.jpg` through `74.jpg`, with byte length, pixel dimensions, and SHA-256 digest. Each registered image is 2400 by 3600 pixels. The complete declared set totals 52,248,065 bytes.

"Canonical" here means **the exact carrier bytes used by the cited HMS experiment**. It does not mean HMS created the page, owns it, or has authenticated every point in its historical chain of custody.

## Verification procedure

1. Obtain the files only from a source you are legally entitled to use.
2. Keep the originals unchanged. Work on a copy.
3. Confirm that the set contains exactly `00.jpg` through `74.jpg`.
4. Compute SHA-256 for each file.
5. Compare the digest, byte count, width, and height with the manifest.
6. Record mismatches; do not silently substitute, recompress, rename, crop, enhance, or repair a carrier.
7. Bind every experiment to the manifest digest and exact page digest it used.

PowerShell example for one page:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath .\00.jpg
```

GNU/Linux example for one page:

```bash
sha256sum ./00.jpg
```

The expected hash for each page is in both manifests. Corpus Manifest Verifier `0.1.0-rc.3` is bound to the JSON manifest, but remains a release candidate until clean-environment human UAT and exact-package approval are complete. Until then, native hashing remains the public reference check.

## Derived images

Never replace a registered carrier with an enhanced, annotated, OCR-cleaned, color-corrected, resized, or recompressed version. Derived images can be useful, but they must receive a separate object ID, hash, transformation record, and parent-carrier link.

This is especially important for steganographic work: two images that look identical to a human can have materially different encoded bytes and coefficient structures.

## Future image release gate

An image-bearing release requires, at minimum:

- a redistribution-cleared source or documented permission;
- an exact match to the public manifest;
- provenance and acquisition records;
- a declaration that the images are third-party material;
- archive hashes and a contents manifest; and
- a separate human-approved public release gate.

Until those conditions are satisfied, the complete index is public and the image bytes remain external.
