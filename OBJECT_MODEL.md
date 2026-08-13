# Canonical HMS Object and Provenance Model

This model is frozen before the first public release so the same identities and relationships can support GitHub evidence, local tools, hosted Runtime workspaces, member research, corrections, and future corpora.

## Canonical chain

```text
Corpus → Page → Region → PageSet → Pipeline → Experiment → Run → Result → Evidence → Claim → HashLock → ProofLock → Publication

For browsable distribution, related Runs and Results may be grouped into a Research Capsule and one or more curated Run Sets:

```text
RUN-#### → RES-#### → CAP-#### → RSET-####
```
```

Every derived object records its direct parents. A public claim must be traceable backward to immutable source and environment manifests without relying on a filename, chat history, or prose description.

## Permanent namespaces

| Prefix | Object | Example |
|---|---|---|
| `CORP` | Corpus manifest | `CORP-0001` |
| `PAGE` | Canonical page version | `PAGE-0001` |
| `REG` | Page region | `REG-0001` |
| `PSET` | Ordered page/region set | `PSET-0001` |
| `PIPE` | Versioned operation pipeline | `PIPE-0001` |
| `OBS` | Observation | `OBS-0001` |
| `HYP` | Hypothesis | `HYP-0001` |
| `EXP` | Experiment definition | `EXP-0001` |
| `RUN` | One execution | `RUN-0001` |
| `RES` | Result | `RES-0001` |
| `NEG` | Bounded negative result | `NEG-0001` |
| `EVD` | Evidence bundle | `EVD-0001` |
| `CLM` | Bounded claim | `CLM-0001` |
| `HL` | HashLock | `HL-0001` |
| `PL` | ProofLock | `PL-0001` |
| `RR` | Research report | `RR-0001` |
| `COR` | Correction | `COR-0001` |
| `RET` | Retraction | `RET-0001` |
| `RC` | Release candidate package | `RC-0001` |
| `ENV` | Deterministic environment | `ENV-0001` |
| `PUB` | Publication decision | `PUB-0001` |
| `XPD` | Public Expedition | `XPD-0001` |
| `CAP` | Research Capsule | `CAP-0001` |
| `RSET` | Curated Run Set | `RSET-0001` |

The original namespace meanings are frozen as of `v0.1.0`; `CAP` and `RSET` are additive Research Archive 1.0 namespaces. Identifiers use four or more digits, are never reassigned, and remain reserved after withdrawal or retraction. Patreon transmission IDs form a separate delivery namespace and do not identify scientific objects.

Every assigned object ID is retained in the [permanent ID registry](registry/id-reservations.json).

## Provenance requirements

Every derived object must record:

- its canonical ID and schema version;
- direct parent object IDs;
- content or manifest hashes for every material input;
- the pipeline and exact parameter family;
- the execution environment manifest and random seed;
- page numbering, alphabet, encoding, and transcription conventions;
- the actor or system that created it and the recorded time;
- visibility and publication state;
- supersession, correction, and retraction links.

Missing links must be explicit. `unknown` is valid intake metadata; an invented provenance link is not.

## Corpus and transcription identity

A source image, canonical transcription, alternative transcription, and user transcription are different versioned objects. Updating a transcription creates a new object and does not rewrite historic runs. A run always retains the exact transcription ID and hash it used.

## Complete-family retention

Runs that search a parameter family must preserve the family definition, total attempts, ranking rule, failures, and selected result. Publishing only an interesting output without its search denominator is not an admissible HMS evidence bundle.

The machine-readable contract is [schemas/hms-object.schema.json](schemas/hms-object.schema.json).

The package and generated-presentation contract is defined in the [Research Archive Standard](docs/RESEARCH_ARCHIVE_STANDARD.md).
