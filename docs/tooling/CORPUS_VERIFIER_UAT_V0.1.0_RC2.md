# Corpus Manifest Verifier 0.1.0-rc.2 UAT

Status: **PENDING HUMAN EXECUTION**

This checklist qualifies one exact Windows ZIP. Record the candidate filename and SHA-256 before testing. Do not substitute a rebuilt package during the run.

## Environment

- Fresh or representative Windows 10/11 x64 user environment
- No Python installation required
- Tester is not the person who prepared the candidate, when practical
- Network may remain disconnected after acquiring the package

## Acceptance procedure

1. Compare the ZIP SHA-256 with the candidate record.
2. Extract the complete ZIP into a new ordinary user folder.
3. Confirm `SHA256SUMS` matches every packaged member.
4. Run `HMS-Corpus-Verifier-CLI.exe demo-self-test`; require GOOD, ALTERED, MISSING, EXTRA, and TRAVERSAL to pass their expected controls.
5. Run `HMS-Corpus-Verifier.exe --self-test`; require exit code 0.
6. Open the desktop application normally. Confirm the canonical manifest is preselected and the authority banner says PROVENANCE, OFFLINE, and READ-ONLY.
7. Confirm the manifest preview reports `LP-75-IMAGES` v1.0.0, 75 files, and digest `d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009`.
8. Select the packaged GOOD folder. Require PASS and two verified files; confirm the window remains responsive.
9. Select ALTERED, MISSING, and EXTRA in turn. Require clear FAIL summaries and correct color-coded findings.
10. Confirm Problems only, Verified only, filename/status Search, sortable headings, and Copy selected behave correctly.
11. Confirm the TRAVERSAL manifest is rejected, not followed.
12. Disable strict mode, confirm the warning appears, then cancel. Repeat and explicitly continue; confirm the report records `strict: false`.
13. Run `canonical-info`; require 75 files and the canonical manifest digest above.
14. If the tester legally holds the canonical set, verify its folder in strict mode. Require 75 verified and zero altered, missing, unsafe, or extra files.
15. Export a report. Confirm the suggested filename is descriptive, the JSON validates, the report digest verifies, and no local corpus-root path appears.
16. Confirm Copy report digest places the exact `report_sha256` value on the clipboard.
17. Confirm the tool makes no network request and does not alter corpus files.
18. Exercise Ctrl+O, Ctrl+Shift+O, Ctrl+Enter, Ctrl+S, Ctrl+F, and F1.
19. Ask the tester to explain in their own words what PASS means. Accept only byte identity, not authenticity, ownership, transcription correctness, or a solve.

## Record

- Tester:
- Date/time and timezone:
- Windows edition/build and architecture:
- Candidate filename:
- Candidate SHA-256:
- ZIP member checksums: PASS / FAIL
- CLI five-case self-test: PASS / FAIL
- GUI five-case self-test: PASS / FAIL
- GUI ordinary-user flow: PASS / FAIL
- Responsive verification: PASS / FAIL
- Filter/search/sort/copy controls: PASS / FAIL
- Canonical identity inspection: PASS / FAIL
- Canonical local-set check: PASS / FAIL / NOT AVAILABLE
- Export/digest/privacy check: PASS / FAIL
- Strict-mode warning: PASS / FAIL
- Keyboard shortcuts: PASS / FAIL
- Defender or equivalent scan result:
- Problems observed:
- Tester decision: ACCEPT / REJECT
- Signature or durable approval reference:

Any failure requires a new candidate version or documented disposition. Approval applies only to the exact recorded digest.
