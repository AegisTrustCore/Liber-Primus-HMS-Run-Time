# Research Methodology

## Core rule

HMS publishes the smallest claim justified by the evidence. It does not turn a promising output into a corpus-wide conclusion.

## Evidence states

| State | Meaning |
|---|---|
| OBSERVATION | A recorded property or event; no causal or decoding conclusion |
| HYPOTHESIS | A testable explanation or proposed method |
| EXPERIMENTAL | A method was executed; interpretation remains under evaluation |
| PROVISIONAL | Evidence supports a bounded claim but release requirements are incomplete |
| REPRODUCED | A documented rerun produced the same declared output |
| VERIFIED | The bounded public claim passed the full release gate |
| UNSUPPORTED | Available testing did not support the claim |
| REFUTED | Evidence contradicts the precisely stated claim within its tested scope |
| RETRACTED | A previously published claim was withdrawn |

## Verified-result gate

A result may be labeled `VERIFIED` only when:

1. The claim is narrow and unambiguous.
2. The exact source input and version are identified and hashed.
3. All material operations, parameters, keys, and human choices are disclosed.
4. The result can be rerun from the documented procedure.
5. A clean rerun produces the declared output.
6. Relevant positive and negative controls are documented.
7. Assumptions, limitations, and alternative explanations are recorded.
8. The conclusion does not exceed the evidence.
9. The release package contains enough public material for independent verification.
10. Publication is explicitly approved.

Reproduction proves repeatability of the procedure. It does not by itself prove that the interpretation is correct, unique, intentional, or a translation.

## Research object chain

HMS maintains traceability across:

```text
OBSERVATION → HYPOTHESIS → EXPERIMENT → RESULT → REPRODUCTION → REVIEW → RELEASE
```

Permanent identifiers use these prefixes:

- `OBS` — observation
- `HYP` — hypothesis
- `EXP` — experiment
- `RES` — result
- `NEG` — negative result
- `RR` — research report
- `PL` — ProofLock
- `COR` — correction
- `RET` — retraction

## Negative results

A public negative-result record must state the target claim, why the test was relevant, exact parameters, success criterion, observed outcome, and how broadly the rejection applies. “Did not work” is not a sufficient record.

## Corrections

Published history is preserved. Corrections and retractions link to the original record, explain the cause, and identify any replacement. Files are not silently rewritten to erase material research changes.
