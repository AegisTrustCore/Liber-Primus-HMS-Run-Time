# Public Release-Candidate Roadmap

Status: **MIXED — INITIAL OBJECTS PROMOTED; REMAINING ITEMS REQUIRE REVIEW**

This roadmap began as pre-publication triage. Promoted work is now identified by permanent `RUN`, `RES`, `CAP`, and `RSET` IDs in the canonical Research Archive. The generic `RC` rows below describe remaining capability classes; they must not be treated as aliases for already-published objects unless an explicit migration record says so.

This is a public roadmap, not the HMS research queue. It records the existence, evidence class, current state, and public release gate of candidate packages without exposing gated experimental instructions, private datasets, unpublished parameter choices, or the active workbench.

| Public ID | Evidence class | Current state | Gate before public release |
|---|---|---|---|
| RC-0001 | Known control | E159 terminal controls published in `RSET-0004`; further controls require separate review | Freeze canonical inputs, package a clean implementation, and reproduce the declared comparison independently |
| RC-0002 | Bounded negative | Examples published in `RSET-0002`; E1059 published in `RSET-0003`; E1477 published in `RSET-0004` | Approve only exact subjects with the complete tested family, controls, reproduction boundary, and explicit non-claims |
| RC-0003 | Known control | Provenance reconciliation | Reconcile source identity and numbering, package the comparison family, and complete a clean replay |
| RC-0004 | Correction | Initial anti-post-hoc correction published as `RES-0007`; further candidates pending | Identify the superseded interpretation, reproduce the narrowing evidence, and publish both together |
| RC-0005 | Structural observation | E156 solved-LP1 segment frame published in `RSET-0004`; further candidates pending | Freeze canonical source material, document the rule and ambiguity boundary, and reproduce independently |

Exact source experiments, active hypotheses, parameters, datasets, and reproduction assignments remain in the private HMS ledger until a candidate is intentionally promoted through the public release gate.

## Required labels

- `KNOWN_CONTROL`: independently available solved material used to test behavior.
- `STRUCTURAL`: a reproducible relationship that does not claim semantic plaintext.
- `NEGATIVE`: a bounded family failed a declared gate.
- `CORRECTION`: a previous interpretation is narrowed or withdrawn.
- `VERIFIED_RESULT`: reserved for a completed public record, never inferred from an internal status.
