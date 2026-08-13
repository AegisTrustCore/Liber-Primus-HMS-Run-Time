# HMS Endeavour Lite — initial contract

Audience: Observer / public

Status: In development; shared calculation core runnable, local UI pending

Endeavour Lite will be the local, reduced HMS workstation:

- GP29 rune/token lookup and sums;
- paste-or-file input with explicit provenance fields;
- deterministic transforms with visible parameters;
- result export as a portable JSON record;
- side-by-side input/output and diff views;
- local-only projects by default;
- an explicit preview of every object and metadata field before any submission leaves the device;
- canonical provenance IDs and deterministic environment manifests;
- no automated declaration that text is solved.

The first milestone wraps the GP29 calculator in a small local interface and exports the same structured result contract used by the Runtime.

The shared GP29 and Runtime job/result cores now exist, and GP29 has its own release-candidate desktop interface, file loading, JSON export, and Windows portable package. Endeavour Lite still requires its unified shell, page/corpus views, side-by-side experiment workspace, multi-instrument export workflow, and ordinary-user qualification before it can be called runnable or released.
