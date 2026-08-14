# Corpus Manifest Verifier 0.1.0-rc.1 UAT

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
4. Run `HMS-Corpus-Verifier-CLI.exe demo-self-test`; require all five cases to pass.
5. Run `HMS-Corpus-Verifier.exe --self-test`; require exit code 0.
6. Open the desktop application normally. Confirm the canonical manifest is preselected and the interface explains that verification is local and read-only.
7. Select the packaged GOOD folder. Require PASS and two verified files.
8. Select ALTERED, MISSING, and EXTRA in turn. Require a clear FAIL and the correct finding in the file table.
9. Confirm the TRAVERSAL manifest is rejected, not followed.
10. Run `canonical-info`; require 75 files and canonical manifest digest `d11ef54e113d92cc5fd86976709d0ece188f09c7ce95fcc8d0fdb140c685b009`.
11. If the tester legally holds the canonical set, verify its folder in strict mode. Require 75 verified and zero altered, missing, unsafe, or extra files.
12. Export a report. Confirm it opens as JSON, validates, and contains no local corpus-root path.
13. Confirm the tool makes no network request and does not alter corpus files.
14. Ask the tester to explain in their own words what PASS means. Accept only byte identity—not authenticity, ownership, transcription correctness, or a solve.

## Record

- Tester:
- Date/time and timezone:
- Windows edition/build and architecture:
- Candidate filename:
- Candidate SHA-256:
- ZIP member checksums: PASS / FAIL
- CLI five-case self-test: PASS / FAIL
- GUI self-test: PASS / FAIL
- GUI ordinary-user flow: PASS / FAIL
- Canonical identity inspection: PASS / FAIL
- Canonical local-set check: PASS / FAIL / NOT AVAILABLE
- Export/privacy check: PASS / FAIL
- Defender or equivalent scan result:
- Problems observed:
- Tester decision: ACCEPT / REJECT
- Signature or durable approval reference:

Any failure requires a new candidate version or documented disposition. Approval applies only to the exact recorded digest.
