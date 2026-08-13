"""Deterministic, read-only corpus manifest creation and verification."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA = "HMS_CORPUS_MANIFEST_V1"
REPORT_SCHEMA = "HMS_CORPUS_VERIFICATION_V1"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class CorpusManifestError(ValueError):
    """Raised when a manifest cannot be interpreted safely."""


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CorpusManifestError("file path must be a non-empty relative POSIX path")
    if "\\" in value:
        raise CorpusManifestError(f"file path must use forward slashes: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise CorpusManifestError(f"unsafe file path: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise CorpusManifestError(f"file path is not canonical: {value!r}")
    return normalized


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict):
        raise CorpusManifestError("manifest root must be an object")
    if manifest.get("schema") != SCHEMA:
        raise CorpusManifestError(f"schema must be {SCHEMA}")
    for field in ("corpus_id", "version"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            raise CorpusManifestError(f"{field} must be a non-empty string")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise CorpusManifestError("files must be a non-empty array")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise CorpusManifestError(f"files[{index}] must be an object")
        path = normalize_relative_path(item.get("path"))
        if path in seen:
            raise CorpusManifestError(f"duplicate file path: {path}")
        seen.add(path)
        digest = item.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise CorpusManifestError(f"files[{index}].sha256 must be lowercase SHA-256")
        size = item.get("bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise CorpusManifestError(f"files[{index}].bytes must be a non-negative integer")
        role = item.get("role", "UNSPECIFIED")
        if not isinstance(role, str) or not role:
            raise CorpusManifestError(f"files[{index}].role must be a non-empty string")
        validated.append({"path": path, "sha256": digest, "bytes": size, "role": role})
    if [item["path"] for item in validated] != sorted(item["path"] for item in validated):
        raise CorpusManifestError("files must be sorted by canonical path")
    return validated


def _safe_target(root: Path, relative: str) -> Path:
    root_resolved = root.resolve(strict=True)
    target = (root_resolved / Path(*PurePosixPath(relative).parts)).resolve(strict=False)
    if not target.is_relative_to(root_resolved):
        raise CorpusManifestError(f"file resolves outside corpus root: {relative}")
    return target


def verify_manifest(manifest: dict[str, Any], root: Path, strict: bool = False) -> dict[str, Any]:
    files = validate_manifest(manifest)
    root = Path(root)
    if not root.is_dir():
        raise CorpusManifestError(f"corpus root is not a directory: {root}")
    results: list[dict[str, Any]] = []
    expected_paths = {item["path"] for item in files}
    counts = {"verified": 0, "missing": 0, "mismatch": 0, "unsafe": 0, "unexpected": 0}
    for item in files:
        try:
            target = _safe_target(root, item["path"])
        except (CorpusManifestError, OSError) as error:
            counts["unsafe"] += 1
            results.append({"path": item["path"], "status": "UNSAFE", "detail": str(error)})
            continue
        if not target.is_file():
            counts["missing"] += 1
            results.append({"path": item["path"], "status": "MISSING"})
            continue
        actual_size = target.stat().st_size
        actual_digest = sha256_file(target)
        status = "VERIFIED" if actual_size == item["bytes"] and actual_digest == item["sha256"] else "MISMATCH"
        counts[status.lower()] += 1
        results.append({
            "path": item["path"], "status": status,
            "expected_bytes": item["bytes"], "actual_bytes": actual_size,
            "expected_sha256": item["sha256"], "actual_sha256": actual_digest,
        })
    unexpected: list[str] = []
    if strict:
        root_resolved = root.resolve(strict=True)
        for path in sorted((item for item in root_resolved.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
            relative = path.relative_to(root_resolved).as_posix()
            if relative not in expected_paths:
                unexpected.append(relative)
        counts["unexpected"] = len(unexpected)
    passed = not any(counts[key] for key in ("missing", "mismatch", "unsafe", "unexpected"))
    report_core = {
        "schema": REPORT_SCHEMA,
        "corpus_id": manifest["corpus_id"],
        "version": manifest["version"],
        "manifest_sha256": hashlib.sha256(canonical_json(manifest)).hexdigest(),
        "strict": strict,
        "status": "PASS" if passed else "FAIL",
        "summary": counts,
        "files": results,
        "unexpected_files": unexpected,
        "limitations": [
            "This report verifies declared local bytes and paths only; it does not establish source authenticity, redistribution rights, transcription correctness, or a Liber Primus solution."
        ],
    }
    return {**report_core, "report_sha256": hashlib.sha256(canonical_json(report_core)).hexdigest()}


def create_manifest(root: Path, corpus_id: str, version: str, exclude: Iterable[str] = ()) -> dict[str, Any]:
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise CorpusManifestError(f"corpus root is not a directory: {root}")
    excluded = {normalize_relative_path(value) for value in exclude}
    files: list[dict[str, Any]] = []
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise CorpusManifestError(f"file resolves outside corpus root: {relative}")
        files.append({"path": relative, "sha256": sha256_file(path), "bytes": path.stat().st_size, "role": "UNSPECIFIED"})
    if not files:
        raise CorpusManifestError("cannot create an empty corpus manifest")
    manifest = {"schema": SCHEMA, "corpus_id": corpus_id, "version": version, "files": files}
    validate_manifest(manifest)
    return manifest
