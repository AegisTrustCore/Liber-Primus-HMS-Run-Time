#!/usr/bin/env python3
"""Create a private, hash-aware inventory of a mixed Liber Primus research tree.

The output contains relative paths and extracted status metadata. Keep the raw
output private; publish only a reviewed aggregate derived from it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".jsonl", ".csv", ".tsv", ".py", ".yaml",
    ".yml", ".toml", ".ini", ".cfg", ".html", ".htm", ".xml", ".asc",
    ".sha256", ".log", ".rst",
}
ARCHIVE_EXTENSIONS = {".zip"}
DOCUMENT_EXTENSIONS = {".pdf", ".epub", ".doc", ".docx"}
SPREADSHEET_EXTENSIONS = {".xlsx", ".xls", ".ods"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
EXECUTABLE_EXTENSIONS = {".exe", ".msi", ".dll"}

LP_NAME_PATTERN = re.compile(
    r"(?i)(liber|primus|cicada|rune|gematria|ars[_ -]?magna|hms[_ -]?endeavou?r|"
    r"page[_ -]?\d+|(?:^|[_ -])lp(?:[_ -]|$)|operation[_ -]?\d+|e\d{2,5})"
)
EXPERIMENT_PATTERN = re.compile(r"(?i)(?<![A-Za-z0-9])E(\d{2,5})(?![A-Za-z0-9])")
PAGE_PATTERN = re.compile(r"(?i)page[_ -]?0*(\d{1,3})")
DECISION_PATTERN = re.compile(
    r"(?im)^\s*(?:decision|classification|evidence_boundary|next_gate|"
    r"plaintext_recovered|key_material_recovered|locator_or_endpoint_recovered)\s*[:=]\s*(.+)$"
)
STATUS_TOKENS = (
    "VERIFIED", "REPRODUCED", "PROMOTED", "POST_DISCOVERY", "REJECTED",
    "REFUTED", "UNSUPPORTED", "NEGATIVE", "NULL", "PROVISIONAL", "COMPLETE",
)
SENSITIVE_PATTERN = re.compile(
    r"(?i)(password|passwd|secret|api[_ -]?key|access[_ -]?token|private[_ -]?key|"
    r"protonmail\.com|invite\.ics|key\.txt$)"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_text(data: bytes) -> str:
    if b"\x00" in data[:4096]:
        return ""
    return data.decode("utf-8", errors="replace")


def classify_extension(suffix: str) -> str:
    if suffix in TEXT_EXTENSIONS:
        return "text"
    if suffix in ARCHIVE_EXTENSIONS:
        return "archive"
    if suffix in DOCUMENT_EXTENSIONS:
        return "document"
    if suffix in SPREADSHEET_EXTENSIONS:
        return "spreadsheet"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in EXECUTABLE_EXTENSIONS:
        return "executable"
    return "other"


def text_signals(text: str, source: str, member: str | None = None) -> dict[str, Any]:
    experiments = sorted({f"E{n}" for n in EXPERIMENT_PATTERN.findall(text)}, key=lambda x: int(x[1:]))
    pages = sorted({int(n) for n in PAGE_PATTERN.findall(text) if int(n) <= 999})
    decisions = []
    for match in DECISION_PATTERN.finditer(text):
        value = " ".join(match.group(1).strip().split())
        if value and value not in decisions:
            decisions.append(value[:1000])
        if len(decisions) >= 50:
            break
    upper = text.upper()
    tokens = [token for token in STATUS_TOKENS if token in upper]
    return {
        "source": source,
        "member": member,
        "experiments": experiments,
        "pages": pages,
        "status_tokens": tokens,
        "decisions": decisions,
    }


def walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def structured_claims(text: str, source: str, member: str | None) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return []
    keys = {
        "decision", "promoted_claim", "evidence_boundary", "next_gate",
        "next_authorized_scope", "plaintext_recovered", "key_material_recovered",
        "locator_or_endpoint_recovered", "plaintext_claimed",
        "plaintext_execution_authorized", "decrypted", "verified", "reproduced",
        "promotion_status", "confidence", "classification", "status", "result_hash",
    }
    found: list[dict[str, Any]] = []
    for obj in walk_dicts(parsed):
        selected = {key: obj[key] for key in keys if key in obj}
        if selected:
            found.append({"source": source, "member": member, **selected})
        if len(found) >= 200:
            break
    return found


def archive_inventory(path: Path, rel: str, max_member_bytes: int) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    claims: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []
    info: dict[str, Any] = {
        "archive_member_count": 0,
        "archive_uncompressed_bytes": 0,
        "archive_text_members_scanned": 0,
        "archive_member_extensions": {},
        "archive_error": None,
    }
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            info["archive_member_count"] = len(members)
            info["archive_uncompressed_bytes"] = sum(item.file_size for item in members)
            ext_counts: Counter[str] = Counter()
            for item in members:
                if item.is_dir():
                    continue
                suffix = PurePosixPath(item.filename).suffix.lower() or "[none]"
                ext_counts[suffix] += 1
                if suffix not in TEXT_EXTENSIONS or item.file_size > max_member_bytes:
                    continue
                try:
                    data = archive.read(item)
                except (RuntimeError, OSError, zipfile.BadZipFile):
                    continue
                text = safe_text(data)
                if not text:
                    continue
                info["archive_text_members_scanned"] += 1
                signal = text_signals(text, rel, item.filename)
                if signal["experiments"] or signal["pages"] or signal["decisions"]:
                    signals.append(signal)
                claims.extend(structured_claims(text, rel, item.filename))
            info["archive_member_extensions"] = dict(ext_counts.most_common())
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        info["archive_error"] = f"{type(exc).__name__}: {exc}"
    return info, signals, claims


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-text-bytes", type=int, default=32 * 1024 * 1024)
    parser.add_argument("--max-archive-member-bytes", type=int, default=16 * 1024 * 1024)
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    files: list[Path] = []
    errors: list[dict[str, str]] = []
    for current, directories, names in os.walk(root):
        directories.sort(key=str.casefold)
        names.sort(key=str.casefold)
        for name in names:
            files.append(Path(current) / name)

    records: list[dict[str, Any]] = []
    all_signals: list[dict[str, Any]] = []
    all_claims: list[dict[str, Any]] = []
    hashes: defaultdict[str, list[str]] = defaultdict(list)
    type_counts: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    total_bytes = 0

    for index, path in enumerate(files, 1):
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        kind = classify_extension(suffix)
        try:
            stat = path.stat()
            digest = sha256_file(path)
        except OSError as exc:
            errors.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue

        total_bytes += stat.st_size
        type_counts[kind] += 1
        extension_counts[suffix or "[none]"] += 1
        hashes[digest].append(rel)
        record: dict[str, Any] = {
            "path": rel,
            "size": stat.st_size,
            "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "sha256": digest,
            "extension": suffix,
            "kind": kind,
            "in_more_research": rel.casefold().startswith("more research/"),
            "name_lp_signal": bool(LP_NAME_PATTERN.search(rel)),
            "sensitive_name_signal": bool(SENSITIVE_PATTERN.search(rel)),
        }

        if kind == "text" and stat.st_size <= args.max_text_bytes:
            try:
                text = safe_text(path.read_bytes())
            except OSError as exc:
                errors.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
                text = ""
            if text:
                signal = text_signals(text, rel)
                record["text_signal"] = signal
                if signal["experiments"] or signal["pages"] or signal["decisions"]:
                    all_signals.append(signal)
                all_claims.extend(structured_claims(text, rel, None))
        elif kind == "archive":
            archive_info, signals, claims = archive_inventory(
                path, rel, args.max_archive_member_bytes
            )
            record.update(archive_info)
            all_signals.extend(signals)
            all_claims.extend(claims)

        records.append(record)
        if index % 100 == 0:
            print(f"inventoried {index}/{len(files)} files", flush=True)

    duplicate_groups = [
        {"sha256": digest, "paths": paths, "copies": len(paths), "wasted_bytes": records_by_path_size(paths, records) * (len(paths) - 1)}
        for digest, paths in hashes.items()
        if len(paths) > 1
    ]
    duplicate_groups.sort(key=lambda item: (-item["wasted_bytes"], item["sha256"]))

    experiment_counts: Counter[str] = Counter()
    page_counts: Counter[int] = Counter()
    decision_count = 0
    for signal in all_signals:
        experiment_counts.update(signal["experiments"])
        page_counts.update(signal["pages"])
        decision_count += len(signal["decisions"])

    summary = {
        "schema": "HMS_PRIVATE_LP_SOURCE_INVENTORY_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root_name": root.name,
        "file_count": len(records),
        "total_bytes": total_bytes,
        "more_research_file_count": sum(1 for record in records if record["in_more_research"]),
        "more_research_bytes": sum(record["size"] for record in records if record["in_more_research"]),
        "kind_counts": dict(type_counts.most_common()),
        "extension_counts": dict(extension_counts.most_common()),
        "lp_name_signal_count": sum(1 for record in records if record["name_lp_signal"]),
        "sensitive_name_signal_count": sum(1 for record in records if record["sensitive_name_signal"]),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_file_count": sum(item["copies"] for item in duplicate_groups),
        "duplicate_wasted_bytes": sum(item["wasted_bytes"] for item in duplicate_groups),
        "archive_count": type_counts["archive"],
        "archive_member_count": sum(record.get("archive_member_count", 0) for record in records),
        "archive_text_members_scanned": sum(record.get("archive_text_members_scanned", 0) for record in records),
        "structured_claim_fragment_count": len(all_claims),
        "decision_line_count": decision_count,
        "experiment_reference_counts": dict(experiment_counts.most_common()),
        "page_reference_counts": {str(page): count for page, count in page_counts.most_common()},
        "error_count": len(errors),
    }

    write_json(output / "summary.json", summary)
    write_jsonl(output / "files.jsonl", records)
    write_jsonl(output / "signals.jsonl", all_signals)
    write_jsonl(output / "claims.jsonl", all_claims)
    write_json(output / "duplicates.json", duplicate_groups)
    write_json(output / "errors.json", errors)
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if not errors else 1


def records_by_path_size(paths: list[str], records: list[dict[str, Any]]) -> int:
    sizes = {record["path"]: record["size"] for record in records}
    return sizes[paths[0]]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    sys.exit(main())
