# Packaging

Packaging files are build recipes, not released binaries. A CI artifact or local build is unofficial until its exact hash passes the public release gate and receives human approval.

## Expedition 001 Windows verifier

Developer build:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --clean --noconfirm packaging/xpd-0001-verifier.spec
python -m PyInstaller --clean --noconfirm packaging/xpd-0001-verifier-cli.spec
```

The resulting GUI and CLI executables must be tested in a clean directory for:

1. double-click launch;
2. a privately known accepted submission;
3. a rejected submission;
4. readable empty-input handling;
5. absence of network activity and telemetry;
6. absence of private paths, keys, routes, candidate solves, and staged Patreon material.
7. visible beginner instructions and all four progressive hints.

Do not publish the accepted answer or acceptance-test transcript before the solution gate.
