# Public schemas

These JSON Schemas define HMS machine-readable contracts. They are validation rules, not evidence by themselves.

| Contract family | Schemas |
|---|---|
| Research evidence | `run-package`, `result-package`, `capsule-package`, `run-set`, `research-record` |
| Corpus and pages | `corpus-manifest`, `corpus-verification`, `page-record` |
| Runtime and projects | `hms-project`, `project-settings`, `research-object`, `runtime-job`, `runtime-result`, `result-envelope` |
| Products and tools | `product-manifest`, `instrument-manifest`, `hms-plugin-manifest` |
| Releases | `release-manifest`, `release-gate`, `release-state`, `environment-manifest` |
| Expeditions | `challenge-manifest`, `expedition-verification-receipt` |
| Governance | `id-registry`, `patreon-public-manifest`, `hms-object` |

Run `python scripts/validate_records.py` from the repository root to validate public records against these contracts.

