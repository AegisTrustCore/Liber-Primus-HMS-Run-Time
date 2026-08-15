#!/usr/bin/env python3
"""Build the reproducible Windows Expedition 001 verifier candidate package."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import base64
import binascii
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.0"
PACKAGE_NAME = f"HMS-XPD-0001-v{VERSION}-Windows-x64-portable.zip"
FIXED_TIME = (2026, 8, 14, 0, 0, 0)

QUICK_START = """HMS ENDEAVOUR — EXPEDITION 001 VERIFIER v0.3.0

SECURE-SERVICE DEVELOPMENT CANDIDATE — CAMPAIGN CLOSED — NOT FOR RELEASE

1. Double-click HMS-XPD-0001-Verifier.exe.
2. Solve the five synthetic Evidence Ledger classifications.
3. Enter the five-letter answer and select Verify.
4. Copy or save the non-disclosing JSON receipt.

Power users:
  HMS-XPD-0001-Verifier-CLI.exe --help
  HMS-XPD-0001-Verifier-CLI.exe --self-test
  HMS-XPD-0001-Verifier-CLI.exe --instructions
  HMS-XPD-0001-Verifier-CLI.exe --hint 1
  HMS-XPD-0001-Verifier-CLI.exe --json YOUR_ANSWER

Instructions and self-tests work offline. Answer verification requires the configured official
HTTPS service. This development package has no endpoint and must fail closed.
"""

SECURITY = """PUBLIC CLIENT SECURITY BOUNDARY

The package must not contain plaintext solutions, future-stage secrets, unreleased hints,
private key material, reversible answer representations, private research routes, credentials,
or tier-only material. No answer digest or equivalent acceptance predicate may ship publicly.
The configured HTTPS service returns a signed receipt containing only the submission hash.
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(entry: str, name: str, stage: Path, work: Path, windowed: bool, challenge_manifest: Path) -> None:
    add_data = f"{challenge_manifest}{os.pathsep}challenges"
    args = [
        sys.executable, "-m", "PyInstaller", str(ROOT / entry),
        "--name", name, "--onefile", "--clean", "--noconfirm",
        "--distpath", str(stage), "--workpath", str(work / name),
        "--specpath", str(work / "spec"), "--paths", str(ROOT),
        "--add-data", add_data, "--windowed" if windowed else "--console",
    ]
    subprocess.run(args, cwd=ROOT, check=True, env=os.environ.copy())


def main() -> int:
    if os.name != "nt":
        raise SystemExit("This builder creates a Windows x64 package and must run on Windows.")
    os.environ["SOURCE_DATE_EPOCH"] = "1786664400"
    os.environ["PYTHONHASHSEED"] = "0"
    work = ROOT / "build" / "expedition-verifier-windows"
    stage = work / "package"
    shutil.rmtree(work, ignore_errors=True)
    stage.mkdir(parents=True)
    endpoint = os.environ.get("HMS_XPD_VERIFICATION_ENDPOINT")
    public_key = os.environ.get("HMS_XPD_VERIFICATION_PUBLIC_KEY")
    public_key_id = os.environ.get("HMS_XPD_VERIFICATION_PUBLIC_KEY_ID")
    public_values = (endpoint, public_key, public_key_id)
    if any(public_values) and not all(public_values):
        raise SystemExit("Endpoint, Ed25519 public key, and key ID must be configured together.")
    if all(public_values):
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.hostname or parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise SystemExit("Configured verification endpoint must be a clean HTTPS URL.")
        try:
            public_key_bytes = base64.b64decode(public_key, validate=True)
        except (binascii.Error, ValueError) as error:
            raise SystemExit("Configured Ed25519 public key is invalid base64.") from error
        derived_id = "ED25519-" + hashlib.sha256(public_key_bytes).hexdigest()[:16].upper()
        if len(public_key_bytes) != 32 or public_key_id != derived_id:
            raise SystemExit("Configured Ed25519 public key and key ID do not match.")
    configured_manifest = json.loads((ROOT / "challenges" / "manifest.json").read_text(encoding="utf-8"))
    challenge = next(item for item in configured_manifest["challenges"] if item["id"] == "XPD-0001")
    challenge["verification_endpoint"] = endpoint
    challenge["verification_public_key"] = public_key
    challenge["verification_public_key_id"] = public_key_id
    config_dir = work / "configured-challenges"
    config_dir.mkdir()
    configured_manifest_path = config_dir / "manifest.json"
    configured_manifest_path.write_text(json.dumps(configured_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    build("scripts/verify_challenge.py", "HMS-XPD-0001-Verifier-CLI", stage, work, False, configured_manifest_path)
    build("scripts/verify_challenge_gui.py", "HMS-XPD-0001-Verifier", stage, work, True, configured_manifest_path)
    (stage / "QUICK_START.txt").write_text(QUICK_START, encoding="utf-8", newline="\n")
    (stage / "SECURITY.txt").write_text(SECURITY, encoding="utf-8", newline="\n")
    shutil.copyfile(ROOT / "challenges" / "expedition-001" / "README.md", stage / "PUZZLE.md")
    shutil.copyfile(ROOT / "challenges" / "expedition-001" / "HINTS.md", stage / "HINTS.md")
    shutil.copyfile(ROOT / "schemas" / "expedition-verification-receipt.schema.json", stage / "RECEIPT-SCHEMA.json")
    shutil.copyfile(ROOT / "LICENSE", stage / "LICENSE.txt")
    product_manifest = {
        "schema": "HMS_CUSTOMER_PACKAGE_V1",
        "product": "HMS Expedition Verifier",
        "instrument_id": "expedition-verifier",
        "expedition_id": "XPD-0001",
        "version": VERSION,
        "status": "IN_DEVELOPMENT",
        "package_state": "SECURE_SERVICE_CANDIDATE_NOT_FOR_RELEASE",
        "campaign_state": "CLOSED",
        "network_access": True,
        "verification_endpoint_configured": endpoint is not None,
        "verification_endpoint": endpoint,
        "verification_public_key_configured": public_key is not None,
        "verification_public_key": public_key,
        "verification_public_key_id": public_key_id,
        "telemetry": False,
        "solution_disclosed": False,
    }
    (stage / "manifest.json").write_text(json.dumps(product_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
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
