#!/usr/bin/env python3
"""Create and verify HMS corpus manifests without modifying corpus inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import CorpusManifestError, canonical_json, create_manifest, run_demo_self_test, validate_manifest, verify_manifest


APP_VERSION = "0.1.0-rc.2"
CANONICAL_MANIFEST_NAME = "LP-75-IMAGES-v1.0.0.json"


def application_root() -> Path:
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else ROOT


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def default_canonical_manifest() -> Path:
    if getattr(sys, "frozen", False):
        return application_root() / "canonical" / CANONICAL_MANIFEST_NAME
    return ROOT / "corpus" / "liber-primus" / "manifests" / CANONICAL_MANIFEST_NAME


def write_json(value: object, path: Path | None = None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path is None:
        print(rendered, end="")
    else:
        path.write_text(rendered, encoding="utf-8", newline="\n")


def main() -> int:
    configure_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-version", action="version", version=f"HMS Corpus Manifest Verifier {APP_VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo-self-test", help="Run the packaged five-case synthetic verifier suite")
    demo.add_argument("--demo-root", type=Path, default=application_root() / "demo" / "corpus-verifier")
    create = commands.add_parser("create", help="Create a sorted manifest for a local directory")
    create.add_argument("root", type=Path)
    create.add_argument("--corpus-id", required=True)
    create.add_argument("--version", required=True)
    create.add_argument("--exclude", action="append", default=[])
    create.add_argument("--role", default="UNSPECIFIED", help="Role assigned to every created manifest entry")
    create.add_argument("--output", type=Path)
    canonical = commands.add_parser("canonical-info", help="Describe the bundled canonical 75-page LP image manifest")
    canonical.add_argument("--manifest", type=Path, default=default_canonical_manifest())
    verify = commands.add_parser("verify", help="Verify a directory against a manifest")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("root", type=Path)
    verify.add_argument("--strict", action="store_true", help="Fail when undeclared files are present")
    verify.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "demo-self-test":
            result = run_demo_self_test(args.demo_root)
            write_json(result)
            return 0 if result["passed"] else 1
        if args.command == "create":
            manifest = create_manifest(args.root, args.corpus_id, args.version, args.exclude, args.role)
            write_json(manifest, args.output)
            return 0
        if args.command == "canonical-info":
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            files = validate_manifest(manifest)
            write_json({
                "schema": "HMS_CANONICAL_CORPUS_INFO_V1",
                "application_version": APP_VERSION,
                "manifest": args.manifest.name,
                "corpus_id": manifest["corpus_id"],
                "corpus_version": manifest["version"],
                "file_count": len(files),
                "manifest_sha256": hashlib.sha256(canonical_json(manifest)).hexdigest(),
                "limitations": ["This identifies declared page-image bytes only; it does not establish historical authenticity, rights, transcription correctness, or a solve."],
            })
            return 0
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = verify_manifest(manifest, args.root, args.strict)
        write_json(report, args.output)
        return 0 if report["status"] == "PASS" else 1
    except (CorpusManifestError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
