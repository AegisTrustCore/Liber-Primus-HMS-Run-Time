#!/usr/bin/env python3
"""HMS Runtime developer CLI for the first deterministic core slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.gp29 import GP29InputError, calculate, self_test
from hms_tools.runtime import create_job, execute_job


def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    gp29 = commands.add_parser("gp29", help="Calculate GP29 values")
    gp29.add_argument("text", nargs="?", help="Rune text or separated Latin tokens")
    gp29.add_argument("--file", type=Path)
    gp29.add_argument("--mode", choices=("auto", "runes", "tokens"), default="auto")
    gp29.add_argument("--job", action="store_true", help="Wrap calculation in the Runtime job/result contract")
    commands.add_parser("self-test", help="Run frozen public GP29 vectors")
    run_job = commands.add_parser("run-job", help="Execute a JSON job file")
    run_job.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "self-test":
            result = self_test(); emit(result)
            return 0 if result["failed"] == 0 else 1
        if args.command == "run-job":
            emit(execute_job(json.loads(args.path.read_text(encoding="utf-8"))))
            return 0
        if args.text is not None and args.file is not None:
            parser.error("provide text or --file, not both")
        text = args.file.read_text(encoding="utf-8") if args.file else args.text
        if text is None:
            parser.error("gp29 requires text or --file")
        if args.job:
            emit(execute_job(create_job(text, args.mode)))
        else:
            emit(calculate(text, args.mode))
        return 0
    except (GP29InputError, ValueError, json.JSONDecodeError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
