# HMS Endeavour — Admiral Research Station Contract

Status: **MATURE APPLICATION DIRECTION; NOT CURRENT AVAILABILITY**

This is the north-star contract for the integrated HMS / Liber Runtime / AEGIS application. It must be delivered through the staged [HMS Product Ladder](HMS_PRODUCT_LADDER.md), not advertised as one already-built product.

## Authority boundary

- **AEGIS Trust Core** governs identity, permissions, provenance, evidence, verification, ProofLink/ProofLock, recovery, and governance.
- **HMS Endeavour** orchestrates instruments, experiments, Runs, Results, Jobs, solvers, batch work, and plugins.
- **Liber Runtime** provides the LP Atlas, Workbench, Rune/Decrypt/GP29/Geometry labs, Chronicle, Findings, and Evidence.
- **AEGIS AI** assists in the right context rail. It may ask, plan, explain, compare, challenge, and research. It never becomes truth authority, silently runs an experiment, signs, approves, deletes, rewrites, or promotes evidence.
- **Admiral access** is the deepest customer research environment; it is not automatic Vault access.

AEGIS must route authoritative questions to authoritative instruments. It may explain a GP29 result or Corpus Verifier report, but it may not invent the GP value, corpus hash, or verification state itself.

## Application frame

The mature application has four persistent areas:

1. navigation;
2. central research workspace;
3. contextual AEGIS / provenance / evidence rail;
4. bottom job drawer for queued, running, failed, completed, and cancelled work.

Primary destinations are Bridge, Atlas, Laboratory, Voyages, Evidence, Trust, Shipyard, and Observatory. Standard, Advanced, and Developer modes progressively disclose complexity without changing truth.

## Atlas and Workbench

The Atlas covers all 75 pages with immutable canonical images, hashes, metadata, professional zoom/pan and continuous/single-page viewing. Snips create reusable Region objects. Selection works at page, line, word, rune, number, and Region scope.

The Page Workbench supports versioned transcriptions, annotations, search, comparison, PageSets, bookmarks, rules/hints, rune inspection, occurrence search, overlays, and number/totient inspection. Source image, canonical transcription, alternative transcription, and user transcription remain separate immutable inputs.

## Experiment integrity

Before execution, an Experiment declares its question, inputs, versioned Pipeline, parameters, prediction, controls, budget, metrics, and success gate. Runs preserve environment, operation order, seed, artifacts, failures, resource use, and provenance. Results preserve raw output and limitations.

Candidate decryption is named **AUTO EXPLORE**, never AUTO SOLVE. It retains gibberish, failures, and the complete tested family; declared transforms, controls, budget, denominator, and scoring prevent cherry-picking. Solver-class instruments return candidates only.

## Evidence and research memory

The Epistemic Center, Findings Atlas, Chronicle, Field Notes, Wreck Chart, Control Library, and Trust Inspector keep observations, hypotheses, candidates, reproduced results, verified results, negatives, corrections, stale objects, and retractions visibly distinct. Operational provenance is recorded; private chain-of-thought is not a product artifact.

## Instruments and plugins

Instrument families include cryptanalytic, rune, page-geometry, runtime, evidence, and research-history modules. Each declares the full contract in [`instruments/manifest.json`](../instruments/manifest.json). Plugins are versioned, permission-scoped, revocable, sandboxed, and denied network or Vault access unless explicitly declared and approved.

## Projects, privacy, and recovery

Projects reference corpora by identity and hash by default instead of copying source material. Work is local/private by default. Upload, sharing, review, and publication are explicit transitions. The application restores projects, tabs, drafts, jobs, and recoverable state without silently changing evidence.

## Visual and interaction rule

Use a dark-first professional research interface with restrained cyan and brass accents. HMS language may provide identity, but plain subtitles must keep actions understandable. Avoid decorative cyberpunk density.

The master research rule is: **generate candidates aggressively; interpret conservatively.**
