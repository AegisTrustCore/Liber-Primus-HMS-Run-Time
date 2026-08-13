# Page 73 Audit Dossier

Status: **SOURCE TRIAGE COMPLETE; PROVENANCE AND REPRODUCTION PENDING**
Priority: **3**

The source workspace contains Page 73 terminal-language, payload, mask, multihash, BLAKE-512, hash-chain, HMAC, structured-verifier, and reconciliation branches.

The audit must determine which artifacts are:

- Observations about page structure or representation
- Candidate interpretations
- Deterministic encodings or checksums
- Cryptographic verification hypotheses
- Reproductions of earlier candidates
- Negative results or eliminated branches

No Page 73 translation claim is currently published as verified in this repository.

## First triage boundary

Page 73 contains a known solved plaintext used inside HMS as a positive control. That known control must be distinguished from a new HMS-originated recovery.

The reviewed `E952` artifact linked a Page 72-derived selector to the known Page 73 terminal control, but explicitly stated that it did not recover the printed SHA-512 preimage or identify the page described by the plaintext. It also recorded `plaintext_recovered: false` for the experiment itself.

Later E159 material reports replaying the known terminal plaintext with a prime/totient F-pause transform and ranking that operator first among six controls. This is a positive-control candidate, not a new plaintext recovery.

## Required correction

An earlier experiment branch interpreted the printed hash object as selecting that transform. Later E256-E260/E258 analysis retracts the causal inference: the transform result may remain reproducible, but the printed hash was not shown to select it and the initializer provenance was not locally recovered.

An archive-level decoded-pages report also conflicts with later material about whether terminal text was verified in the primary source it reviewed. Corpus provenance and page numbering must be reconciled before the known control can be packaged as canonical.
