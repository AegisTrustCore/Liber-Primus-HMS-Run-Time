"""Deterministic Gematria Primus (GP29) parsing and calculation core."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import asdict, dataclass


RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109)
SOUNDS = ("F", "U/V", "TH", "O", "R", "C/K", "G", "W", "H", "N", "I/J", "IO/IA", "EO", "P", "X", "S/Z", "T", "B", "E", "M", "L", "NG/ING", "OE", "D", "A", "AE", "Y", "EA", "Q")


@dataclass(frozen=True)
class RuneEntry:
    index: int
    rune: str
    sound: str
    prime: int


TABLE = tuple(RuneEntry(i, rune, SOUNDS[i], PRIMES[i]) for i, rune in enumerate(RUNES))
BY_RUNE = {entry.rune: entry for entry in TABLE}


def _aliases() -> dict[str, RuneEntry]:
    aliases: dict[str, RuneEntry] = {}
    for entry in TABLE:
        aliases[entry.sound] = entry
        for alias in entry.sound.split("/"):
            aliases[alias] = entry
    return aliases


BY_TOKEN = _aliases()


class GP29InputError(ValueError):
    """Raised when input cannot be mapped without guessing."""


def parse_runes(text: str) -> list[RuneEntry]:
    entries: list[RuneEntry] = []
    for character in unicodedata.normalize("NFC", text):
        if character in BY_RUNE:
            entries.append(BY_RUNE[character])
        elif character.isspace():
            continue
        else:
            raise GP29InputError(f"unsupported rune-mode character: {character!r}")
    if not entries:
        raise GP29InputError("input contains no GP29 runes")
    return entries


def parse_tokens(text: str) -> list[RuneEntry]:
    normalized = unicodedata.normalize("NFKC", text).upper().strip()
    tokens = [token for token in re.split(r"[\s,;|]+", normalized) if token]
    if not tokens:
        raise GP29InputError("input contains no GP29 tokens")
    unknown = [token for token in tokens if token not in BY_TOKEN]
    if unknown:
        raise GP29InputError(
            "unknown or ambiguous token(s): " + ", ".join(unknown)
            + "; Latin input must be separated by spaces, commas, semicolons, or pipes"
        )
    return [BY_TOKEN[token] for token in tokens]


def parse(text: str, mode: str = "auto") -> tuple[str, list[RuneEntry]]:
    if mode not in {"auto", "runes", "tokens"}:
        raise GP29InputError(f"unsupported input mode: {mode}")
    selected = mode
    if selected == "auto":
        selected = "runes" if any(character in BY_RUNE for character in text) else "tokens"
    return selected, parse_runes(text) if selected == "runes" else parse_tokens(text)


def calculate(text: str, mode: str = "auto") -> dict[str, object]:
    selected_mode, entries = parse(text, mode)
    values = [entry.prime for entry in entries]
    normalized_runes = "".join(entry.rune for entry in entries)
    payload: dict[str, object] = {
        "schema": "HMS_GP29_RESULT_V1",
        "algorithm": "GP29_PRIME_SUM",
        "input_mode": selected_mode,
        "normalized_runes": normalized_runes,
        "normalized_tokens": [entry.sound for entry in entries],
        "entries": [asdict(entry) for entry in entries],
        "rune_count": len(entries),
        "gp_sum": sum(values),
        "gp_sum_mod29": sum(values) % 29,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def self_test() -> dict[str, object]:
    vectors = (
        ("ᚠ", "runes", 2),
        ("F U/V TH", "tokens", 10),
        (RUNES, "runes", sum(PRIMES)),
    )
    checks = []
    for text, mode, expected in vectors:
        actual = calculate(text, mode)["gp_sum"]
        checks.append({"input": text, "mode": mode, "expected": expected, "actual": actual, "passed": actual == expected})
    return {"schema": "HMS_GP29_SELF_TEST_V1", "passed": sum(item["passed"] for item in checks), "failed": sum(not item["passed"] for item in checks), "checks": checks}
