# HMS Endeavour — Liber Primus Public Research Record

> **HMS Endeavour v0.1.0 is the released public research foundation.** This repository is the evidence, verification, puzzle, and public tooling layer for our independent *Liber Primus* research. It is not a claim that the full corpus has been solved.

> **Independent research:** HMS Endeavour is not Cicada 3301, has no affiliation with or endorsement from Cicada 3301, and does not possess Cicada 3301's private signing key. See [Cicada 3301 and the historical OpenPGP key](CICADA_3301.md).

## Current public releases

| Release | What it contains | Access |
|---|---|---|
| [HMS Endeavour v0.1.0](https://github.com/coreystilwell3-eng/Liber-Primus-HMS-Run-Time/releases/tag/v0.1.0) | Public research foundation, schemas, evidence records, validation source, and provenance tooling | Free / public |
| [Research Release RR-0002](https://github.com/coreystilwell3-eng/Liber-Primus-HMS-Run-Time/releases/tag/RR-0002) | Five bounded closure and correction packages with a portable evidence archive | Free / public |
| [Research Release RR-0003](https://github.com/coreystilwell3-eng/Liber-Primus-HMS-Run-Time/releases/tag/RR-0003) | E1477 board-family closure, E156 solved-LP1 segment frames, and E159 terminal known controls | Free / public |

Only the releases listed above are downloadable customer-facing GitHub releases. Development source may be visible on `main` before a packaged tool is approved for release.

## Start here

| I want to… | Start with |
|---|---|
| Understand the 75-page working corpus | [Liber Primus: Start Here](corpus/liber-primus/START-HERE.md) |
| See published findings and their evidence | [Explore Results](research/results/README.md) |
| Reproduce public runs | [Research Archive](research/README.md) |
| Try the free public puzzle | [Expedition 001: The Evidence Ledger](challenges/expedition-001/README.md) |
| Check what is released versus planned | [Public Releases](PUBLIC_RELEASES.md) and [Project Status](PROJECT_STATUS.md) |
| Learn how claims are classified | [Methodology and evidence states](METHODOLOGY.md#evidence-states) |

## Available now

- A complete [75-page working-corpus map](corpus/liber-primus/README.md), page index, timeline, and source-verification path.
- Structured public Result objects and reproducible Runs, including [RSET-0002](research/runsets/RSET-0002/START-HERE.md) and [RSET-0003](research/runsets/RSET-0003/START-HERE.md).
- [RSET-0004](research/runsets/RSET-0004/START-HERE.md): three bounded objects spanning a negative route closure, a structural control, and two established terminal plaintext controls.
- Public audit dossiers for pages 32, 72, and 73. These record bounded observations and controls; they are not presented as new verified plaintext solves.
- Historical Cicada 3301 OpenPGP provenance material and a local verification path.
- Public schemas, release gates, record validators, and developer-source utilities.
- A public synthetic puzzle preview and source verifier for practicing HMS evidence classification.

The repository currently has **three public GitHub releases**. Its Research Archive contains **11 published Runs, 11 published Results, 4 published Capsules, and zero HMS-verified recoveries of previously unknown Liber Primus plaintext**. Open, negative, control, corrected, and verified states remain visibly separate.

## Public puzzles — Observer access

### Expedition 001: The Evidence Ledger

| Field | Current state |
|---|---|
| Access | **Observer — free and public** |
| Difficulty | Deckhand / beginner |
| Purpose | Synthetic method training: classify evidence before making a claim |
| Public material | Briefing, worksheet, hints, and developer-source verifier |
| Campaign | **Closed** — practice preview only; submissions are not being accepted |
| Solution | Sealed until the formal campaign closes under the published release process |
| Packaged download | Not public yet; the Windows candidate still requires its release gate |

[Enter Expedition 001](challenges/expedition-001/README.md) · [Read the public hints](challenges/expedition-001/HINTS.md) · [See all challenges](challenges/README.md)

The puzzle is synthetic and does not conceal an unpublished *Liber Primus* research claim. Its eventual solution remains public rather than becoming a paid answer.

## Public tool status

| Instrument | Status | What a visitor can use today |
|---|---|---|
| Public Record Validator | Released | Python developer source in `v0.1.0` |
| LP Source Audit Inventory | Released | Python developer source in `v0.1.0` |
| Expedition Verifier | In development | Public Python source for Expedition 001; no approved customer package |
| Public GP29 Calculator | **Release candidate** | Source is visible; the exact Windows candidate is awaiting clean-machine UAT and human approval |
| Corpus Manifest Verifier | Internal testing | Developer source only; canonical public package not released |
| Liber Runtime Beta | In development | Local developer core only; no hosted public service |
| HMS Endeavour Lite | Planned | Architecture only; implementation begins after GP29 release and Corpus Verifier RC |
| Advanced instruments | Planned | No solver, batch engine, API/socket layer, or Plugin SDK is available |

The GP29 calculator is a deterministic calculator, **not a solver**. It will receive a public download only after the exact candidate passes its remaining release gate. Track that gate in [GitHub issue #23](https://github.com/coreystilwell3-eng/Liber-Primus-HMS-Run-Time/issues/23).

See the machine-readable [Product Ladder](products/manifest.json), readable [HMS Product Ladder](docs/HMS_PRODUCT_LADDER.md), [Instrument Manifest](instruments/manifest.json), [Instrument Registry](instruments/README.md), and [Roadmap](ROADMAP.md) for exact delivery modes and boundaries.

## Current research position

- Pages 32, 72, and 73 have public audit dossiers and known-control material. Their labels describe the evidence actually established; they do not imply that every interpretation is solved.
- RSET-0002 publishes bounded historical closures and corrections.
- RSET-0003 publishes the E1059 ledger verification and a bounded default-key OutGuess branch closure.
- Promising routes, failed routes, hypotheses, and corrections remain distinguishable in the [Research Index](RESEARCH_INDEX.md).
- No HMS record currently establishes a newly verified *Liber Primus* plaintext. If that changes, it must pass the same public evidence and release controls.

## What comes next

1. Complete independent clean-machine UAT and owner approval for the exact GP29 v0.1.0 candidate; publish it only if the gate passes.
2. Complete the Expedition 001 customer package and open a formal public campaign under a separately approved gate.
3. Finish the canonical corpus manifest and customer-facing Corpus Manifest Verifier.
4. Build Endeavour Lite, then add the LP Atlas, Rune Workbench, and Experiment Engine as accepted increments.
5. Grow those increments into Liber Runtime Beta; add Auto Explore and contextual AEGIS only after the object lifecycle is dependable.
6. Add batch, Advanced GP, solver, sockets/API, and the Plugin SDK only after their dependency gates are met.

The detailed sequence is maintained in [Next Steps](NEXT_STEPS.md).

## Public, member, and private layers

- **Public GitHub:** stable claims, evidence needed to verify them, negative results safe to disclose, corrections, free puzzles, and approved public tools.
- **Patreon expedition layers:** early commentary, guided walkthroughs, development notes, structured research context, and tier-appropriate participation. Paid access does not buy a “more true” answer.
- **Private research:** unreviewed branches, sensitive routes, unpublished candidates, credentials, personal data, and material that has not passed its disclosure and release gates.

See [Membership](MEMBERSHIP.md), the [Patreon release matrix](patreon/RELEASE_MATRIX.md), and [Release Policy](RELEASE_POLICY.md).

## Standards and verification

- [Object Model](OBJECT_MODEL.md) — permanent IDs and provenance
- [Methodology](METHODOLOGY.md) — what HMS means by verified
- [Evidence States](METHODOLOGY.md#evidence-states) — verified, control, open, negative, and corrected
- [Public Release Gate](PUBLIC_RELEASE_GATE.md) — mandatory human-controlled approval
- [Signing](SIGNING.md) — tags, hashes, signatures, and project identity
- [Disclosure Policy](DISCLOSURE_POLICY.md) — handling significant discoveries
- [Corrections](CORRECTIONS.md) — narrowed, superseded, and withdrawn interpretations
- [Research Privacy](PRIVACY.md) — private-by-default handling and compute boundaries

## Release principle

HMS Endeavour publishes methods, evidence, limitations, and reproducible negative results—not just conclusions. A visible branch, source file, or release candidate is not a public product release until its recorded gate is approved.

Original project work is licensed under the [Apache License 2.0](LICENSE), subject to the third-party and source-material boundaries in [NOTICE](NOTICE).
