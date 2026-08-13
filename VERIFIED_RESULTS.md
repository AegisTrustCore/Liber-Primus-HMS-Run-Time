# Verified Results

This ledger contains only HMS-originated claims that have passed the public release gate defined in [METHODOLOGY.md](METHODOLOGY.md).

## Current ledger

### OBS-0001 — historical OpenPGP key fingerprint

The bundled public-key bytes parse to the fingerprint recorded in [`OBS-0001`](research/records/OBS-0001.json). This is a verified provenance artifact result, not a recovered Liber Primus plaintext result and not evidence of HMS affiliation with Cicada 3301.

## Liber Primus plaintext ledger

No HMS-originated research record has completed public packaging yet.

This does **not** mean the audit found nothing useful. It found positive-control replays on already-solved Liber Primus material, structural candidates, and bounded negative results. Their public states are listed in the [release-candidate roadmap](audit/RELEASE_CANDIDATE_QUEUE.md), but exact active research detail remains private until a package passes clean reproduction and evidence review.

In particular, reproducing known plaintext is evidence that a method or runtime stage behaves as claimed on that control. It is not a claim that HMS first translated that page, and it is not proof that the same method solves an unsolved page.

## Public reproduction runs

The first bounded [public run drop](reports/PUBLIC_RUNS_001.md) contains:

- `RUN-0001`, a clean replay of the already-public historical OpenPGP artifact verification;
- `RUN-0002`, synthetic acceptance and rejection tests for the local Expedition verifier core.

Neither run is an LP plaintext result, route disclosure, or claim that Expedition 001 is open.
