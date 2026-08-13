# Liber Runtime — initial contract

Audience: Navigator beta and above, with public verification surfaces

Status: Planned; architecture started

Liber Runtime will attach to HMS Endeavour as the persistent experiment environment. Its first contract includes:

- immutable corpus and input manifests;
- versioned operation pipelines;
- queued jobs with resource limits;
- complete parameter and seed capture;
- result, control, and negative-result ledgers;
- shareable public verification bundles;
- tier-aware workspaces without tier-dependent truth labels;
- future socket/API and add-on interfaces using capability-scoped tokens.
- private-by-default visibility with explicit `PRIVATE → PROJECT → GROUP → HMS_REVIEW → PUBLIC` transitions;
- separately enforced compute quotas for jobs, concurrency, runtime, family size, storage, and retention;
- full parameter-family retention so selected outputs preserve their search denominator;
- source-image, canonical, alternative, and user transcriptions as distinct immutable inputs.

The Runtime will not receive private Vault material by default, and an Admiral entitlement will not bypass evidence review or provenance controls.

Tier capability and compute allowance are separate policy decisions. A locked-tool preview may show documentation and sample output but cannot execute the protected backend.
