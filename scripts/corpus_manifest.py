#!/usr/bin/env python3
"""Create and verify HMS corpus manifests without modifying corpus inputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import CorpusManifestError, create_manifest, verify_manifest


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def write_json(value: object, path: Path | None = None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path is None:
        print(rendered, end="")
    else:
        path.write_text(rendered, encoding="utf-8", newline="\n")


def main() -> int:
    configure_output()
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="Create a sorted manifest for a local directory")
    create.add_argument("root", type=Path)
    create.add_argument("--corpus-id", required=True)
    create.add_argument("--version", required=True)
    create.add_argument("--exclude", action="append", default=[])
    create.add_argument("--output", type=Path)
    verify = commands.add_parser("verify", help="Verify a directory against a manifest")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("root", type=Path)
    verify.add_argument("--strict", action="store_true", help="Fail when undeclared files are present")
    verify.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "create":
            manifest = create_manifest(args.root, args.corpus_id, args.version, args.exclude)
            write_json(manifest, args.output)
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
