# GP29 Calculator v0.1.1 usability scope

Status: **RELEASE CANDIDATE**

This is a usability revision of the deterministic GP29 calculator. It does not change the frozen 29-rune table, prime assignments, registers, aggregate formulas, or claim boundary from v0.1.0.

## Added

- An English-letter input mode that maps A through Z one character at a time.
- A visible, selectable 29-row Gematria Primus alphabet in the desktop calculator.
- Exact insertion of either the selected sound token or rune.
- Plain-language input-mode names and an explanation of each mode.
- A confirmation before alphabet insertion clears input from an incompatible mode.
- A results dashboard with headline totals, normalized sequences, aggregate registers, and a per-rune table.
- Raw JSON and diagnostics in a secondary tab instead of the default reading path.

## Input distinction

English-letter mode is recommended for ordinary words. It never joins adjacent characters:

```text
TH -> T + H
THING -> T + H + I/J + N + G
```

Latin-sound mode preserves the v0.1.0 longest-alias rule:

```text
TH -> TH
THING -> TH + NG/ING
```

Explicit-token mode remains the authoritative way to declare an exact segmentation. Rune mode accepts the canonical Unicode runes.

## Unchanged boundary

GP29 calculates declared values. It does not infer language, choose a key or route, rank candidates, translate Liber Primus, or establish a solve claim.

## Release rule

This revision is a new release subject. The qualified v0.1.0 ZIP and its pending UAT record do not approve v0.1.1. The exact v0.1.1 candidate must be rebuilt, qualified, tested by an ordinary user, and explicitly approved before publication.
