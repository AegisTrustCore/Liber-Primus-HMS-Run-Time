#!/usr/bin/env python3
"""Build the deterministic HMS Endeavour Runtime Environment Windows RC package."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0-rc.1"
PACKAGE_NAME = f"HMS-Endeavour-Runtime-v{VERSION}-Windows-x64-portable.zip"
FIXED_TIME = (2026, 8, 14, 0, 0, 0)
CANONICAL_MANIFEST = ROOT / "corpus/liber-primus/manifests/LP-75-IMAGES-v1.0.0.json"

START_HERE = """HMS ENDEAVOUR RUNTIME ENVIRONMENT v1.0.0-rc.1

RELEASE CANDIDATE - NOT AN APPROVED PUBLIC RELEASE

HMS Endeavour Runtime is a private local workstation for the Rune Workbench, GP29,
corpus verification, page-aware LP Atlas, bounded experiments, immutable Runs,
Results and research objects, structural comparison, audit, safe backup, and export.

START
1. Double-click HMS-Endeavour-Runtime.exe.
2. Create a project in a new empty folder, or open an existing HMS project.
3. Use Rune Workbench, GP29, Corpus Verify, or Experiments and save the Result.
4. Inspect Runs & Results and explicitly export only the Result you intend to share.

Power users:
  HMS-Endeavour-Runtime-CLI.exe --help
  HMS-Endeavour-Runtime-CLI.exe self-test

BOUNDARIES
- Projects are private and local by default.
- The package includes the 75-page identity manifest, not page images.
- GP29 output is CALCULATION_ONLY; corpus reports are PROVENANCE_ONLY.
- Bounded comparison output is EXPERIMENTAL and never a solve declaration.
- Expedition 001 remains closed; its signed HTTPS client is disabled until an approved
  campaign manifest supplies an OPEN state, endpoint, Ed25519 public key, and key ID.
- Expedition answers are never saved; only the signed receipt and submission hash enter history.
- This exact build has no active endpoint, accounts, telemetry, uploads, solver, or automatic solve claims.
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(entry: str, name: str, stage: Path, work: Path, windowed: bool) -> None:
    args = [sys.executable,"-m","PyInstaller",str(ROOT / entry),"--name",name,"--onefile","--clean","--noconfirm","--distpath",str(stage),"--workpath",str(work / name),"--specpath",str(work / "spec"),"--paths",str(ROOT),"--windowed" if windowed else "--console"]
    subprocess.run(args, cwd=ROOT, check=True, env=os.environ.copy())


def write_package(stage: Path, output: Path) -> Path:
    files = sorted((path for path in stage.rglob("*") if path.is_file() and path.name != "SHA256SUMS"), key=lambda path:path.relative_to(stage).as_posix())
    (stage / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.relative_to(stage).as_posix()}\n" for path in files), encoding="utf-8", newline="\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted((item for item in stage.rglob("*") if item.is_file()), key=lambda item:item.relative_to(stage).as_posix()):
            info=zipfile.ZipInfo(path.relative_to(stage).as_posix(),date_time=FIXED_TIME); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644 << 16
            archive.writestr(info,path.read_bytes(),compresslevel=9)
    return output


def main() -> int:
    if os.name != "nt":
        raise SystemExit("This builder creates a Windows x64 package and must run on Windows.")
    os.environ["SOURCE_DATE_EPOCH"]="1786664400"; os.environ["PYTHONHASHSEED"]="0"
    work=ROOT / "build/endeavour-runtime-windows"; stage=work / "package"
    shutil.rmtree(work,ignore_errors=True); stage.mkdir(parents=True)
    build("scripts/endeavour_lite.py","HMS-Endeavour-Runtime-CLI",stage,work,False)
    build("scripts/endeavour_lite_app.py","HMS-Endeavour-Runtime",stage,work,True)
    (stage / "START-HERE.txt").write_text(START_HERE,encoding="utf-8",newline="\n")
    (stage / "canonical").mkdir(); shutil.copyfile(CANONICAL_MANIFEST,stage / "canonical" / CANONICAL_MANIFEST.name)
    (stage / "expedition").mkdir(); shutil.copyfile(ROOT / "challenges/manifest.json",stage / "expedition/manifest.json")
    (stage / "schemas").mkdir()
    for name in ("hms-project.schema.json","project-settings.schema.json","research-object.schema.json","result-envelope.schema.json","corpus-manifest.schema.json","corpus-verification.schema.json","challenge-manifest.schema.json","expedition-verification-receipt.schema.json"):
        shutil.copyfile(ROOT / "schemas" / name,stage / "schemas" / name)
    shutil.copyfile(ROOT / "LICENSE",stage / "LICENSE.txt")
    (stage / "manifest.json").write_text(json.dumps({"schema":"HMS_CUSTOMER_PACKAGE_V1","product":"HMS Endeavour Runtime Environment","version":VERSION,"status":"RELEASE_CANDIDATE","package_state":"RC_NOT_FOR_PUBLIC_RELEASE","network_access":False,"telemetry":False,"expedition_campaign":"CLOSED","features":["RUNE_WORKBENCH","GP29","CORPUS_VERIFY","LP_ATLAS_PAGE_AWARE","RESEARCH_OBJECTS","RESULT_COMPARISON","PROJECT_AUDIT","PRIVACY_SAFE_BACKUP","BOUNDED_GP29_EXPERIMENT","EXPEDITION_SIGNED_CLIENT_FAIL_CLOSED","LOCAL_RUNS_RESULTS","EXPLICIT_JSON_EXPORT"]},indent=2)+"\n",encoding="utf-8",newline="\n")
    output=write_package(stage,ROOT / "dist" / PACKAGE_NAME)
    print(f"Built {output}"); print(f"SHA256 {sha256(output)}"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
