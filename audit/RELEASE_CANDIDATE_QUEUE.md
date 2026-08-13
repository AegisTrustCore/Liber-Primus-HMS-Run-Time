# Public Release-Candidate Roadmap

Status: **TRIAGE ONLY — NO ITEM IS PUBLICLY VERIFIED YET**

This is a public roadmap, not the HMS research queue. It records the existence, evidence class, current state, and public release gate of candidate packages without exposing gated experimental instructions, private datasets, unpublished parameter choices, or the active workbench.

| Public ID | Evidence class | Current state | Gate before public release |
|---|---|---|---|
| RC-001 | Known control | Reproduction pending | Freeze canonical inputs, package a clean implementation, and reproduce the declared comparison independently |
| RC-002 | Bounded negative | Reproduction pending | Define the tested family and success criterion, rerun the controls, and state the exact rejection boundary |
| RC-003 | Known control | Provenance reconciliation | Reconcile source identity and numbering, package the comparison family, and complete a clean replay |
| RC-004 | Correction | Superseded-claim link pending | Identify the superseded interpretation, reproduce the narrowing evidence, and publish both together |
| RC-005 | Structural observation | Independent implementation pending | Freeze canonical source material, document the rule and ambiguity boundary, and reproduce independently |

Exact source experiments, active hypotheses, parameters, datasets, and reproduction assignments remain in the private HMS ledger until a candidate is intentionally promoted through the public release gate.

## Required labels

- `KNOWN_CONTROL`: independently available solved material used to test behavior.
- `STRUCTURAL`: a reproducible relationship that does not claim semantic plaintext.
- `NEGATIVE`: a bounded family failed a declared gate.
- `CORRECTION`: a previous interpretation is narrowed or withdrawn.
- `VERIFIED_RESULT`: reserved for a completed public record, never inferred from an internal status.
