# Cicada 3301, Liber Primus, and HMS Endeavour

HMS Endeavour is an independent research project focused on the unresolved material and reproducible study of *Liber Primus*, a runic work released in connection with Cicada 3301.

It is not Cicada 3301, does not speak for Cicada 3301, and does not claim endorsement, succession, recruitment authority, or possession of a Cicada private key.

## Historical OpenPGP identity reference

The historical Cicada 3301 public key preserved in this repository has the full fingerprint:

```text
6D85 4CD7 9333 22A6 01C3  286D 181F 01E5 7A35 090F
```

Long key ID: `181F01E57A35090F`

User ID in the key: `Cicada 3301 (845145127)`

Created: `2012-01-05`

Bundled armored key: [`keys/cicada-3301-2012.asc`](keys/cicada-3301-2012.asc)

Always compare the **full fingerprint**. A name, avatar, short key ID, cryptic tone, or copied key block is not proof that a new message came from Cicada 3301.

## What the key establishes

The bundled bytes parse as an OpenPGP public key with the fingerprint above. They can be used to test signatures attributed to that key.

The key alone does not establish:

- that every historical item attributed to Cicada 3301 is authentic;
- that any present-day account controls the corresponding private key;
- that HMS Endeavour is affiliated with Cicada 3301; or
- that an HMS research claim is correct.

HMS messages and releases are HMS material. They must never be presented as signed Cicada transmissions.

## Verification

With GnuPG installed:

```bash
python scripts/verify_cicada_key.py
```

Expected primary fingerprint:

```text
6D854CD7933322A601C3286D181F01E57A35090F
```

The structured verification record is [`OBS-0001`](research/records/OBS-0001.json). See [`keys/README.md`](keys/README.md) for file integrity information and safe usage notes.
