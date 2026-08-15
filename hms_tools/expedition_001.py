"""Public, non-solution guidance shared by Expedition 001 interfaces."""

from __future__ import annotations


CHALLENGE_ID = "XPD-0001"
VERSION = "0.3.0"

LOGS = (
    "A repeatable row/column relation survives, but produces no readable message.",
    "A later audit withdraws an interpretation while preserving the transform and output.",
    "A declared four-route family fails its checksum; no claim is made outside that family.",
    "A method recreates plaintext that was known before the experiment.",
    "An operation is proposed, but has not been run or falsified.",
)

VOCABULARY = (
    "VERIFIED_RESULT — passed the declared release gate",
    "STRUCTURAL — reproducible organization without a plaintext claim",
    "KNOWN_CONTROL — previously known material used to validate behavior",
    "HYPOTHESIS — testable proposal not yet established",
    "BOUNDED_NEGATIVE — declared family failed without universal impossibility",
    "CORRECTION — prior statement narrowed, repaired, or withdrawn",
)

STEPS = (
    "1. Classify each of the five logs with the most precise vocabulary label.",
    "2. Use each selected label once; one vocabulary label remains unused.",
    "3. Uppercase each label and remove spaces, hyphens, and underscores.",
    "4. Take 1-based characters 2, 3, 11, 6, and 7 in log order.",
    "5. Join the five characters and verify the five-letter answer with the official service.",
)

HINTS = (
    "Classify the state of the evidence, not the technique described.",
    "Ask: relation without plaintext; withdrawn interpretation; bounded failed family; previously known target; proposed but untested.",
    "No label repeats. None of the logs says a new claim completed a release gate, so that label is unused.",
    "Normalize before counting: BOUNDED_NEGATIVE becomes BOUNDEDNEGATIVE. Count from 1, not 0.",
)


def instructions_text(campaign_state: str = "CLOSED") -> str:
    state = campaign_state.strip().upper()
    campaign_line = (
        "Campaign state: OPEN; submit through the signed official verification service."
        if state == "OPEN"
        else "Campaign state: closed redesign preview; the verification service is not active."
    )
    sections = [
        "EXPEDITION 001 — THE EVIDENCE LEDGER",
        "Goal: classify five fictional logs, extract five characters, and verify the answer.",
        "",
        "LOGS",
        *(f"{index}. {value}" for index, value in enumerate(LOGS, 1)),
        "",
        "VOCABULARY",
        *VOCABULARY,
        "",
        "STEPS",
        *STEPS,
        "",
        campaign_line,
    ]
    return "\n".join(sections)


def hint_text(level: int) -> str:
    if level < 1 or level > len(HINTS):
        raise ValueError(f"Hint level must be between 1 and {len(HINTS)}.")
    return f"HINT {level}\n{HINTS[level - 1]}"
