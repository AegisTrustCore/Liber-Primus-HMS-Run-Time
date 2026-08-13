#!/usr/bin/env python3
"""Strict Gematria Primus 29-symbol lookup and summation CLI."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Entry:
    index: int
    rune: str
    token: str
    prime: int
    aliases: tuple[str, ...] = ()


ENTRIES = (
    Entry(0, "ᚠ", "F", 2), Entry(1, "ᚢ", "U", 3), Entry(2, "ᚦ", "TH", 5),
    Entry(3, "ᚩ", "O", 7), Entry(4, "ᚱ", "R", 11), Entry(5, "ᚳ", "K", 13, ("C", "C/K")),
    Entry(6, "ᚷ", "G", 17), Entry(7, "ᚹ", "W", 19), Entry(8, "ᚻ", "H", 23),
    Entry(9, "ᚾ", "N", 29), Entry(10, "ᛁ", "I", 31), Entry(11, "ᛄ", "J", 37),
    Entry(12, "ᛇ", "EO", 41), Entry(13, "ᛈ", "P", 43), Entry(14, "ᛉ", "X", 47),
    Entry(15, "ᛋ", "S", 53, ("Z", "S/Z")), Entry(16, "ᛏ", "T", 59),
    Entry(17, "ᛒ", "B", 61), Entry(18, "ᛖ", "E", 67), Entry(19, "ᛗ", "M", 71),
    Entry(20, "ᛚ", "L", 73), Entry(21, "ᛝ", "ING", 79, ("NG",)),
    Entry(22, "ᛟ", "OE", 83), Entry(23, "ᛞ", "D", 89), Entry(24, "ᚪ", "A", 97),
    Entry(25, "ᚫ", "AE", 101), Entry(26, "ᚣ", "Y", 103),
    Entry(27, "ᛡ", "IA", 107, ("IO",)), Entry(28, "ᛠ", "EA", 109),
)

BY_RUNE = {entry.rune: entry for entry in ENTRIES}
BY_TOKEN: dict[str, Entry] = {}
for _entry in ENTRIES:
    for _token in (_entry.token, *_entry.aliases):
        BY_TOKEN[_token] = _entry


def lookup_token(token: str) -> Entry:
    normalized = token.strip().upper()
    try:
        return BY_TOKEN[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown GP29 token: {token!r}") from exc


def parse_token_arguments(values: list[str]) -> list[Entry]:
    tokens = [part for value in values for part in re.split(r"[\s,]+", value) if part]
    if not tokens:
        raise ValueError("at least one GP29 token is required")
    return [lookup_token(token) for token in tokens]


def parse_runes(value: str) -> list[Entry]:
    entries: list[Entry] = []
    for rune in value:
        if rune.isspace():
            continue
        if rune not in BY_RUNE:
            raise ValueError(f"unknown GP29 rune: {rune!r}")
        entries.append(BY_RUNE[rune])
    if not entries:
        raise ValueError("at least one GP29 rune is required")
    return entries


def result(entries: list[Entry]) -> dict:
    return {"symbols": [asdict(entry) for entry in entries], "gp_sum": sum(item.prime for item in entries)}


def print_result(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for item in payload["symbols"]:
        print(f"{item['index']:>2}  {item['rune']}  {item['token']:<3}  {item['prime']:>3}")
    print(f"GP sum: {payload['gp_sum']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("table", help="show the full 29-symbol table")
    lookup = commands.add_parser("lookup", help="look up one Latin token or alias")
    lookup.add_argument("token")
    total = commands.add_parser("sum", help="sum explicit Latin tokens")
    total.add_argument("tokens", nargs="+")
    runes = commands.add_parser("runes", help="sum Unicode runes")
    runes.add_argument("value")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    args = build_parser().parse_args()
    try:
        if args.command == "table":
            entries = list(ENTRIES)
        elif args.command == "lookup":
            entries = [lookup_token(args.token)]
        elif args.command == "sum":
            entries = parse_token_arguments(args.tokens)
        else:
            entries = parse_runes(args.value)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    print_result(result(entries), args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
