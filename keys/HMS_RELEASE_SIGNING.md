# HMS Release Signing Identity

This is the public trust root for the HMS Endeavour `v0.1.x` release series. It is independent of the historical Cicada 3301 evidence key.

| Field | Value |
|---|---|
| Identity | `HMS Endeavour Release Signing` |
| OpenPGP fingerprint | `7B4E 8795 A984 2FB0 4301 114B 7A7B 2779 E2F1 8AE6` |
| Created | 2026-07-25 |
| Primary algorithm | RSA 2048 |
| Primary usage | Certification and signing |
| Release-series scope | `v0.1.x` |

The public key is attached to the [`v0.1.0` GitHub Release](https://github.com/AegisTrustCore/Liber-Primus-HMS-Run-Time/releases/tag/v0.1.0) as `HMS-Endeavour-v0.1.0-signing-key.asc`. Private key material is not stored in GitHub, CI, Patreon, the Runtime, or Codex context.

## Verify the release assets

```bash
gh release download v0.1.0 -R AegisTrustCore/Liber-Primus-HMS-Run-Time
gpg --import HMS-Endeavour-v0.1.0-signing-key.asc
gpg --verify SHA256SUMS.asc SHA256SUMS
sha256sum --check SHA256SUMS
```

## Verify the signed tag

```bash
git fetch origin tag v0.1.0
git tag --verify v0.1.0
```

The fingerprint printed by GnuPG must exactly match the fingerprint above. The historical Cicada 3301 key must never be accepted as the HMS release identity.
