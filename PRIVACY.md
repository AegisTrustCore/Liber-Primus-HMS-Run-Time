# Research Privacy and Sharing Policy

HMS collects and retains only the user research required to provide an explicitly requested capability.

## Default visibility

```text
PRIVATE → PROJECT → GROUP → HMS_REVIEW → PUBLIC
```

New projects, annotations, hypotheses, corpora, runs, and results default to `PRIVATE`. Visibility changes require an explicit user action. Joining a community, Patreon tier, group, or research session never makes private work public.

## Local/private mode

Endeavour Lite and the Cartographer workstation are designed for local-only projects. Local source material and notes remain on the user's machine unless the user explicitly submits a defined bundle. Submission must preview the exact objects and metadata that will leave the device.

## Data minimization

- Do not upload source material when a local hash or manifest can satisfy the task.
- Do not collect unpublished hypotheses for analytics or model training by default.
- Keep authentication, entitlement, billing, research content, and telemetry as separate data classes.
- Provide export, deletion, retention, and sharing controls.
- Record an audit event for every visibility change and HMS-review submission.

## Compute is a separate entitlement

Tool access does not imply unlimited computation. Hosted capabilities will enforce separately configurable limits for jobs per period, concurrent jobs, maximum runtime, parameter-family size, storage, retention, and export volume. Public tier copy must distinguish capability access from compute allowance.

## Locked-tool previews

A user without entitlement may see a tool's purpose, status, example output, limitations, and required tier. The protected backend must not execute the tool, access private data, or return a protected result.
