#!/usr/bin/env python3
"""Verify an HMS Expedition submission through the official sealed service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.challenge_verifier import application_root
from hms_tools.expedition_client import ExpeditionClientError, ServiceConfiguration, configured_service, verify_remote
from hms_tools.expedition_verifier import packaged_self_test
from hms_tools.expedition_001 import CHALLENGE_ID, HINTS, VERSION, hint_text, instructions_text


def write_json(value: object, path: Path | None = None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path is None:
        print(rendered, end="")
    else:
        path.write_text(rendered, encoding="utf-8", newline="\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("items", nargs="*", metavar="ANSWER", help="Answer, or legacy EXPEDITION_ID ANSWER")
    parser.add_argument("--expedition", default=CHALLENGE_ID, help=f"Expedition ID (default: {CHALLENGE_ID})")
    parser.add_argument("--json", action="store_true", help="Print a non-disclosing JSON verification receipt")
    parser.add_argument("--output", type=Path, help="Write the JSON receipt to a file")
    parser.add_argument("--endpoint", help="HTTPS verification endpoint; intended for qualification and deployment testing")
    parser.add_argument("--public-key", help="Base64 Ed25519 public key; required with --endpoint")
    parser.add_argument("--public-key-id", help="Frozen Ed25519 key ID; required with --endpoint")
    parser.add_argument("--hint", type=int, choices=range(1, len(HINTS) + 1), metavar=f"1-{len(HINTS)}")
    parser.add_argument("--instructions", action="store_true", help="Show the complete public puzzle instructions")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic accept/reject controls")
    parser.add_argument("--version", action="version", version=f"HMS Expedition Verifier {VERSION}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        passed = packaged_self_test(VERSION)
        result = {"product": "HMS Expedition Verifier", "version": VERSION, "self_test": "PASS" if passed else "FAIL"}
        write_json(result) if args.json else print(f"Self-test {'passed' if passed else 'failed'}.")
        return 0 if passed else 1
    if args.instructions:
        print(instructions_text())
        return 0
    if args.hint is not None:
        print(hint_text(args.hint))
        return 0
    if len(args.items) == 1:
        expedition_id, submitted = args.expedition, args.items[0]
    elif len(args.items) == 2:
        expedition_id, submitted = args.items
    else:
        print("ERROR: provide ANSWER, or legacy EXPEDITION_ID ANSWER. Run --help for usage.", file=sys.stderr)
        return 2

    try:
        if args.endpoint or args.public_key or args.public_key_id:
            if not all((args.endpoint, args.public_key, args.public_key_id)):
                raise ExpeditionClientError("--endpoint, --public-key, and --public-key-id must be provided together")
            configuration = ServiceConfiguration(args.endpoint, args.public_key, args.public_key_id)
        else:
            configuration = configured_service(application_root() / "challenges" / "manifest.json")
        if configuration is None:
            raise ExpeditionClientError("verification service is not configured; the campaign remains closed")
        receipt = verify_remote(
            configuration.endpoint,
            expedition_id,
            submitted,
            VERSION,
            public_key_b64=configuration.public_key_b64,
            public_key_id=configuration.public_key_id,
        )
    except ExpeditionClientError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if args.output:
        write_json(receipt, args.output)
    if args.json:
        write_json(receipt)
    elif receipt["accepted"]:
        print("VALID STAGE RESULT")
        print(f"Expedition: {expedition_id}")
        print(f"Verifier: {VERSION}")
        print(f"Proof receipt: {receipt['receipt_id']}")
    else:
        print("NOT ACCEPTED")
        print("The submission did not satisfy the frozen verification contract.")
        print("No additional solution information is disclosed.")
        print(f"Proof receipt: {receipt['receipt_id']}")
    return 0 if receipt["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
