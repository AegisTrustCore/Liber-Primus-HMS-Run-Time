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
    L: int
    R: int
    N: int
    Q: int


TABLE = tuple(
    RuneEntry(
        index=i,
        rune=rune,
        sound=SOUNDS[i],
        prime=PRIMES[i],
        L=i,
        R=(-i) % 29,
        N=PRIMES[i] % 29,
        Q=PRIMES[i] // 29,
    )
    for i, rune in enumerate(RUNES)
)
BY_RUNE = {entry.rune: entry for entry in TABLE}


def _aliases() -> dict[str, RuneEntry]:
    aliases: dict[str, RuneEntry] = {}
    for entry in TABLE:
        aliases[entry.sound] = entry
        for alias in entry.sound.split("/"):
            aliases[alias] = entry
    return aliases


BY_TOKEN = _aliases()
LATIN_ALIASES = tuple(sorted(BY_TOKEN, key=lambda alias: (-len(alias), alias)))


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


def parse_letters(text: str) -> list[RuneEntry]:
    """Map ordinary English A-Z input one letter at a time.

    This mode deliberately does not combine adjacent letters into GP29 sound
    clusters. For example, ``TH`` is T followed by H; users who intend the
    single TH rune can select Latin-sound or explicit-token mode.
    """
    normalized = unicodedata.normalize("NFKC", text).upper()
    entries: list[RuneEntry] = []
    separators = set(" \t\r\n,.;:!?'-\"()[]{}")
    for position, character in enumerate(normalized):
        if character in separators:
            continue
        if character not in BY_TOKEN or len(character) != 1 or not character.isascii():
            raise GP29InputError(
                f"unsupported English-letter character at position {position + 1}: {character!r}"
            )
        entries.append(BY_TOKEN[character])
    if not entries:
        raise GP29InputError("input contains no English A-Z letters")
    return entries


def parse_latin(text: str) -> list[RuneEntry]:
    """Parse continuous Latin with a frozen longest-alias rule.

    Whitespace and basic sentence punctuation are separators. At each letter,
    the longest canonical GP29 alias wins; equal-length aliases sort
    lexicographically. This is deterministic transliteration, not linguistic
    interpretation.
    """
    normalized = unicodedata.normalize("NFKC", text).upper()
    entries: list[RuneEntry] = []
    position = 0
    separators = set(" \t\r\n,.;:!?'-\"()[]{}")
    while position < len(normalized):
        character = normalized[position]
        if character in separators:
            position += 1
            continue
        alias = next((candidate for candidate in LATIN_ALIASES if normalized.startswith(candidate, position)), None)
        if alias is None:
            raise GP29InputError(f"unsupported Latin-mode character at position {position + 1}: {character!r}")
        entries.append(BY_TOKEN[alias])
        position += len(alias)
    if not entries:
        raise GP29InputError("input contains no GP29 Latin symbols")
    return entries


def parse(text: str, mode: str = "auto") -> tuple[str, list[RuneEntry]]:
    if mode not in {"auto", "letters", "runes", "latin", "tokens"}:
        raise GP29InputError(f"unsupported input mode: {mode}")
    selected = mode
    if selected == "auto":
        if any(character in BY_RUNE for character in text):
            selected = "runes"
        else:
            try:
                return "tokens", parse_tokens(text)
            except GP29InputError:
                selected = "latin"
    parsers = {"letters": parse_letters, "runes": parse_runes, "latin": parse_latin, "tokens": parse_tokens}
    return selected, parsers[selected](text)


def calculate(text: str, mode: str = "auto") -> dict[str, object]:
    selected_mode, entries = parse(text, mode)
    prime_values = [entry.prime for entry in entries]
    l_values = [entry.L for entry in entries]
    r_values = [entry.R for entry in entries]
    n_values = [entry.N for entry in entries]
    q_values = [entry.Q for entry in entries]
    normalized_runes = "".join(entry.rune for entry in entries)
    payload: dict[str, object] = {
        "schema": "HMS_GP29_RESULT_V1",
        "algorithm": "GP29_LR_PRIME_NQ_V1",
        "input_mode": selected_mode,
        "normalized_runes": normalized_runes,
        "normalized_tokens": [entry.sound for entry in entries],
        "entries": [asdict(entry) for entry in entries],
        "rune_count": len(entries),
        "L_sum": sum(l_values),
        "L_sum_mod29": sum(l_values) % 29,
        "R_sum": sum(r_values),
        "R_sum_mod29": sum(r_values) % 29,
        "prime_sum": sum(prime_values),
        "prime_sum_mod29": sum(prime_values) % 29,
        "N_sum": sum(n_values),
        "N_sum_mod29": sum(n_values) % 29,
        "Q_sum": sum(q_values),
        "Q_sum_mod4": sum(q_values) % 4,
        "gp_sum": sum(prime_values),
        "gp_sum_mod29": sum(prime_values) % 29,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def format_human(result: dict[str, object]) -> str:
    """Render a calculation for an ordinary reader without changing its JSON."""
    entries = result.get("entries", [])
    lines = [
        "GP29 CALCULATION",
        "",
        f"Input mode: {result['input_mode']}",
        f"Runes: {result['normalized_runes']}",
        f"Tokens: {' '.join(result['normalized_tokens'])}",
        f"Rune count: {result['rune_count']}",
        "",
        "AGGREGATES",
        f"L sum: {result['L_sum']}  (mod 29 = {result['L_sum_mod29']})",
        f"R sum: {result['R_sum']}  (mod 29 = {result['R_sum_mod29']})",
        f"Prime / GP sum: {result['prime_sum']}  (mod 29 = {result['prime_sum_mod29']})",
        f"N sum: {result['N_sum']}  (mod 29 = {result['N_sum_mod29']})",
        f"Q sum: {result['Q_sum']}  (mod 4 = {result['Q_sum_mod4']})",
        "",
        "PER-RUNE VALUES",
        "#   Rune  Token   L   R  Prime   N   Q",
    ]
    for number, entry in enumerate(entries, 1):
        lines.append(
            f"{number:<3} {entry['rune']:<5} {entry['sound']:<7} "
            f"{entry['L']:>2}  {entry['R']:>2}  {entry['prime']:>5}  {entry['N']:>2}  {entry['Q']:>2}"
        )
    lines.extend(("", f"Result SHA-256: {result['result_sha256']}", "", "Calculation only — not a Liber Primus decode or solve claim."))
    return "\n".join(lines)


def self_test() -> dict[str, object]:
    vectors = (
        ("ᚠ", "runes", 2, [0], [0], [2], [0]),
        ("H", "letters", 23, [8], [21], [23], [0]),
        ("F U/V TH", "tokens", 10, [0, 1, 2], [0, 28, 27], [2, 3, 5], [0, 0, 0]),
        ("THING", "latin", 84, [2, 21], [27, 8], [5, 21], [0, 2]),
        (RUNES, "runes", sum(PRIMES), list(range(29)), [(-i) % 29 for i in range(29)], [p % 29 for p in PRIMES], [p // 29 for p in PRIMES]),
    )
    checks = []
    for text, mode, expected, expected_l, expected_r, expected_n, expected_q in vectors:
        result = calculate(text, mode)
        actual = result["prime_sum"]
        actual_l = [entry["L"] for entry in result["entries"]]
        actual_r = [entry["R"] for entry in result["entries"]]
        actual_n = [entry["N"] for entry in result["entries"]]
        actual_q = [entry["Q"] for entry in result["entries"]]
        passed = (actual, actual_l, actual_r, actual_n, actual_q) == (expected, expected_l, expected_r, expected_n, expected_q)
        checks.append({"input": text, "mode": mode, "expected_prime_sum": expected, "actual_prime_sum": actual, "passed": passed})
    return {"schema": "HMS_GP29_SELF_TEST_V1", "passed": sum(item["passed"] for item in checks), "failed": sum(not item["passed"] for item in checks), "checks": checks}
