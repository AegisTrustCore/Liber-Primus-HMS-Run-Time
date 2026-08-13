# HMS Instrument Registry

The machine-readable registry is [`manifest.json`](manifest.json). It is the authoritative public answer to “does this tool exist yet, and how can it actually be used?”

| Instrument | Status | Delivery reality | Intended access |
|---|---|---|---|
| Public Record Validator | RELEASED — 0.1.0 | Developer source; not a customer application | Observer |
| LP Source Audit Inventory | RELEASED — 0.1.0 | Developer source; not a customer application | Observer |
| HMS Expedition Verifier | IN DEVELOPMENT | GUI/CLI portable package being qualified | Observer |
| Corpus Manifest Verifier | IN DEVELOPMENT | No download | Observer |
| Public GP29 Calculator | INTERNAL TESTING | Developer source only; no customer download | Observer |
| Advanced GP Laboratory | PLANNED | No service | Cartographer |
| Liber Runtime Beta | IN DEVELOPMENT | Local developer core only; no hosted service | Navigator |
| GP Solver | PLANNED | No service | Navigator |
| Batch Experiment Engine | PLANNED | No service | Navigator |
| Socket/API Integration Layer | PLANNED | No service | Admiral |
| Add-on and Plugin SDK | PLANNED | No package | Admiral |

The validator and source-audit inventory were released in `v0.1.0` specifically as developer tools. They require CPython and are not customer-ready applications. The shared GP29/Runtime core is runnable as developer source but remains in internal testing; GP29 is still held for a separate customer release, and Expedition 001 remains closed until its packaged verifier passes the customer release gate.

`PLANNED` is not availability. Access levels describe the intended destination; delivery modes describe packaging. See the [Distribution and User Experience Standard](../docs/DISTRIBUTION_STANDARD.md). `customer_ready: true` requires an actual tested user delivery, not merely public source.
