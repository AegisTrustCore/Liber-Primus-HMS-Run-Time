"""Local-first HMS Endeavour project and shared result-envelope contracts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_SCHEMA = "HMS_PROJECT_V1"
RESULT_SCHEMA = "HMS_RESULT_ENVELOPE_V1"
PROJECT_VERSION = "0.1.0-dev"
VISIBILITIES = {"PRIVATE", "PROJECT", "GROUP", "HMS_REVIEW", "PUBLIC"}
EVIDENCE_LABELS = {"CALCULATION_ONLY", "PROVENANCE_ONLY", "TRAINING_ONLY", "EXPERIMENTAL", "CANDIDATE", "BOUNDED_NEGATIVE", "STRUCTURAL", "KNOWN_CONTROL"}
ID_RE = re.compile(r"^[A-Z]+-[A-F0-9]{16}$")


class ProjectError(ValueError):
    """Raised when a project or result violates the local HMS contract."""


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _identifier(prefix: str, value: object) -> str:
    return f"{prefix}-{hashlib.sha256(canonical_json(value)).hexdigest()[:16].upper()}"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def validate_project(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != PROJECT_SCHEMA:
        raise ProjectError(f"project schema must be {PROJECT_SCHEMA}")
    if not isinstance(value.get("project_id"), str) or not ID_RE.fullmatch(value["project_id"]) or not value["project_id"].startswith("PRJ-"):
        raise ProjectError("project_id is invalid")
    if not isinstance(value.get("name"), str) or not value["name"].strip():
        raise ProjectError("project name is required")
    if value.get("visibility") not in VISIBILITIES:
        raise ProjectError("project visibility is invalid")
    if not isinstance(value.get("created_at"), str) or not value["created_at"]:
        raise ProjectError("project created_at is required")
    corpus = value.get("corpus")
    if not isinstance(corpus, dict) or set(corpus) != {"manifest_ref", "manifest_sha256", "local_root_configured"}:
        raise ProjectError("project corpus reference is invalid")
    if corpus["manifest_ref"] is not None and not isinstance(corpus["manifest_ref"], str):
        raise ProjectError("manifest_ref must be a string or null")
    digest = corpus["manifest_sha256"]
    if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest)):
        raise ProjectError("manifest_sha256 must be lowercase SHA-256 or null")
    if not isinstance(corpus["local_root_configured"], bool):
        raise ProjectError("local_root_configured must be boolean")
    if value.get("application_version") != PROJECT_VERSION:
        raise ProjectError(f"application_version must be {PROJECT_VERSION}")
    return value


def create_project_record(
    name: str,
    *,
    created_at: str | None = None,
    manifest_ref: str | None = None,
    manifest_sha256: str | None = None,
) -> dict[str, Any]:
    timestamp = created_at or utc_now()
    identity = {"name": name.strip(), "created_at": timestamp}
    return validate_project({
        "schema": PROJECT_SCHEMA,
        "project_id": _identifier("PRJ", identity),
        "name": name.strip(),
        "created_at": timestamp,
        "visibility": "PRIVATE",
        "application_version": PROJECT_VERSION,
        "corpus": {
            "manifest_ref": manifest_ref,
            "manifest_sha256": manifest_sha256,
            "local_root_configured": False,
        },
    })


def create_result_envelope(
    *,
    project_id: str,
    instrument_id: str,
    instrument_version: str,
    operation: str,
    payload: object,
    parameters: dict[str, Any] | None = None,
    input_refs: list[dict[str, str]] | None = None,
    evidence_label: str,
    limitations: list[str],
    visibility: str = "PRIVATE",
    provenance: dict[str, str] | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    if not isinstance(project_id, str) or not project_id.startswith("PRJ-"):
        raise ProjectError("project_id is invalid")
    if not all(isinstance(value, str) and value for value in (instrument_id, instrument_version, operation)):
        raise ProjectError("instrument identity and operation are required")
    if evidence_label not in EVIDENCE_LABELS:
        raise ProjectError("evidence label is invalid")
    if visibility not in VISIBILITIES:
        raise ProjectError("visibility is invalid")
    if not limitations or not all(isinstance(item, str) and item for item in limitations):
        raise ProjectError("at least one limitation is required")
    core = {
        "schema": RESULT_SCHEMA,
        "project_id": project_id,
        "created_at": created_at or utc_now(),
        "instrument": {"id": instrument_id, "version": instrument_version},
        "operation": operation,
        "status": "SUCCEEDED",
        "visibility": visibility,
        "evidence_label": evidence_label,
        "input_refs": input_refs or [],
        "parameters": parameters or {},
        "payload": payload,
        "provenance": provenance or {},
        "limitations": limitations,
    }
    digest = hashlib.sha256(canonical_json(core)).hexdigest()
    return {**core, "result_id": f"LRES-{digest[:16].upper()}", "envelope_sha256": digest}


def validate_result_envelope(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != RESULT_SCHEMA:
        raise ProjectError(f"result schema must be {RESULT_SCHEMA}")
    claimed = value.get("envelope_sha256")
    result_id = value.get("result_id")
    if not isinstance(claimed, str) or not re.fullmatch(r"[a-f0-9]{64}", claimed):
        raise ProjectError("envelope_sha256 is invalid")
    if not isinstance(result_id, str) or result_id != f"LRES-{claimed[:16].upper()}":
        raise ProjectError("result_id does not match envelope digest")
    core = {key: item for key, item in value.items() if key not in {"result_id", "envelope_sha256"}}
    actual = hashlib.sha256(canonical_json(core)).hexdigest()
    if actual != claimed:
        raise ProjectError("result envelope digest does not match canonical content")
    if value.get("evidence_label") not in EVIDENCE_LABELS or value.get("visibility") not in VISIBILITIES:
        raise ProjectError("result evidence or visibility is invalid")
    return value


class ProjectStore:
    """Persistent local store with immutable Run and Result files."""

    def __init__(self, root: Path, project: dict[str, Any]) -> None:
        self.root = root.resolve()
        self.project = validate_project(project)

    @classmethod
    def create(
        cls,
        root: Path,
        name: str,
        *,
        created_at: str | None = None,
        manifest_ref: str | None = None,
        manifest_sha256: str | None = None,
    ) -> "ProjectStore":
        root = Path(root)
        if root.exists() and any(root.iterdir()):
            raise ProjectError("project folder must be empty")
        root.mkdir(parents=True, exist_ok=True)
        project = create_project_record(name, created_at=created_at, manifest_ref=manifest_ref, manifest_sha256=manifest_sha256)
        for name_part in ("runs", "results", "exports", "notes"):
            (root / name_part).mkdir()
        _write_json(root / "project.json", project)
        _write_json(root / "settings.json", {"schema":"HMS_PROJECT_SETTINGS_V1","local_corpus_root":None})
        _write_json(root / "index.json", {"schema":"HMS_PROJECT_INDEX_V1","runs":[],"results":[]})
        return cls(root, project)

    @classmethod
    def open(cls, root: Path) -> "ProjectStore":
        root = Path(root)
        try:
            project = json.loads((root / "project.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ProjectError(f"project could not be opened: {error}") from error
        return cls(root, project)

    def _immutable_write(self, relative: Path, value: object) -> Path:
        target = (self.root / relative).resolve()
        if not target.is_relative_to(self.root):
            raise ProjectError("project write resolved outside project root")
        rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if target.exists():
            if target.read_text(encoding="utf-8") != rendered:
                raise ProjectError(f"immutable project object already exists: {relative.as_posix()}")
            return target
        _write_json(target, value)
        return target

    def save_execution(
        self,
        job: dict[str, Any],
        runtime_result: dict[str, Any],
        *,
        instrument_id: str,
        instrument_version: str,
    ) -> dict[str, Any]:
        job_id = str(job.get("job_id", ""))
        if not ID_RE.fullmatch(job_id):
            raise ProjectError("runtime job_id is invalid")
        self._immutable_write(Path("runs") / f"{job_id}.json", job)
        envelope = create_result_envelope(
            project_id=self.project["project_id"],
            instrument_id=instrument_id,
            instrument_version=instrument_version,
            operation=str(runtime_result.get("operation", "")),
            payload=runtime_result.get("output"),
            parameters=job.get("parameters", {}),
            input_refs=[{"kind":"RUNTIME_JOB","id":job_id}],
            evidence_label=str(runtime_result.get("evidence_label", "")),
            limitations=list(runtime_result.get("limitations", [])),
            visibility=str(runtime_result.get("visibility", "PRIVATE")),
            provenance={
                "job_id": job_id,
                "specification_sha256": str(job.get("specification_sha256", "")),
                "runtime_result_sha256": str(runtime_result.get("result_sha256", "")),
            },
        )
        self._immutable_write(Path("results") / f"{envelope['result_id']}.json", envelope)
        self.rebuild_index()
        return envelope

    def rebuild_index(self) -> dict[str, Any]:
        runs = sorted(path.stem for path in (self.root / "runs").glob("JOB-*.json"))
        results = sorted(path.stem for path in (self.root / "results").glob("LRES-*.json"))
        index = {"schema":"HMS_PROJECT_INDEX_V1","runs":runs,"results":results}
        _write_json(self.root / "index.json", index)
        return index

    def list_results(self) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for path in sorted((self.root / "results").glob("LRES-*.json")):
            values.append(validate_result_envelope(json.loads(path.read_text(encoding="utf-8"))))
        return values

    def export_result(self, result_id: str, destination: Path) -> Path:
        source = self.root / "results" / f"{result_id}.json"
        if not source.is_file():
            raise ProjectError(f"unknown result: {result_id}")
        value = validate_result_envelope(json.loads(source.read_text(encoding="utf-8")))
        _write_json(Path(destination), value)
        return Path(destination)
