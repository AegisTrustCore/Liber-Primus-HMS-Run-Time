# Corpus Manifest Verifier 0.1.0-rc.3 UAT

Status: **PENDING HUMAN EXECUTION**

This checklist qualifies one exact Windows ZIP. Record the candidate filename and SHA-256 before testing. Do not substitute a rebuilt package during the run.

## Environment

- Fresh or representative Windows 10/11 x64 user environment
- No Python installation required
- Tester is not the person who prepared the candidate, when practical
- Network may remain disconnected after acquiring the package

## Acceptance procedure

1. Compare the ZIP SHA-256 with the candidate record and confirm all `SHA256SUMS` members.
2. Run `HMS-Corpus-Verifier-CLI.exe demo-self-test`; require GOOD, ALTERED, MISSING, EXTRA, and TRAVERSAL to pass their expected controls.
3. Run `HMS-Corpus-Verifier.exe --self-test`; require exit code 0.
4. Open the desktop application. Confirm the canonical manifest is preselected and the authority banner says PROVENANCE, OFFLINE, and READ-ONLY.
5. Confirm the preview reports `LP-75-IMAGES` v1.0.0, 75 files, and digest `d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009`.
6. Use **Select page files** and choose one declared page. Require the shared corpus root to load and the interface to state `1 of 75`; verification must still check all 75 declared files.
7. Repeat with several declared pages. Require one shared root and the correct selection count.
8. Attempt a file outside the manifest and selections from different roots. Require rejection without changing the current corpus root.
9. Select the packaged GOOD folder. Require PASS and two verified files; confirm the window remains responsive.
10. Select ALTERED, MISSING, and EXTRA in turn. Require clear FAIL summaries and correct color-coded findings.
11. Confirm Problems only, Verified only, Search, sortable headings, Copy selected, and Copy report digest behave correctly.
12. Confirm the TRAVERSAL manifest is rejected, not followed.
13. Disable strict mode, confirm the warning appears, then cancel. Repeat and continue; confirm the report records `strict: false`.
14. Run `canonical-info`; require 75 files and the canonical manifest digest above.
15. If the tester legally holds the canonical set, verify it in strict mode. Require 75 verified and zero altered, missing, unsafe, or extra files.
16. Export a report. Confirm the suggested filename is descriptive, JSON validates, the digest verifies, and no local corpus-root path appears.
17. Confirm the tool makes no network request and does not alter corpus files.
18. Exercise Ctrl+O, Ctrl+Shift+O, Ctrl+Enter, Ctrl+S, Ctrl+F, and F1.
19. Ask the tester what PASS means. Accept only byte identity, not authenticity, ownership, transcription correctness, or a solve.

## Record

- Tester:
- Date/time and timezone:
- Windows edition/build and architecture:
- Candidate filename and SHA-256:
- ZIP member checksums: PASS / FAIL
- CLI and GUI self-tests: PASS / FAIL
- Page-file selection and rejection controls: PASS / FAIL
- GUI ordinary-user flow and responsiveness: PASS / FAIL
- Filter/search/sort/copy controls: PASS / FAIL
- Canonical identity inspection: PASS / FAIL
- Canonical local-set check: PASS / FAIL / NOT AVAILABLE
- Export/digest/privacy check: PASS / FAIL
- Strict-mode warning and shortcuts: PASS / FAIL
- Defender or equivalent scan result:
- Problems observed:
- Tester decision: ACCEPT / REJECT
- Signature or durable approval reference:

Any failure requires a new candidate version or documented disposition. Approval applies only to the exact recorded digest.
