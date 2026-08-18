# HMS Endeavour Public Roadmap

Status: **PLANNED**, **IN DEVELOPMENT**, **INTERNAL TESTING**, **RELEASE CANDIDATE**, **RELEASED**, **DEPRECATED**, **RETIRED**. Release channels are tracked separately.

The machine-readable [product ladder](products/manifest.json) is authoritative for build order and product status. The [instrument manifest](instruments/manifest.json) is authoritative for individual tool contracts and availability.

## Foundation

| Capability | Status |
|---|---|
| Public repository and release boundary | RELEASED |
| Research methodology and publication schemas | RELEASED |
| Record validator and continuous integration | RELEASED — developer source |
| Protected-main governance | RELEASED |
| Membership and Patreon release boundary | RELEASED |
| Corpus provenance and verification manifest | INTERNAL TESTING — verifier development package locally qualified; canonical LP manifest pending |

## Research record

| Capability | Status |
|---|---|
| Source inventory and sanitized audit | RELEASED |
| Page 32 dossier and first closure set | RELEASED — continuing research |
| Page 72 dossier | RELEASED — reconciliation continuing |
| Page 73 dossier and selector correction | RELEASED — provenance reconciliation continuing |
| Known-control reproduction packages | RELEASED — initial non-plaintext controls; solved-material LP control pending |
| Negative-result archive | RELEASED — initial bounded set; continuing curation |
| First HMS-originated verified-result record | PLANNED |

## Atlas and laboratory

| Capability | Status |
|---|---|
| Public 75-page working-corpus map and page index | RELEASED |
| Page regions and Page Sets | PLANNED |
| Comparison workspace | PLANNED |
| Experiment engine and pipeline builder | IN DEVELOPMENT — local GP29, corpus-report validation, and bounded declared GP29 comparison jobs runnable |
| Result comparison and saved research workspace | IN DEVELOPMENT — saved local Runs/Results and export exist; comparison is planned |

## GP systems

| Capability | Status |
|---|---|
| Public GP29 calculator | RELEASED — v0.1.1 public Windows desktop and CLI package |
| Advanced GP Laboratory | PLANNED |
| GP Solver | PLANNED |
| Batch experiment engine and parameter sweeps | PLANNED |

## Proof and integration

| Capability | Status |
|---|---|
| Checksum and corpus-manifest verifier | IN DEVELOPMENT |
| Public reproduction packages | RELEASED / ACTIVE — eleven Runs, eleven Results, four Capsules; RSET-0001 staged and RSET-0002 through RSET-0004 published |
| ProofLock and notary verification | PLANNED |
| Authenticated sockets and API | PLANNED |
| Add-on architecture and plugin SDK | PLANNED |

The roadmap describes intended direction. A planned capability is not an entitlement, release-date promise, or claim that the tool already exists.

## Implementation boundary

- Public GP29 Calculator: v0.1.1 is released under instrument-specific tag `GP29-v0.1.1` with English-letter, Latin-sound, token, and rune input plus deterministic `L/R/prime/N/Q` output. Its exact ZIP, qualification, acceptance limitation, and approval are bound by the public gate.
- HMS Endeavour Lite: bounded public launch workstation in development with the nautical Aegis/HMS shell, GP29, Corpus identity, read-only 75-page Atlas, and Expedition entry workflows.
- HMS Endeavour Runtime Environment: advanced member visual deck in private internal testing with page tabs, zoom/pan, visual marks, page-scoped rune selections, translation notes, and local workspace persistence. No member download is released.
- Hosted Liber Runtime: planned separately from the local workstation; general experiments, hosted persistence, authentication, entitlements, quotas, sockets, Auto Explore, and contextual AEGIS remain future work.

## Frozen product sequence

GP29 release → Corpus Manifest Verifier release → HMS Endeavour Runtime Environment v1 release → Expedition campaign package → Hosted Liber Runtime → Auto Explore → contextual AEGIS → Batch → Advanced GP → Solver → Plugin SDK.

See the [HMS Product Ladder](docs/HMS_PRODUCT_LADDER.md). Advanced work may be researched privately, but it must not displace usable dependency layers or be advertised as released.

See the [tool architecture](docs/tooling/ARCHITECTURE.md). The instrument registry remains authoritative when roadmap prose and promotional language differ.
