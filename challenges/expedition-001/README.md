# Expedition 001 — The Evidence Ledger

Status: **RELEASE CANDIDATE — NOT YET OPEN**  
Access: **Observer / free GitHub**  
Material: **synthetic method-training puzzle**

This expedition teaches the vocabulary used to separate a verified result from a control, unresolved idea, bounded negative result, or correction. The scenarios are fictionalized training records. They are not source evidence and do not assert a Liber Primus solution.

## The five log entries

Classify each entry with the most precise ledger label shown in the vocabulary below.

1. A repeatable relation between row and column positions survives a frozen transcription, but the method produces no readable message.
2. A later audit withdraws an earlier interpretation while preserving the reproducible transform and its raw output.
3. Four declared routes were run against frozen inputs and shuffled controls. None met the predeclared checksum; no claim is made about routes outside that tested family.
4. A method recreates plaintext that was independently known before the experiment and is used to confirm that the implementation behaves as expected.
5. An operation has been proposed, but its inputs and falsification test have not yet been run.

## Vocabulary

- `VERIFIED_RESULT` — the claimed result has passed the declared release gate
- `STRUCTURAL` — a reproducible relation or organization, without a plaintext claim
- `KNOWN_CONTROL` — previously known material used to validate a method
- `HYPOTHESIS` — a testable proposal that is not yet established
- `BOUNDED_NEGATIVE` — a declared test family failed its target without claiming universal impossibility
- `CORRECTION` — a prior statement is narrowed, repaired, or withdrawn

## Extraction

1. Write the five labels in log order.
2. Convert each label to uppercase and remove spaces, hyphens, and underscores.
3. Take the 1-based character at indices `2, 3, 3, 9, 1`.
4. Join the characters into a five-letter answer.

Verify locally without sending an answer anywhere:

```bash
python scripts/verify_challenge.py EXP-001 YOUR_ANSWER
```

The verifier normalizes the answer and compares its SHA-256 digest with the sealed digest in the public manifest. It stores nothing and makes no network request.

## Public clue 0

Every entry describes the **state of the evidence**, not the technique used to produce it. No selected label repeats, and one vocabulary label is unused.

## Fair-release promise

Tiered hints may explain the taxonomy sooner or provide structured worksheets, but they do not introduce a different answer. After the campaign window, the complete solution and reasoning will be added to GitHub for everyone.
