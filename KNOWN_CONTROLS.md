# Known Controls

Known controls are material whose target result was already available independently of the HMS experiment. They are essential for testing implementation behavior, but they are not HMS discoveries.

## Published controls

[`RES-0011`](research/results/RES-0011/README.md), released in [`RSET-0004`](research/runsets/RSET-0004/START-HERE.md), records two established terminal controls:

- Page 73: the segment-wide family ranks the established sequential-prime/totient F-pause operator first.
- Page 74: the same family ranks direct GP first.

Each control exceeds all 500 retained full-family shuffles in token and vocabulary measures. This validates the bounded Runtime behavior; it is not an HMS-originated translation of either page.

## Candidates awaiting public packaging

| Candidate | Reported control behavior | What it can establish | What it cannot establish |
|---|---|---|---|
| E143-E145 | Held-out recovery of declared F decisions and GP tokens on solved LP1 pages | The disclosed decoder path behaves as reported on those frozen controls | That the decoder solves an unsolved LP2 page |
| E156-E160 follow-on | E156 segment-frame structure and E159 terminal controls are published; operation-selector and transfer questions remain | A separately declared follow-on may test transfer or selection | That published control success identifies unknown plaintext elsewhere |

## Publication requirements

Each additional control package must include canonical input provenance, hashes, the complete tested operator family, runnable code, expected output, actual output, and a clean-environment replay. Page numbering and primary-source provenance must be reconciled before a new control is called canonical.
