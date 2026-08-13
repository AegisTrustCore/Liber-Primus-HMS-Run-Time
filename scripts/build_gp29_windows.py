#!/usr/bin/env python3
"""Build the Windows GP29 GUI/CLI release-candidate package."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-rc.1"
PACKAGE_NAME = f"HMS-GP29-v{VERSION}-Windows-x64-portable.zip"
FIXED_TIME = (2026, 8, 13, 0, 0, 0)

START_HERE = """HMS GP29 Calculator v0.1.0-rc.1

WHAT IT IS
A deterministic Gematria Primus calculator. It is not a decoder and makes no Liber Primus solve claim.

START
- Double-click HMS-GP29.exe for the desktop interface.
- Power users can run HMS-GP29-CLI.exe --help.
- Run HMS-GP29-CLI.exe self-test before relying on a calculation.
- The desktop executable also supports HMS-GP29.exe --self-test for package qualification.

INPUT
Use the 29 supported runes, or explicit sound tokens separated by spaces or commas. Continuous Latin is rejected because sound segmentation would be ambiguous.

PRIVACY
The application is offline. It has no telemetry, accounts, or network features. Input files are read but never modified.

VERIFY
Compare each included file with SHA256SUMS. Compare this ZIP with the checksum on the official GitHub release page.

STATUS
Release candidate. Do not redistribute it as an approved HMS release until its public software gate is APPROVED.
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
    shutil.copyfile(ROOT / "LICENSE", stage / "LICENSE.txt")
    output = write_package(stage, dist / PACKAGE_NAME)
    print(f"Built {output}")
    print(f"SHA256 {sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
