# Public Research Index

Last reviewed: 2026-08-12

This index answers three different questions separately: what is publicly verified, what is a known control, and what is still being tested. A promising result does not move between these categories by wording alone.

## Current evidence map

| Class | Current public position | Supporting location |
|---|---|---|
| Historical PGP identity artifact | Bundled key bytes and full parsed fingerprint verified; provenance claim remains narrowly scoped | [OBS-0001](research/records/OBS-0001.json) |
| New HMS-originated LP plaintext | None published | [Verified results](VERIFIED_RESULTS.md) |
| Known solved-material controls | Strong reproduction candidates identified; public packages pending | [Known controls](KNOWN_CONTROLS.md) |
| Page 32 | Structural candidates and bounded negative results; rune prose remains unsolved | [Page 32 dossier](pages/page-032/README.md) |
| Page 72 | Structural/register candidates; no reviewed record explicitly reports plaintext recovery | [Page 72 dossier](pages/page-072/README.md) |
| Page 73 | Known-control replay candidate; selector interpretation corrected | [Page 73 dossier](pages/page-073/README.md) |
| Negative results | Multiple bounded candidates identified; none packaged as a final public record yet | [Negative results](NEGATIVE_RESULTS.md) |
| Corrections | Page 73 visible-hash causal-selector claim withdrawn | [Corrections](CORRECTIONS.md) |

## Public release roadmap

1. `RC-0001` — package and reproduce a solved-material known control.
2. `RC-0002` — package one bounded negative result with its complete tested family.
3. `RC-0003` — reconcile provenance before publishing another known-control replay.
4. `RC-0004` — publish a correction beside the narrower result it preserves.
5. `RC-0005` — independently implement one structural observation.

Exact assignments, parameters, and datasets belong to the private research queue. GitHub records only the [public release-candidate roadmap](audit/RELEASE_CANDIDATE_QUEUE.md) until a package passes the public gate.
