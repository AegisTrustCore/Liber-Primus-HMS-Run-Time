# HMS Product Ladder

Status: **FROZEN ARCHITECTURE**
Last reviewed: 2026-08-17

This document defines what HMS builds, in what order, and what prevents a planned capability from being advertised as available. The machine-readable source is [`products/manifest.json`](../products/manifest.json); individual tool contracts are authoritative in [`instruments/manifest.json`](../instruments/manifest.json).

```text
PUBLIC FOUNDATION
        ↓
EXPEDITION VERIFIER
        ↓
GP29
        ↓
CORPUS MANIFEST VERIFIER
        ↓
ENDEAVOUR LITE
        ↓
LIBER RUNTIME BETA
        ↓
ADVANCED INSTRUMENTS
        ↓
FULL HMS / AEGIS RESEARCH STATION
```

The arrows describe dependency maturity, not a requirement that all engineering occur serially. GP29 is released. Corpus Manifest Verifier and the local HMS Endeavour Runtime Environment are the two current public release candidates; Expedition remains separately campaign-gated.

## Current product truth

| Product | Current state | Next state | Gate |
|---|---|---|---|
| Public Foundation | RELEASED | — | Continue admitting material only through public evidence and release gates |
| Expedition Verifier | IN_DEVELOPMENT | RELEASE_CANDIDATE | Customer package, solution-leak audit, synthetic/public tests, exact-subject approval |
| Public GP29 Calculator | RELEASED | Maintain | Approved exact-subject gate; future changes require a new release subject |
| Corpus Manifest Verifier | IN_DEVELOPMENT — 0.2.0-dev | RELEASE_CANDIDATE | New nautical viewer package, exact Windows qualification, UAT, and checksum-bound approval |
| HMS Endeavour Lite | IN_DEVELOPMENT — 0.2.0-dev | RELEASE_CANDIDATE | Freeze the bounded public surface and qualify its standalone package |
| HMS Endeavour Runtime Environment | INTERNAL_TESTING — 1.1.0-dev | RELEASE_CANDIDATE | Private repository, share-safe export, entitlement packaging, member UAT, and checksum-bound approval |
| Hosted Liber Runtime | PLANNED | IN_DEVELOPMENT | Hosted persistence, accounts/entitlements, sockets, Auto Explore, contextual AEGIS, and separately reviewed capability gates |
| Advanced Instruments | PLANNED / mixed private prototypes | IN_DEVELOPMENT per module | Individual contracts, tests, capability gates, limitations, approval |
| Full HMS / AEGIS Research Station | PLANNED | IN_DEVELOPMENT | Accepted dependency layers, privacy, trust, recovery, permissions, and operations |

Source visibility is not customer availability. The status vocabulary is `PLANNED`, `IN_DEVELOPMENT`, `INTERNAL_TESTING`, `RELEASE_CANDIDATE`, `RELEASED`, `DEPRECATED`, and `RETIRED`. Release channel is separate: `DEVELOPMENT`, `EXPERIMENTAL`, `BETA`, `RC`, or `STABLE`.

## Frozen build order

1. GP29 release
2. Corpus Manifest Verifier release candidate
3. Expedition Verifier public package
4. HMS Endeavour Runtime Environment v1 (includes LP Atlas, Rune Workbench, and bounded Experiment Engine)
5. Hosted Liber Runtime
6. Auto Explore
7. AEGIS contextual integration
8. Batch Engine
9. Advanced GP Laboratory
10. Solver
11. Plugin SDK

Advanced Solver, Batch, API/socket, and Plugin SDK work must not displace the usable dependency layers.

## Product roles

- **Expedition Verifier teaches participation.** It returns PASS/FAIL and a non-disclosing receipt under a frozen challenge contract.
- **GP29 provides calculation.** It exposes deterministic `L`, `R`, `p`, `N`, and `Q`; it is not a solver.
- **Corpus Manifest Verifier establishes source trust.** It says whether a folder matches a manifest, not whether the manifest is historically authentic.
- **HMS Endeavour Runtime Environment unifies public instruments.** It is the first coherent local-first desktop workstation and turns source selections into objects, experiments, Runs, Results, evidence, and reproducible history.
- **Hosted Liber Runtime extends collaboration.** It adds reviewed networked capabilities later; it is not a second name for the local release candidate.
- **Advanced Instruments add capability.** Each module has its own contract and authority boundary.
- **AEGIS connects and explains.** It invokes authoritative tools and explains their results; it does not impersonate them or promote evidence.

## Access is capability, not truth

| Capability | Observer | Pilgrim | Navigator | Cartographer | Admiral |
|---|---|---|---|---|---|
| Expedition Verifier, GP29 Basic, Corpus Verifier | Full when released | Full | Full | Full | Full |
| HMS Endeavour Runtime Environment and LP Atlas | Full when released | Full | Full | Full | Full |
| Rune Workbench | Preview | Preview | Full | Full | Full |
| Basic experiments | — | Preview | Full | Full | Full |
| Auto Explore / Advanced GP | — | — | Selected | Full | Full |
| Batch Engine | — | — | Quota | Full | Full |
| Experimental Solver | — | — | — | Preview | Full |
| Plugin SDK | — | — | — | — | Full |

This matrix is a target architecture, not a statement that unreleased capabilities are available. Paid access may provide more capability, context, compute, or participation; it never creates a “more true” result.

## Customer-ready definition

An HMS instrument is customer-ready only when it has a deterministic core, tested input/output contract, human-usable interface, standalone delivery, quick start, self-test, export, visible version, clear limitations, provenance, checksums, release manifest, ordinary-user acceptance, and human approval bound to the exact release subject.

## Shared product language

Every instrument uses the same object model, evidence vocabulary, Trust Core boundary, design system, and Result shell:

`OBJECT · STATUS · INPUT · OUTPUT · INTERPRETATION · LIMITATIONS · PROVENANCE · EXPORT`

Every screen answers: what object is this, what is its status, what can the researcher do, what supports it, and what is the next step?
