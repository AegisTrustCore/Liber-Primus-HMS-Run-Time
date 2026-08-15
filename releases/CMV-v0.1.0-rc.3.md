# HMS Corpus Manifest Verifier 0.1.0-rc.3

Status: **RELEASE CANDIDATE — NOT APPROVED FOR PUBLIC DISTRIBUTION**

Candidate package: `HMS-Corpus-Verifier-v0.1.0-rc.3-Windows-x64-portable.zip`

SHA-256: `dc0366e6c506a02ad12f5846d373d671242518f778dedc9706b00400ed562125`

## Changes from rc.2

- Adds multi-file selection for declared corpus pages.
- Resolves selected files to one safe shared manifest root.
- Rejects undeclared files, ambiguous mappings, duplicate selections, and mixed roots.
- Makes selection scope explicit while continuing to verify every manifest entry; selecting one page can never produce a misleading partial-corpus PASS.

The verification report contract and meaning of PASS are unchanged. PASS establishes declared byte identity only, not historical authenticity, rights, transcription correctness, translation, or a Liber Primus solution.

Two local clean builds were byte-identical, and two independent GitHub Windows workflow runs passed reproduction and exact packaged-interface qualification. The exact package passed internal checksums, both packaged self-tests, all five synthetic cases, strict verification of the bound 75-page local set, the focused 15-test verifier/package suite, and Microsoft Defender scanning. Clean-environment human UAT and explicit owner approval remain required.
