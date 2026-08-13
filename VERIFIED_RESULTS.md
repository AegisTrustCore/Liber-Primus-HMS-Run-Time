# Verified Results

This ledger contains only HMS-originated claims that have passed the public release gate defined in [METHODOLOGY.md](METHODOLOGY.md).

## Current ledger

### OBS-0001 — historical OpenPGP key fingerprint

The bundled public-key bytes parse to the fingerprint recorded in [`OBS-0001`](research/records/OBS-0001.json). This is a verified provenance artifact result, not a recovered Liber Primus plaintext result and not evidence of HMS affiliation with Cicada 3301.

The corresponding first-class Result is [`RES-0001`](research/results/RES-0001/README.md), supported by the downloadable [`RUN-0001`](research/runs/RUN-0001/README.md) execution package.

[`RES-0002`](research/results/RES-0002/README.md) records the Expedition verifier's reproduced synthetic-control behavior. It is a software known control, not a Liber Primus result.

## Liber Primus plaintext ledger

No HMS-originated recovery of previously unknown Liber Primus plaintext has completed public packaging.

This does **not** mean the audit found nothing useful. It found positive-control replays on already-solved Liber Primus material, structural candidates, and bounded negative results. Their public states are listed in the [release-candidate roadmap](audit/RELEASE_CANDIDATE_QUEUE.md), but exact active research detail remains private until a package passes clean reproduction and evidence review.

In particular, reproducing known plaintext is evidence that a method or runtime stage behaves as claimed on that control. It is not a claim that HMS first translated that page, and it is not proof that the same method solves an unsolved page.

## Public reproduction runs

The first bounded [structured run set](research/runsets/RSET-0001/README.md) contains:

- `RUN-0001`, a clean replay of the already-public historical OpenPGP artifact verification;
- `RUN-0002`, synthetic acceptance and rejection tests for the local Expedition verifier core.

Neither run is an LP plaintext result, route disclosure, or claim that Expedition 001 is open.

The second structured set, [`RSET-0002`](research/runsets/RSET-0002/README.md), publishes bounded negatives and a correction. Those records belong in the negative-result and correction ledgers, not in the verified-plaintext ledger.
