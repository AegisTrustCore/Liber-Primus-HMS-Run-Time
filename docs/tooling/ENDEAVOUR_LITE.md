# HMS Endeavour Lite — initial contract

Audience: Observer basic; Pilgrim and above when released

Status: **IN DEVELOPMENT — runnable `0.1.0-dev`, not publicly released**

Endeavour Lite will be the local, reduced HMS workstation:

- selectable 29-rune reference and explicit-token handoff;
- GP29 rune/token lookup and sums;
- paste-or-file input with explicit provenance fields;
- a bounded GP29 comparison experiment with a predeclared hypothesis and success gate;
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

The `0.1.0-dev` slice now provides the unified desktop and CLI shell, private local project create/open workflow, immutable Run storage, shared `HMS_RESULT_ENVELOPE_V1`, selectable Rune Workbench, GP29 execution, corpus verification handoff, one bounded declared GP29 batch experiment, explicit JSON export, history inspection, and a metadata-only 75-page LP Atlas. It does not copy corpus images into projects.

Automated Windows development-package qualification now covers deterministic rebuilds, internal checksums, packaged GUI/CLI self-tests, project creation, saved calculation, result listing/export, and the bundled 75-file identity manifest. Still required before release: integrate the approved secure Expedition client, improve project settings and recovery behavior, complete clean-environment human UAT, and approve the exact package. Annotations, Regions, page rendering, general Experiment Builder, Auto Explore, AEGIS, sockets, accounts, and hosted synchronization remain later increments.

Developer start:

```text
python scripts/endeavour_lite_app.py
python scripts/endeavour_lite_app.py --self-test
python scripts/endeavour_lite.py --help
python scripts/build_endeavour_lite_windows.py
```
