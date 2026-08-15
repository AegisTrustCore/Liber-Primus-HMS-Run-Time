# HMS Endeavour Runtime Environment v1 — UAT and release gate

Release candidate: `1.0.0-rc.1`

Artifact: `HMS-Endeavour-Runtime-v1.0.0-rc.1-Windows-x64-portable.zip`

SHA-256: `294fcef812a54f2329d52f0b1a22dfecf2ed260a50ded25da7d2823b07ddc9ab`

Automated qualification completed on Windows 10, August 15, 2026:

- 79 repository tests: PASS
- public-record validation: PASS
- deterministic package build and internal `SHA256SUMS`: PASS
- extracted CLI self-test: PASS
- extracted GUI self-test: PASS
- project creation and GP29 Result: PASS
- Note, normalized Region, and Page Set persistence: PASS
- research-object listing and explicit export: PASS
- project audit and index rebuild: PASS
- privacy-safe backup creation: PASS
- Microsoft Defender custom scan: COMPLETED with Defender enabled

## Human UAT still required

Test this exact SHA-256 on a clean Windows account before public release:

1. Extract the ZIP and confirm `SHA256SUMS`.
2. Launch `HMS-Endeavour-Runtime.exe`; confirm all tabs render without clipping at 100% and 150% display scaling.
3. Create a project in an empty folder and reopen it.
4. Link a local 75-page corpus folder, select a page in LP Atlas, and open the page.
5. Save a Bookmark, multi-page Page Set, Note, normalized Region, Evidence object, and Claim object.
6. Run two GP29 calculations, select both Results, save their structural comparison, and inspect evidence labels and limitations.
7. Verify the corpus, inspect history, export one Result, and export one research object.
8. Run project audit; confirm `PASS` and correct Run/Result/object counts.
9. Create a safe backup. Inspect the ZIP and confirm it contains no corpus images, exports, or local corpus-root path.
10. Confirm Expedition is fail-closed and no submission can be sent while the campaign is closed.
11. Confirm no account, telemetry, silent upload, automatic solving, or unreviewed truth promotion is present.

Record tester, machine, Windows version, display scaling, timestamp, artifact SHA-256, each step’s result, and any defect. Public promotion requires all steps to pass and owner approval bound to this exact artifact hash.
