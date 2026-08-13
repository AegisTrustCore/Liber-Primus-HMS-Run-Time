# Next Steps

## Foundation freeze

PR #1 remains `v0.1.0-rc.1` for publication-boundary review. Its scope is frozen: no new research packages, application features, or challenge launch will be added before merge.

Completed foundation gates:

- Public/private publication-boundary audit.
- Metadata-only Patreon public interface in GitHub.
- Status-only public research roadmap.
- Canonical object and provenance model.
- Deterministic environment manifest.
- Machine-readable Public Release Gate with automation unable to supply human approval.
- Patreon no-affiliation and GP29-status corrections.

Still required before `v0.1.0`:

1. Perform the final human review and explicitly approve [the pending gate](releases/gates/v0.1.0.json).
2. Configure and document the HMS release-signing identity without placing its private key in the repository or automation context.
3. Review and merge through protected `main` after all required checks pass.
4. Generate `SHA256SUMS`, sign the tag and release artifacts, and publish `v0.1.0` only from the reviewed foundation merge.
5. Update temporary Patreon branch/PR links to stable `main` or tagged-release URLs.

## Progressive public sequence after `v0.1.0`

1. Release GP29 `v0.1` as a separately versioned free tool.
2. Open Expedition 001 only after the foundation is live on the default branch.
3. Publish `RC-0001` as the first public known-control package after clean reproduction.
4. Release HMS Endeavour Lite alpha after its own capability and evidence review.
5. Continue with individually reviewed research, tool, and Runtime releases.

## Boundary rule

The public roadmap states what category of work is happening and what gate remains. The private research queue holds exact source experiments, assignments, parameters, datasets, candidate instructions, and active validation detail. A candidate enters GitHub in full only when it is intentionally promoted as a public package.

Releases follow demonstrated capability, not arbitrary calendar promises.
