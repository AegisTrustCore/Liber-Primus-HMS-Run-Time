# Deployment material

This directory contains deployment definitions for hosted HMS components. Their presence does not mean a service is deployed or public.

## Expedition verification service

[`expedition-service/`](expedition-service/) contains the non-root container, API contract, and production server configuration for the sealed Expedition verifier.

Expedition 001 remains closed until the [deployment gate](../docs/tooling/EXPEDITION_SERVICE_DEPLOYMENT_GATE.md) records an approved host, signing key, HTTPS endpoint, privacy and abuse controls, exact client qualification, and a human opening decision.

Never commit production secrets, private signing material, answer predicates, or service credentials here.

