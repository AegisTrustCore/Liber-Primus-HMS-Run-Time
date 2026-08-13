# Security Policy

Do not open a public issue containing credentials, tokens, signing keys, private correspondence, personal information, Vault material, or unreleased research.

If sensitive material is discovered in repository history, stop distribution and contact the project owner privately. Removing a visible file is not sufficient if the content remains in Git history; affected credentials must also be rotated.

Public frontend controls are not security boundaries. Premium logic, private datasets, and authoritative entitlement checks belong in protected server-side systems outside this repository.

Official signing keys are human-controlled secrets and must never enter repository files, CI variables used by untrusted pull requests, Patreon posts, browser automation, or AI-assistant context. See [SIGNING.md](SIGNING.md).

Potential discoveries involving credentials, personal data, active services, or exploitable systems follow [DISCLOSURE_POLICY.md](DISCLOSURE_POLICY.md) before publication.
