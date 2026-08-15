# HMS Corpus Manifest Verifier 0.1.0-rc.2

Status: **RELEASE CANDIDATE — NOT APPROVED FOR PUBLIC DISTRIBUTION**

Candidate package: `HMS-Corpus-Verifier-v0.1.0-rc.2-Windows-x64-portable.zip`

SHA-256: `ee379e1f9fc0f3601833161202aae9f2118deda53fad309478336932d8d88ba9`

## Changes from rc.1

- Keeps the window responsive while hashing a corpus.
- Shows manifest identity, file count, declared size, and canonical digest before verification.
- Adds All, Problems only, and Verified only filters plus filename/status search.
- Adds sortable findings, expected/actual digests, color-coded outcomes, and selected-row copying.
- Runs and reports all five packaged controls from the GUI self-test.
- Warns explicitly before non-strict verification.
- Adds safer report filenames, report-digest copying, privacy confirmation, and keyboard shortcuts.

The verification contract and meaning of PASS are unchanged. PASS establishes declared byte identity only. It does not establish historical authenticity, redistribution rights, transcription correctness, translation, or a Liber Primus solution.

## Qualification state

Two local clean builds were byte-identical. The exact package passed internal checksum verification, both packaged self-tests, all five synthetic cases, canonical identity inspection, strict verification of the bound 75-page local set, privacy inspection, the complete 75-test source suite, and Microsoft Defender scanning.

Clean-environment ordinary-user UAT and explicit owner approval remain required. This candidate is retained for review and must not be presented as a public release.
