# Liber Runtime — initial contract

Audience: Navigator beta and above, with public verification surfaces

Status: In development; deterministic developer core runnable

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

## Runnable slice v0.0.1

The repository now includes a local reference engine for `gp29.calculate` jobs. It provides deterministic job IDs, specification hashes, result hashes, explicit visibility, and the evidence label `CALCULATION_ONLY`.

```text
python scripts/hms_runtime.py self-test
python scripts/hms_runtime.py gp29 "F U/V TH" --mode tokens --job
```

The local `RuntimeStore` demonstrates submit, execute, and retrieve behavior without accounts, persistence, networking, entitlements, or Vault access. Those omissions are intentional and remain required work before a hosted beta.

The Corpus Manifest Verifier now emits `HMS_CORPUS_VERIFICATION_V1`. That portable report—not an implicit workstation crawl or local corpus-root path—is the planned Runtime ingestion boundary. Report sharing remains explicit and private by default.

Canonical contracts:

- `schemas/runtime-job.schema.json`
- `schemas/runtime-result.schema.json`
- `hms_tools/runtime.py`
- `schemas/corpus-manifest.schema.json`
- `schemas/corpus-verification.schema.json`
