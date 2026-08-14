# GP29 Calculator v0.1.0 frozen scope

Status: **FROZEN**

This contract defines the complete GP29 v0.1.0 product. Features outside it must wait for v0.1.1, v0.2.0, or the Advanced GP Laboratory.

## Product promise

GP29 calculates declared Gematria Primus values. It does not decode, simplify, translate, score, rank, or solve Liber Primus.

## Included

### Input

- typed continuous Latin input using the documented deterministic longest-alias rule;
- explicit separated GP29 sound tokens;
- the 29 canonical Unicode runes; and
- UTF-8 text files through the desktop and CLI interfaces.

### Calculation

For each rune at canonical zero-based index `i` with assigned prime `p`:

```text
L = i
R = (-i) mod 29
prime = p
N = p mod 29
Q = floor(p / 29)
prime = 29Q + N
```

The result includes rune count, the sums of `L`, `R`, prime, `N`, and `Q`, and the documented `mod 29` or `mod 4` aggregates. `gp_sum` and `gp_sum_mod29` remain compatibility aliases for the prime sum fields.

### Output and verification

- readable desktop result;
- deterministic JSON export;
- canonical JSON result digest;
- embedded frozen test vectors;
- desktop and CLI self-tests;
- reproducible Windows x64 portable package; and
- SHA-256 checksums and a release manifest.

### Interfaces

- Windows 10/11 x64 standalone desktop application; and
- Windows 10/11 x64 standalone command-line application.

Neither interface requires Python, an HMS account, a network connection, or telemetry.

## Excluded

- automatic plaintext or language interpretation;
- LP page solving, key selection, transformation selection, or route selection;
- simplification or automatic segmentation chosen by language scoring;
- Gematria hunting, parameter sweeps, batch experimentation, or candidate ranking;
- AI or remote services;
- Corpus Manifest Verifier packaging; and
- Patreon authentication, quotas, sockets, APIs, or plugins.

## Change rule

Any change to code, interface text, documentation inside the package, executables, checksums, archive contents, or manifest creates a new release candidate. The exact artifact accepted by an ordinary user must be the exact artifact approved and released.
