# HMS Plugin and Integration Boundary

Status: **CONTRACT PREVIEW — NO PUBLIC PLUGIN EXECUTION YET**

The public repository exposes the draft manifest contract so integrations can be reviewed without pretending the Plugin SDK is released. Runtime plugin execution, installation, entitlements, sandboxing, signing, revocation, and member packages remain Admiral-gated development work.

Every future plugin must declare:

- identity, version, publisher, and Runtime compatibility;
- its evidence authority class;
- exact project/page/object/result permissions;
- inputs and outputs using HMS object contracts;
- any network permission and a closed domain allow-list;
- limitations that remain attached to every Result.

No plugin receives network, Vault, corpus, project, write, or publication authority by default. A plugin cannot elevate its own output or bypass the HMS Result shell. The draft schema is [`hms-plugin-manifest.schema.json`](../schemas/hms-plugin-manifest.schema.json).

## Delivery boundary

| Layer | Availability |
|---|---|
| Manifest contract and permission vocabulary | Public design preview |
| Read-only example manifests | Future public documentation |
| Private HMS integration prototypes | Admiral development staging |
| Executable Plugin SDK or third-party loader | Not built or released |

Publishing this contract does not promise compatibility with the eventual stable SDK.
