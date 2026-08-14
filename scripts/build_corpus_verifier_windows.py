#!/usr/bin/env python3
"""Build the Windows Corpus Manifest Verifier development package."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-dev"
PACKAGE_NAME = f"HMS-Corpus-Verifier-v{VERSION}-Windows-x64-portable.zip"
FIXED_TIME = (2026, 8, 13, 0, 0, 0)

START_HERE = """HMS Corpus Manifest Verifier v0.1.0-dev

DEVELOPMENT BUILD — NOT AN APPROVED PUBLIC RELEASE

WHAT IT DOES
Checks local files against a canonical JSON manifest: path safety, SHA-256, byte count, missing files, and optional undeclared-file rejection.

START
- Double-click HMS-Corpus-Verifier.exe for the desktop interface.
- Choose a manifest and its corpus root, then select Verify.
- Power users can run HMS-Corpus-Verifier-CLI.exe --help.
- Run either executable with --self-test before qualification.

PRIVACY AND SAFETY
Verification is offline and read-only. The application has no telemetry, accounts, network features, or upload path. It never establishes authenticity, redistribution rights, transcription correctness, or a Liber Primus solve.
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(entry: str, name: str, stage: Path, work: Path, windowed: bool) -> None:
    args = [sys.executable, "-m", "PyInstaller", str(ROOT / entry), "--name", name, "--onefile", "--clean", "--noconfirm", "--distpath", str(stage), "--workpath", str(work / name), "--specpath", str(work / "spec"), "--paths", str(ROOT), "--windowed" if windowed else "--console"]
    subprocess.run(args, cwd=ROOT, check=True, env=os.environ.copy())


def main() -> int:
    if os.name != "nt":
        raise SystemExit("This builder creates a Windows x64 package and must run on Windows.")
    os.environ["SOURCE_DATE_EPOCH"] = "1786578000"
    os.environ["PYTHONHASHSEED"] = "0"
    work = ROOT / "build" / "corpus-verifier-windows"
    stage = work / "package"
    shutil.rmtree(work, ignore_errors=True)
    stage.mkdir(parents=True)
    build("scripts/corpus_manifest.py", "HMS-Corpus-Verifier-CLI", stage, work, False)
    build("scripts/corpus_verifier_app.py", "HMS-Corpus-Verifier", stage, work, True)
    (stage / "START-HERE.txt").write_text(START_HERE, encoding="utf-8", newline="\n")
    shutil.copyfile(ROOT / "LICENSE", stage / "LICENSE.txt")
    files = sorted(stage.iterdir(), key=lambda path: path.name)
    (stage / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in files), encoding="utf-8", newline="\n")
    output = ROOT / "dist" / PACKAGE_NAME
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(stage.iterdir(), key=lambda item: item.name):
            info = zipfile.ZipInfo(path.name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    print(f"Built {output}")
    print(f"SHA256 {sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
