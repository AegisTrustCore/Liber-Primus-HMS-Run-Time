# HMS Distribution and User Experience Standard

Status: **ADOPTED**

This standard governs public tools, Patreon member tools, command-line utilities, plugins, hosted services, and puzzle packages.

## Two definitions of done

- **Engineering done:** the implementation works under its declared development environment.
- **Customer done:** a reasonably computer-literate researcher can obtain, launch, understand, use, export from, and verify the product without installing a programming environment or asking how to run source code.

A raw script may be released as a `DEVELOPER_TOOL`. It is not a customer-ready application merely because its source executes.

## Supported experiences

| Experience | Audience | Normal path |
|---|---|---|
| User | Ordinary researcher | Download or open, launch, use, save/export |
| Power user | Technical researcher | Download supported binary, run `--help`, receive human or JSON output |
| Developer | Contributor | Clone source, create an environment, install dependencies, run tests |

Developer setup must not be presented as the default customer path.

## Product classes and delivery modes

Product classes are `DEVELOPER_TOOL`, `USER_INSTRUMENT`, `PUZZLE_PACKAGE`, `PLUGIN`, and `HOSTED_SERVICE`.

Delivery modes are:

- `WEB`
- `DESKTOP_INSTALLER`
- `DESKTOP_PORTABLE`
- `CLI_BINARY`
- `RUNTIME`
- `PLUGIN`
- `DEVELOPER_SOURCE`

Access level and delivery mode are independent. An Observer instrument may be a desktop application; a Navigator capability may be hosted only.

## Core and interface rule

Every substantial instrument has one deterministic core. Desktop, CLI, web, and Runtime interfaces call that core and share the same test vectors. Interface implementations must not silently fork the research logic.

## Customer release gate

Before a tool or puzzle can be described as customer-ready, all applicable checks must pass:

- A supported platform and delivery mode are named truthfully.
- A clean user machine can launch the distributed artifact without Python, Node, `pip`, `npm`, or source checkout.
- The package exposes its product name, object or instrument ID, and version.
- Quick start, examples, method, limitations, and offline help are included.
- Normal errors are readable and do not expose a traceback.
- Output can be copied or exported in the declared format.
- A self-test or sealed acceptance test passes against the packaged artifact.
- Inputs are never modified in place.
- The package contains no credentials, private paths, private research, gated routes, or Vault material.
- Checksums, signature plan, release notes, and rollback/correction procedure exist.
- The exact package is tested before human approval; rebuilding invalidates that approval.

Automation may build, test, and reject. It may not fabricate human approval or publish a sealed campaign.

## Public GitHub experience

A customer tool page puts these sections in this order:

1. What it is
2. Download
3. Quick start
4. Supported systems
5. Examples
6. Output format
7. Limitations
8. Verify download
9. Developer setup
10. Changelog

Only tested operating-system builds are advertised. Early Windows-only support is acceptable when stated plainly. Official assets are never silently replaced; a correction receives a new version.

## Patreon delivery

Patreon posts may distribute approved early-access or tier-specific products, but must use the same package identity, version, checksum, limitations, and qualification record as GitHub releases. Members must not be asked to download random scripts or install development dependencies.

Protected logic stays server-side or in access-controlled packages. Hiding a button in a public client is not an access boundary.

## Puzzle packages

A public puzzle must be solvable from its released instructions and verifiable with a packaged client. Local verification is preferred only when the acceptance predicate cannot reveal protected material. Short or otherwise enumerable answers require an approved sealed service. Before opening a campaign, HMS privately confirms both an accepted and rejected submission against the exact distributed build and, where applicable, the exact deployed service. The acceptance answer remains sealed until the public solution gate.

The puzzle package must not require telemetry or an account. A network request is permitted only when the campaign explicitly declares the service, data sent, retention behavior, and failure mode. The complete public solution returns to GitHub when the campaign closes.

## First reference implementations

1. Expedition 001 establishes the portable puzzle-verifier pattern.
2. GP29 establishes the full customer instrument pattern.
3. Corpus Manifest Verifier reuses the packaging and interface pattern.
4. Endeavour Lite begins unifying released instruments in one shell.

GP29 is a calculator, not an LP decoder. No GP29 build becomes `RELEASED` until its canonical core, tests, user interface, CLI, JSON export, examples, limitations, self-test, portable package, checksums, and release notes pass the customer gate.
