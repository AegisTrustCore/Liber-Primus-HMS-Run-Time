# Research Station UX Standard

This is the long-term interface boundary for Endeavour Lite and the mature AEGIS Trust Core research station. It is direction, not a claim that these screens or services exist today. The complete authority and maturity boundary is in the [Admiral Research Station Contract](ADMIRAL_RESEARCH_STATION_CONTRACT.md).

Reusable components, result layout, visual language, and authority badges are frozen in the [HMS Shared Design System](HMS_DESIGN_SYSTEM.md).

## Researcher-facing model

The application presents a small set of stable work areas inside a four-part frame: navigation, central workspace, contextual rail, and bottom Job Drawer.

- **Bridge:** home, status, and next actions
- **Atlas:** corpora, sources, pages, and immutable imports
- **Laboratory:** interactive methods and instruments
- **Voyages:** experiments, runs, comparisons, and recovery
- **Evidence:** claims, controls, negatives, corrections, and provenance
- **Trust:** ProofLink, ProofLock, verification, and authorization boundaries
- **Shipyard:** qualified tools and plugins
- **Observatory:** health and activity

Internal HMS components do not each become navigation items. System detail is progressively disclosed through Standard, Research, and Developer complexity levels.

## Screen contract

Every screen must answer:

1. What object am I looking at?
2. What can I do here?
3. What is its status?
4. What evidence supports it?
5. What should I do next?

The immediate hierarchy contains one primary action and no more than two secondary actions.

## Truth display

The interface uses explicit epistemic states such as `OBSERVATION`, `HYPOTHESIS`, `CANDIDATE`, `REPRODUCED`, `VERIFIED`, `BLOCKED`, `REFUTED`, `STALE`, and `RETRACTED`. It does not display invented truth percentages.

AEGIS assistance remains contextual and permission-bounded. It may ask, plan, explain, compare, challenge, or research, but evidence authority remains visible and the researcher remains in control. It invokes authoritative instruments rather than inventing their outputs.

## Shared Result shell

Every instrument presents `OBJECT`, `STATUS`, `INPUT`, `OUTPUT`, `INTERPRETATION`, `LIMITATIONS`, `PROVENANCE`, and `EXPORT`. Candidate-generation interfaces preserve raw and failed outputs and use **AUTO EXPLORE**, never AUTO SOLVE.
