# Permanent ID Registry

[`id-reservations.json`](id-reservations.json) is append-only in meaning. An ID remains reserved after its object is superseded, retracted, retired, or removed from active indexes. It must never be assigned to a different object.

Pull requests that add a canonical HMS object must reserve its ID in the same change. Renumbering before the first public release is recorded as a migration; after `v0.1.0`, published IDs are immutable.

Canonical prefix meanings are frozen in [the object model](../OBJECT_MODEL.md), including the distinct `EXP` experiment, `XPD` Expedition, `RC` release-candidate, and `ENV` environment namespaces.
