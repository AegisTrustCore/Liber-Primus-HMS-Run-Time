# HMS Instrument Registry

The machine-readable registry is [`manifest.json`](manifest.json). It is the authoritative public answer to “does this tool exist yet?”

| Instrument | Purpose | Status | Intended access |
|---|---|---|---|
| Public Record Validator | Enforce public record and dossier invariants | RELEASE CANDIDATE | Observer |
| LP Source Audit Inventory | Hash and classify private intake without publishing raw paths | RELEASE CANDIDATE | Observer |
| Corpus Manifest Verifier | Verify canonical corpus inputs and hashes | IN DEVELOPMENT | Observer |
| Public GP29 Calculator | Strict rune/token GP lookup and summation CLI | RELEASE CANDIDATE | Observer |
| Advanced GP Laboratory | Saved calculations, comparisons, and advanced analysis | PLANNED | Cartographer |
| Liber Runtime Beta | Hosted personal research workspace | PLANNED | Navigator |
| GP Solver | Automated candidate and parameter exploration | PLANNED | Navigator |
| Batch Experiment Engine | Queued runs, sweeps, and comparisons | PLANNED | Navigator |
| Socket/API Integration Layer | Authenticated programmatic Runtime access | PLANNED | Admiral |
| Add-on and Plugin SDK | Capability-scoped instrument extensions | PLANNED | Admiral |

`PLANNED` is not availability. Access levels describe the current intended destination and may be revised before implementation.

Release-candidate instruments exist in draft PR #1 but are not part of `main` or a tagged GitHub release yet. The [GP29 Calculator](../tools/gp29/README.md) is now runnable in the review branch.
