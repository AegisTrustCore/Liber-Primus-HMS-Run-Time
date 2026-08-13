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

GP29 is the first planned executable slice and will receive a separate public release after the foundation. Endeavour Lite and Liber Runtime begin as interface contracts around that core; their status remains planned until runnable code exists.
