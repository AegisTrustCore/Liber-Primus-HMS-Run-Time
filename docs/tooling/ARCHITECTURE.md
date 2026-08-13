# HMS tool architecture — first implementation boundary

The tool family will share one versioned research core while exposing progressively larger interfaces.

```text
GP29 data + corpus manifests + evidence schemas
                     |
              deterministic core
             /        |         \
   GP29 Calculator  Endeavour Lite  Liber Runtime
       public CLI    local public UI  hosted workspace
                                      |
                              jobs, sockets, add-ons
```

## Rules

1. The deterministic core contains mappings, transforms, parsers, hashes, and result serialization—not membership or marketing logic.
2. Every experiment records input identity, operation order, parameters, output digest, software version, and evidence label.
3. A readable-looking output is a candidate, not a verified result.
4. Endeavour Lite must remain usable locally without an HMS account.
5. Runtime entitlement checks remain server-side; no private dataset or secret ships in the public client.
6. Sockets and add-ons consume the same job/result contract as the UI.
7. Historical Cicada signatures and future HMS release signatures occupy separate trust namespaces.

## First implementation

The first executable slice now lives in `hms_tools.gp29` and `hms_tools.runtime`:

- one frozen 29-rune/prime table;
- strict rune and separated-token parsers;
- deterministic calculation and result digests;
- a versioned local job/result contract;
- a reference in-memory queue; and
- the developer CLI at `scripts/hms_runtime.py`.

The same core drives the GP29 desktop application, standalone CLI, and reproducible Windows portable-package builder. RC1 is superseded; the frozen v0.1.0 contract is implemented in the RC2 source candidate. RC2 does not become a release candidate until it is built from merged `main`, and it cannot become public until the exact package passes security review, clean-machine ordinary-user acceptance, and human approval. Endeavour Lite and the hosted service will later wrap these contracts rather than reimplementing them.
