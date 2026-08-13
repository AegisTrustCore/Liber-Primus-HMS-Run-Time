# Public Research Index

Last reviewed: 2026-08-13

This index answers three different questions separately: what is publicly verified, what is a known control, and what is still being tested. A promising result does not move between these categories by wording alone.

## Current evidence map

| Class | Current public position | Supporting location |
|---|---|---|
| Historical PGP identity artifact | Bundled key bytes and full parsed fingerprint verified; provenance claim remains narrowly scoped | [OBS-0001](research/records/OBS-0001.json) |
| Public Results | Eight Results: one provenance result, one software control, five bounded negative/null Results, and one correction; none is an LP plaintext recovery | [Browse Results](research/results/README.md) |
| Public reproduction runs | Eight Runs across artifact verification, synthetic controls, acquisition boundaries, Page 32 holdouts, correction auditing, and the E1059 default-key OutGuess calibration | [Browse Runs](research/runs/README.md) |
| Research Capsules | Three Capsules covering the public verification foundation, Page 32 manifest-interpretation closures, and E1059 OutGuess closure | [Browse Capsules](research/capsules/README.md) |
| New HMS-originated LP plaintext | None published | [Verified results](VERIFIED_RESULTS.md) |
| Known solved-material controls | Strong reproduction candidates identified; public packages pending | [Known controls](KNOWN_CONTROLS.md) |
| Page 32 | Structural candidates and bounded negative results; rune prose remains unsolved | [Page 32 dossier](pages/page-032/README.md) |
| Page 72 | Structural/register candidates; no reviewed record explicitly reports plaintext recovery | [Page 72 dossier](pages/page-072/README.md) |
| Page 73 | Known-control replay candidate; selector interpretation corrected | [Page 73 dossier](pages/page-073/README.md) |
| Published closure run set | Five reviewed historical closure runs: acquisition null, three Page 32 negatives, and one anti-post-hoc correction | [RSET-0002](research/runsets/RSET-0002/README.md) |
| Published OutGuess closure | E1059 closes only the frozen default-key OutGuess 0.13 lane; carrier-level reproduction remains partial | [RSET-0003](research/runsets/RSET-0003/START-HERE.md) |
| Negative results | Five structured bounded negative/null Results are packaged; RSET-0002 and RSET-0003 are published | [Negative results](NEGATIVE_RESULTS.md) |
| Corrections | Page 73 visible-hash causal-selector claim withdrawn; Page 32 terminal holdout eligibility narrowed | [Corrections](CORRECTIONS.md) |

## Public release roadmap

1. `RC-0001` — package and reproduce a solved-material known control.
2. `RC-0002` — package one bounded negative result with its complete tested family.
3. `RC-0003` — reconcile provenance before publishing another known-control replay.
4. `RC-0004` — publish a correction beside the narrower result it preserves.
5. `RC-0005` — independently implement one structural observation.

Exact assignments, parameters, and datasets belong to the private research queue. GitHub records only the [public release-candidate roadmap](audit/RELEASE_CANDIDATE_QUEUE.md) until a package passes the public gate.

The structured [Research Archive](research/README.md) is the canonical publication surface. Markdown ledgers explain the record; package manifests and their linked artifacts are the record.
