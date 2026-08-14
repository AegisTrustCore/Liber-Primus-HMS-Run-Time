# HMS Instrument Registry

The machine-readable registry is [`manifest.json`](manifest.json). It is the authoritative public answer to “does this tool exist yet, what is it allowed to mean, and how can it actually be used?” Product order and dependencies are maintained separately in the [HMS Product Ladder](../docs/HMS_PRODUCT_LADDER.md).

| Instrument | Status | Delivery reality | Intended access |
|---|---|---|---|
| Public Record Validator | RELEASED — 0.1.0 | Developer source; not a customer application | Observer |
| LP Source Audit Inventory | RELEASED — 0.1.0 | Developer source; not a customer application | Observer |
| HMS Expedition Verifier | IN DEVELOPMENT — 0.2.0 | Public developer source; private Windows candidate; no customer download | Observer |
| Corpus Manifest Verifier | RELEASE CANDIDATE — 0.1.0-rc.1 | Developer source and private qualification package; no customer download | Observer |
| Public GP29 Calculator | RELEASED — 0.1.1 | Public Windows desktop/CLI download with approved manifest and checksums | Observer |
| Advanced GP Laboratory | PLANNED | No service | Cartographer |
| Liber Runtime Beta | IN DEVELOPMENT | Local developer core only; no hosted service | Navigator |
| GP Solver | PLANNED | No service | Admiral |
| Batch Experiment Engine | PLANNED | No service | Navigator |
| Socket/API Integration Layer | PLANNED | No service | Admiral |
| Add-on and Plugin SDK | PLANNED | No package | Admiral |

The validator and source-audit inventory were released in `v0.1.0` specifically as developer tools. They require CPython and are not customer-ready applications. GP29 v0.1.1 is the first released customer-ready Windows instrument; its shared Runtime core remains available as developer source. Expedition 001 remains closed until its packaged verifier passes the customer release gate.

`PLANNED` is not availability. Status and release channel are separate. Access levels describe the intended destination; delivery modes describe packaging. Every contract now declares inputs, outputs, authority class, evidence scope, capabilities, offline/network/privacy behavior, test vectors, self-test, ordinary-user acceptance, limitations, release gate, and human approval. See the [Distribution and User Experience Standard](../docs/DISTRIBUTION_STANDARD.md). `customer_ready: true` requires an actual tested user delivery, not merely public source.

Authority classes are `REFERENCE`, `CALCULATION`, `PROVENANCE`, `STRUCTURAL_ANALYSIS`, `EXPERIMENTAL`, `SOLVER`, and `VERIFICATION`. AEGIS may explain an authoritative instrument result; it may not invent or silently elevate one.
