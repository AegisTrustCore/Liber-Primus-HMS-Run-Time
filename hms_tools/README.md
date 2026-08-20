# HMS deterministic core

This Python package contains the shared implementation used by public command-line tools, desktop applications, tests, and builders.

| Module group | Responsibility |
|---|---|
| `gp29.py` | Frozen Gematria Primus mapping and deterministic registers |
| `corpus_manifest.py` | Corpus identity creation and verification |
| `challenge_verifier.py`, `expedition_*` | Expedition client, receipt, service, and fail-closed verification contracts |
| `project.py`, `runtime.py` | Local projects, immutable research objects, jobs, Results, audit, and safe backup |
| `ui_theme.py` | Shared Aegis/HMS nautical desktop theme |

This package contains no Patreon entitlement logic and does not turn a calculation into a research claim. Public and member interfaces must preserve the evidence labels returned by the core.

