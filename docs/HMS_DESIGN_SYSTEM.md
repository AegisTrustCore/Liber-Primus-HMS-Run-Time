# HMS Shared Design System

Status: **ARCHITECTURE CONTRACT; NAUTICAL DESKTOP FOUNDATION IMPLEMENTED**

Every standalone instrument, Endeavour Lite screen, Runtime workspace, and member-facing research build uses the same design language and object semantics.

## Component inventory

The shared desktop foundation now provides a common Aegis/HMS masthead, nautical palette, authority badges, typography, controls, tables, notebooks, and text surfaces through `hms_tools/ui_theme.py`. The longer-term component library will provide:

- `AppShell`, `Sidebar`, `TopBar`, `ContextRail`, and `JobDrawer`;
- `ObjectHeader`, `StatusBadge`, and `EvidenceBadge`;
- `RunTable`, `ResultTable`, and `ArtifactTable`;
- `FilePicker`, `PageViewer`, `RuneInspector`, and `NumberInspector`;
- `ExportMenu`, `TrustInspector`, `AegisPanel`, and `CommandPalette`.

Products may compose these components differently, but they must not fork evidence labels, authority language, provenance display, or release status meanings.

## Result shell

Every instrument output presents these sections in order:

1. Object
2. Status
3. Input
4. Output
5. Interpretation
6. Limitations
7. Provenance
8. Export

The instrument's authority class is visible beside its status. For example, GP29 says `CALCULATION`; Corpus Manifest Verifier says `PROVENANCE`; Expedition Verifier says `VERIFICATION`; Auto Explore says `EXPERIMENTAL`; a future solver says `SOLVER`.

## Interaction and visual language

- Dark-first, professional research station.
- Restrained cyan for active/verified interface state and brass for HMS identity.
- Plain-language subtitles accompany nautical names.
- One primary action and no more than two secondary actions per immediate hierarchy.
- Standard, Advanced, and Developer views change information density, not evidence truth.
- Keyboard navigation, readable focus, scalable type, and non-color status cues are mandatory.
- Decorative “cyberpunk” density must never obscure object, status, provenance, limitations, or next action.

Candidate-generation actions use **Explore**, **Run**, or **Auto Explore**. They do not use **Solve** unless the instrument's declared authority class is `SOLVER`, and even then the output remains a candidate until evidence review.
