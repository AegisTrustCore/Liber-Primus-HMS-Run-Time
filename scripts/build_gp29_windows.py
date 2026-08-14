#!/usr/bin/env python3
"""Build the Windows GP29 v0.1.1 release-candidate package."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.1-rc.2"
PACKAGE_NAME = f"HMS-GP29-v{VERSION}-Windows-x64-portable.zip"
FIXED_TIME = (2026, 8, 13, 0, 0, 0)

START_HERE = """HMS GP29 Calculator v0.1.1-rc.2

WHAT IT IS
A deterministic Gematria Primus calculator. It is not a decoder and makes no Liber Primus solve claim.

START
- Double-click HMS-GP29.exe for the desktop interface.
- Power users can run HMS-GP29-CLI.exe --help.
- Run HMS-GP29-CLI.exe self-test before relying on a calculation.
- The desktop executable also supports HMS-GP29.exe --self-test for package qualification.

INPUT
Use English-letter mode for ordinary A-Z words. Every letter remains separate, so H cannot be silently combined into TH. Use Latin-sound mode only when GP29 clusters such as TH, NG, or ING are intended. Explicit sound tokens and the 29 supported runes remain available.

VISIBLE ALPHABET
The desktop application shows the complete 29-rune table. Filter it by rune, sound, row, or prime; then insert the exact sound token or rune. A mode change that would make existing input incompatible asks before clearing it.

WORKFLOW FEATURES
Use quick examples to learn the input modes, Ctrl+Enter or F5 to calculate, the in-memory session history to revisit calculations, clipboard actions to share results, and CSV export for the per-rune breakdown. Session history is never written to disk or transmitted.

OUTPUT
The default results dashboard shows headline totals, normalized sequences, aggregate registers, and a per-rune table. Raw JSON remains available in a secondary tab and through export. Each rune reports its canonical L, R, prime, N, and Q values.

DOCUMENTED TESTS
- English letters: H -> Prime / GP sum 23
- English letters: TH -> T + H -> Prime / GP sum 82
- Latin sounds: TH -> one TH rune -> Prime / GP sum 5
- Tokens: F U/V TH -> Prime / GP sum 10
- Rune: ᚠ -> Prime / GP sum 2
- EXAMPLE.txt contains the UTF-8 Latin example.

CLI EXAMPLES
HMS-GP29-CLI.exe self-test
HMS-GP29-CLI.exe gp29 CICADA --mode letters
HMS-GP29-CLI.exe gp29 --file EXAMPLE.txt --mode letters

JSON EXPORT
In the desktop application, calculate first and select Export JSON. You choose the destination and filename in the Save dialog.

PRIVACY
The application is offline. It has no telemetry, accounts, or network features. Input files are read but never modified.

VERIFY
Compare each included file with SHA256SUMS. Compare this ZIP with the checksum on the official GitHub release page.

STATUS
Release candidate. This exact ZIP is not an approved HMS release until its public software gate is APPROVED and the official GitHub release is published.
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_package(stage: Path, output: Path) -> Path:
    files = sorted((path for path in stage.iterdir() if path.is_file() and path.name != "SHA256SUMS"), key=lambda path: path.name)
    sums = "".join(f"{sha256(path)}  {path.name}\n" for path in files)
    (stage / "SHA256SUMS").write_text(sums, encoding="utf-8", newline="\n")
    members = sorted(stage.iterdir(), key=lambda path: path.name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in members:
            info = zipfile.ZipInfo(path.name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return output


def build_executable(entry: str, name: str, stage: Path, work: Path, windowed: bool) -> None:
    try:
        import PyInstaller
    except ImportError as error:
        raise SystemExit("PyInstaller 6.22.0 is required: python -m pip install -r requirements-build.txt") from error
    args = [
        sys.executable, "-m", "PyInstaller", str(ROOT / entry), "--name", name, "--onefile", "--clean", "--noconfirm",
        "--distpath", str(stage), "--workpath", str(work / name), "--specpath", str(work / "spec"),
        "--paths", str(ROOT),
    ]
    args.append("--windowed" if windowed else "--console")
    subprocess.run(args, cwd=ROOT, check=True, env=os.environ.copy())


def main() -> int:
    if os.name != "nt":
        raise SystemExit("This builder creates the declared Windows x64 package and must run on Windows.")
    os.environ["SOURCE_DATE_EPOCH"] = "1786578000"
    os.environ["PYTHONHASHSEED"] = "0"
    dist = ROOT / "dist"
    work = ROOT / "build" / "gp29-windows"
    stage = work / "package"
    shutil.rmtree(work, ignore_errors=True)
    stage.mkdir(parents=True)
    build_executable("scripts/hms_runtime.py", "HMS-GP29-CLI", stage, work, False)
    build_executable("scripts/gp29_app.py", "HMS-GP29", stage, work, True)
    (stage / "START-HERE.txt").write_text(START_HERE, encoding="utf-8", newline="\n")
    (stage / "EXAMPLE.txt").write_text("CICADA\n", encoding="utf-8", newline="\n")
    shutil.copyfile(ROOT / "LICENSE", stage / "LICENSE.txt")
    output = write_package(stage, dist / PACKAGE_NAME)
    print(f"Built {output}")
    print(f"SHA256 {sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
