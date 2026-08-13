# Corrections and Retractions

Corrections are permanent parts of the public evidence history. They are linked to the affected claim rather than silently replacing it.

## COR candidate — Page 73 visible-hash selector

Status: **PUBLIC PACKAGING PENDING**

An earlier experiment branch interpreted a printed Page 73 hash object as selecting a prime/totient transform. Later E256-E260/E258 analysis narrows that conclusion:

- The transform may still reproduce already-known terminal plaintext as a positive control.
- The printed hash object was not shown to select that operation.
- The initializer provenance was not locally recovered.
- The retained transform replay must not be presented as a causal visible-hash selector or as new plaintext recovery.

The formal correction record will receive a permanent `COR-` identifier when the original and superseding evidence are packaged together.
