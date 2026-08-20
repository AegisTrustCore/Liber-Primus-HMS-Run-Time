# Tooling documentation

This directory records instrument architecture, scope boundaries, UAT protocols, security audits, and deployment gates.

## Current instruments

| Instrument | Design | Qualification material |
|---|---|---|
| GP29 Calculator | [GP29](GP29.md) | `GP29_SCOPE_*` and `GP29_UAT*` |
| Corpus Manifest Verifier | [Corpus Verifier](CORPUS_MANIFEST_VERIFIER.md) | `CORPUS_VERIFIER_UAT_*` |
| HMS Endeavour Lite | [Endeavour Lite](ENDEAVOUR_LITE.md) | [Runtime/Lite UAT](RUNTIME_V1_UAT.md) |
| HMS Endeavour Runtime Environment | [Member Runtime](LIBER_RUNTIME.md) | Private exact-package qualification remains outside GitHub |
| Expedition 001 | [Deployment gate](EXPEDITION_SERVICE_DEPLOYMENT_GATE.md) | [Solution-leak audit](EXPEDITION_001_SOLUTION_LEAK_AUDIT.md) |

The [tool architecture](ARCHITECTURE.md), [instrument registry](../../instruments/README.md), and [product manifest](../../products/manifest.json) are authoritative when descriptive documents disagree.

Historical UAT files are retained as evidence for their exact version. They do not approve later builds.
