# HMS Endeavour Lite — initial contract

Audience: Observer basic; Pilgrim and above when released

Status: Planned; shared calculation core exists, unified application not started

Endeavour Lite will be the local, reduced HMS workstation:

- GP29 rune/token lookup and sums;
- paste-or-file input with explicit provenance fields;
- deterministic transforms with visible parameters;
- result export as a portable JSON record;
- side-by-side input/output and diff views;
- local-only projects by default;
- an explicit preview of every object and metadata field before any submission leaves the device;
- canonical provenance IDs and deterministic environment manifests;
- no automated declaration that text is solved.

## Version sequence

### v0.1 — unified public workstation

Navigation: Bridge, Project, Files, GP29, Corpus Verify, Runs, Results, and Settings.

Core workflows:

1. Create Project → select corpus → verify corpus → save a hash/reference-based project.
2. Enter text → GP29 → save Run → inspect Result → export JSON.
3. Open Run → inspect → reproduce → compare.

The local project layout uses `project.json`, a corpus reference, notes, Runs, Results, exports, and settings. It does not copy the full source corpus unless the researcher explicitly requests that behavior.

### v0.2 — visual research bridge

Add the LP page viewer, annotations, snips, Regions, basic PageSets, Run comparison, and HTML/TXT reports.

### v0.3 — Runtime shell

Add the basic Experiment Builder, contextual AEGIS rail, Trust Inspector, and instrument catalog.

The shared GP29 and Runtime job/result cores now exist, and GP29 v0.1.1 is released with its desktop interface, CLI, file loading, dashboard, JSON/CSV export, and Windows portable package. Endeavour Lite begins implementation after the Corpus Manifest Verifier reaches release candidate. It still requires its unified shell, local project format, page/corpus views, side-by-side experiment workspace, multi-instrument export workflow, and ordinary-user qualification before it can be called runnable or released.
