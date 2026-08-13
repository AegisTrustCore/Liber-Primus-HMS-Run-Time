#!/usr/bin/env python3
"""Create a private, preliminary intake catalog for historical research ZIPs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path


CRITICAL = re.compile(r"plaintext|private.?key|onion|endpoint|selector|router|address|candidate.?solve|keyspace", re.I)
PUBLIC = re.compile(r"audit|null|reject|negative|closure|control|blocked|provenance|validator|falsification", re.I)
ADVANCED = re.compile(r"parameter|transducer|recursive|payload|solver|cipher|decode|projection|orbit|lattice", re.I)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(path: Path) -> dict:
    names: list[str] = []
    entry_count = 0
    uncompressed = 0
    nested_zip_count = 0
    nested_zip_unreadable = False
    integrity = "PASS"
    try:
        with zipfile.ZipFile(path) as archive:
            try:
                bad = archive.testzip()
                integrity = "PASS" if bad is None else f"FAIL:{bad}"
            except NotImplementedError:
                integrity = "UNSUPPORTED_COMPRESSION_REVIEW"
            for item in archive.infolist():
                entry_count += 1
                uncompressed += item.file_size
                names.append(item.filename)
                if item.filename.lower().endswith(".zip") and item.file_size <= 25 * 1024 * 1024:
                    nested_zip_count += 1
                    try:
                        with archive.open(item) as nested_stream:
                            with zipfile.ZipFile(io.BytesIO(nested_stream.read())) as nested:
                                names.extend(f"{item.filename}!/{entry.filename}" for entry in nested.infolist())
                    except (OSError, zipfile.BadZipFile, NotImplementedError, RuntimeError):
                        nested_zip_unreadable = True
    except (OSError, zipfile.BadZipFile, NotImplementedError) as exc:
        integrity = f"ERROR:{type(exc).__name__}"
    signal_text = " ".join([path.name, *names])
    signals = []
    if nested_zip_unreadable: signals.append("NESTED_ZIP_UNREADABLE")
    if CRITICAL.search(signal_text): signals.append("CRITICAL_DISCLOSURE_TERM")
    if PUBLIC.search(signal_text): signals.append("BOUNDED_OR_AUDIT_TERM")
    if ADVANCED.search(signal_text): signals.append("ADVANCED_METHOD_TERM")
    has_result = any(re.search(r"result.*\.(json|csv|txt)$", name, re.I) for name in names)
    has_report = any(re.search(r"report.*\.(md|txt|html)$", name, re.I) for name in names)
    has_checksum = any("sha256" in name.lower() or "manifest" in name.lower() for name in names)
    has_code = any(Path(name).suffix.lower() in {".py", ".ipynb", ".js", ".rs"} for name in names)
    if integrity != "PASS": recommendation = "QUARANTINE"
    elif "CRITICAL_DISCLOSURE_TERM" in signals: recommendation = "CRITICAL_HOLD_REVIEW"
    elif "BOUNDED_OR_AUDIT_TERM" in signals and has_result and has_checksum: recommendation = "PUBLIC_CANDIDATE_REVIEW"
    elif has_code and has_result: recommendation = "CARTOGRAPHER_REPRODUCTION_REVIEW"
    elif "ADVANCED_METHOD_TERM" in signals: recommendation = "NAVIGATOR_OR_CARTOGRAPHER_REVIEW"
    else: recommendation = "MANUAL_TRIAGE"
    if has_code and has_result and has_checksum: maturity = "REPRODUCTION_CANDIDATE"
    elif has_result and has_report and has_checksum: maturity = "STRUCTURED_EVIDENCE_CANDIDATE"
    elif has_result or has_report: maturity = "PARTIAL_RECORD"
    else: maturity = "RAW_ARCHIVE"
    return {
        "source_file": str(path),
        "source_name": path.name,
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
        "zip_integrity": integrity,
        "entry_count": entry_count,
        "uncompressed_bytes": uncompressed,
        "nested_zip_count": nested_zip_count,
        "has_result": has_result,
        "has_report": has_report,
        "has_checksum": has_checksum,
        "has_code": has_code,
        "preliminary_maturity": maturity,
        "preliminary_access_review": recommendation,
        "signals": signals,
        "review_state": "UNREVIEWED",
        "final_evidence_class": None,
        "final_access_level": None,
        "notes": "Automated intake only; never publish or tier from this recommendation alone.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overrides", type=Path, help="Private reviewed overrides keyed by source_name")
    args = parser.parse_args()
    paths = sorted({path.resolve() for root in args.roots for path in root.rglob("*.zip")})
    records = [inspect(path) for path in paths]
    if args.overrides:
        overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
        for record in records:
            record.update(overrides.get(record["source_name"], {}))
    args.output.mkdir(parents=True, exist_ok=True)
    json_path = args.output / "archive-intake.json"
    csv_path = args.output / "archive-intake.csv"
    json_path.write_text(json.dumps({"schema_version":"1.0.0","record_count":len(records),"records":records}, indent=2), encoding="utf-8", newline="\n")
    fields = list(records[0]) if records else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = dict(record); row["signals"] = "|".join(record["signals"]); writer.writerow(row)
    summary = Counter(record["preliminary_access_review"] for record in records)
    print(json.dumps({"records":len(records),"recommendations":summary,"json":str(json_path),"csv":str(csv_path)}, indent=2, default=dict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
