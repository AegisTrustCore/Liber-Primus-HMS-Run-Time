# E1606 — Page 32 signed-displacement reversal holdout

Pair the sixteen generator positions with the sixteen source-order 109-rune blocks. Interpret only the final two negative displacements as instructions to reverse their blocks. Train a first-order GP29 transition model on blocks 1–14 and score `DD`, `DR`, `RD`, and `RR` on blocks 15–16 without language scoring. Pass requires `RR` to rank first and its margin to exceed the reverse-both margin for every adjacent-pair leave-out control.
