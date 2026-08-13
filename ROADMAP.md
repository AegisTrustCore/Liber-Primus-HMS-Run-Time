# HMS Endeavour Public Roadmap

Legend: **RELEASED**, **RELEASE CANDIDATE**, **IN DEVELOPMENT**, **PLANNED**

The machine-readable [instrument manifest](instruments/manifest.json) is authoritative for individual tool status.

## Foundation

| Capability | Status |
|---|---|
| Public repository and release boundary | RELEASE CANDIDATE |
| Research methodology and publication schemas | RELEASE CANDIDATE |
| Record validator and continuous integration | RELEASE CANDIDATE |
| Protected-main governance | RELEASED |
| Membership and Patreon release boundary | RELEASE CANDIDATE |
| Corpus provenance and verification manifest | IN DEVELOPMENT |

## Research record

| Capability | Status |
|---|---|
| Source inventory and sanitized audit | RELEASE CANDIDATE |
| Page 32 dossier | IN DEVELOPMENT |
| Page 72 dossier | IN DEVELOPMENT |
| Page 73 dossier and selector correction | IN DEVELOPMENT |
| Known-control reproduction packages | IN DEVELOPMENT |
| Negative-result archive | IN DEVELOPMENT |
| First HMS-originated verified-result record | PLANNED |

## Atlas and laboratory

| Capability | Status |
|---|---|
| Public page index | PLANNED |
| Page regions and Page Sets | PLANNED |
| Comparison workspace | PLANNED |
| Experiment engine and pipeline builder | PLANNED |
| Result comparison and saved research workspace | PLANNED |

## GP systems

| Capability | Status |
|---|---|
| Public GP29 calculator | IN DEVELOPMENT |
| Advanced GP Laboratory | PLANNED |
| GP Solver | PLANNED |
| Batch experiment engine and parameter sweeps | PLANNED |

## Proof and integration

| Capability | Status |
|---|---|
| Checksum and corpus-manifest verifier | IN DEVELOPMENT |
| Public reproduction packages | PLANNED |
| ProofLock and notary verification | PLANNED |
| Authenticated sockets and API | PLANNED |
| Add-on architecture and plugin SDK | PLANNED |

The roadmap describes intended direction. A planned capability is not an entitlement, release-date promise, or claim that the tool already exists.

## Implementation boundary

- Public GP29 Calculator: held for a separate `v0.1` release after the foundation.
- HMS Endeavour Lite: local interface and portable-result contract documented; application not yet implemented.
- Liber Runtime: hosted job, workspace, entitlement, and verification boundaries documented; service not yet implemented.

See the [tool architecture](docs/tooling/ARCHITECTURE.md). The instrument registry remains authoritative when roadmap prose and promotional language differ.
