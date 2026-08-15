# Expedition 001 — The Evidence Ledger

Status: **PRACTICE PREVIEW — CAMPAIGN CLOSED**

Difficulty: **Deckhand / beginner**

Access: **Observer / free GitHub**

Material: **synthetic method-training puzzle**

Evidence ceiling: **TRAINING ONLY — NO LIBER PRIMUS RESEARCH CLAIM**

> If you opened this page and did not know what to do, start with the five-minute route immediately below. You do not need Cicada knowledge, runes, cryptography, or HMS software.

> **The signal is not the answer. The record of how you verified it is.**

## Your mission in one sentence

Classify five fictional research log entries, extract one character from each classification label, join those characters into a five-letter answer, and check it with the official verifier when the campaign opens.

## Five-minute start

1. Read log entry 1.
2. Choose the one vocabulary label that describes the **state of its evidence**.
3. Repeat for entries 2–5. No chosen label repeats.
4. Remove spaces, hyphens, and underscores from each chosen label and write it in uppercase.
5. From labels 1–5, take characters at positions `2, 3, 11, 6, 7` respectively.
6. Join the five extracted characters in log order.
7. Check the answer with the official verifier after the campaign opens. Verification is unavailable while the campaign is closed.

The answer is exactly five letters. The character positions are **1-based**, so position 1 means the first character.

## Harmless worked example

Suppose a different practice log were labeled `KNOWN_CONTROL` and asked for character position 1:

```text
KNOWN_CONTROL → KNOWNCONTROL → K
```

Use the same normalization and extraction process on the real five logs. This example is not one of the real extraction instructions.

## The five log entries

Choose the most precise vocabulary label for each entry.

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

## Fill-in worksheet

| Log | What happened? | Your label | Normalized label | Position | Extracted character |
|---:|---|---|---|---:|---|
| 1 | Repeatable relation; no message |  |  | 2 |  |
| 2 | Earlier interpretation withdrawn |  |  | 3 |  |
| 3 | Declared family failed its gate |  |  | 11 |  |
| 4 | Previously known text recreated |  |  | 6 |  |
| 5 | Proposed but not run |  |  | 7 |  |

If the signal fades, open the [progressive public hints](HINTS.md). Reveal only one signal at a time; each one states its practical instruction directly.

## Check your answer

Planned command-line route after the official HTTPS service is approved:

```bash
python scripts/verify_challenge.py YOUR_ANSWER
python scripts/verify_challenge.py --json --output receipt.json YOUR_ANSWER
```

The public client will send the submission to the rate-limited official HTTPS verification service and receive a signed, non-plaintext PASS/FAIL receipt. No answer or answer digest is shipped in public metadata or binaries. The service must suppress request-body logging, and the client must disclose the network request before the campaign opens.

The prior offline Windows candidate failed its solution-leak audit because a five-letter digest is enumerable. It will never be released. The replacement client/service design is under development and there is **no public download yet**.

## What this puzzle teaches

The important result is not merely the five-letter answer. The Expedition teaches why HMS distinguishes:

- a repeatable structure from readable plaintext;
- a correction from deletion of inconvenient evidence;
- a bounded failed family from “nothing can work”;
- a known control from a new discovery;
- an untested hypothesis from a verified result.

## What this puzzle is not

The scenarios are fictionalized training records. They are not Liber Primus source evidence, a Cicada clue, a translated page, or a claim about an active HMS route.

## Campaign state

The puzzle is visible so its clarity and tooling can be reviewed, but the formal campaign is closed. No timed hint schedule, badge, submission collection, or public solution release has begun. The challenge manifest is authoritative.

## Fair-release promise

Tiered material may teach the method sooner or provide a better worksheet and validation context, but it will not introduce a different answer. When the campaign eventually closes after launch, the complete solution and reasoning will be added to GitHub for everyone.
