"""Local-first HMS Endeavour project and shared result-envelope contracts."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_SCHEMA = "HMS_PROJECT_V1"
RESULT_SCHEMA = "HMS_RESULT_ENVELOPE_V1"
SETTINGS_SCHEMA = "HMS_PROJECT_SETTINGS_V1"
OBJECT_SCHEMA = "HMS_RESEARCH_OBJECT_V1"
PROJECT_VERSION = "1.1.0-dev"
SUPPORTED_PROJECT_VERSIONS = {"0.1.0-dev", "1.0.0-rc.1", PROJECT_VERSION}
VISIBILITIES = {"PRIVATE", "PROJECT", "GROUP", "HMS_REVIEW", "PUBLIC"}
EVIDENCE_LABELS = {"CALCULATION_ONLY", "PROVENANCE_ONLY", "TRAINING_ONLY", "EXPERIMENTAL", "CANDIDATE", "BOUNDED_NEGATIVE", "STRUCTURAL", "KNOWN_CONTROL"}
OBJECT_TYPES = {"NOTE", "BOOKMARK", "REGION", "PAGE_SET", "RUNE_SELECTION", "EVIDENCE", "CLAIM"}
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
    if value.get("application_version") not in SUPPORTED_PROJECT_VERSIONS:
        raise ProjectError(f"unsupported application_version: {value.get('application_version')}")
    return value


def validate_settings(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != SETTINGS_SCHEMA:
        raise ProjectError(f"settings schema must be {SETTINGS_SCHEMA}")
    if set(value) != {"schema", "local_corpus_root"}:
        raise ProjectError("project settings contain unsupported fields")
    root = value.get("local_corpus_root")
    if root is not None and (not isinstance(root, str) or not root.strip()):
        raise ProjectError("local_corpus_root must be a non-empty string or null")
    return value


def create_research_object(
    *, project_id: str, object_type: str, title: str, payload: dict[str, Any],
    page_refs: list[str] | None = None, result_refs: list[str] | None = None,
    visibility: str = "PRIVATE", created_at: str | None = None,
) -> dict[str, Any]:
    object_type = str(object_type).upper()
    if object_type not in OBJECT_TYPES:
        raise ProjectError(f"unsupported research object type: {object_type}")
    if not isinstance(title, str) or not title.strip():
        raise ProjectError("research object title is required")
    if not isinstance(payload, dict):
        raise ProjectError("research object payload must be an object")
    if visibility not in VISIBILITIES:
        raise ProjectError("research object visibility is invalid")
    core = {
        "schema": OBJECT_SCHEMA, "project_id": project_id, "object_type": object_type,
        "title": title.strip(), "created_at": created_at or utc_now(), "visibility": visibility,
        "page_refs": page_refs or [], "result_refs": result_refs or [], "payload": payload,
    }
    digest = hashlib.sha256(canonical_json(core)).hexdigest()
    return {**core, "object_id": f"LOBJ-{digest[:16].upper()}", "object_sha256": digest}


def validate_research_object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != OBJECT_SCHEMA:
        raise ProjectError(f"research object schema must be {OBJECT_SCHEMA}")
    digest = value.get("object_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ProjectError("research object digest is invalid")
    if value.get("object_id") != f"LOBJ-{digest[:16].upper()}":
        raise ProjectError("research object id does not match digest")
    core = {key: item for key, item in value.items() if key not in {"object_id", "object_sha256"}}
    if hashlib.sha256(canonical_json(core)).hexdigest() != digest:
        raise ProjectError("research object digest does not match canonical content")
    if value.get("object_type") not in OBJECT_TYPES or value.get("visibility") not in VISIBILITIES:
        raise ProjectError("research object type or visibility is invalid")
    if not isinstance(value.get("page_refs"), list) or not isinstance(value.get("result_refs"), list):
        raise ProjectError("research object references must be arrays")
    return value


def validate_runtime_job(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != "HMS_RUNTIME_JOB_V1":
        raise ProjectError("runtime job schema is invalid")
    digest = value.get("specification_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ProjectError("runtime job digest is invalid")
    if value.get("job_id") != f"JOB-{digest[:16].upper()}":
        raise ProjectError("runtime job id does not match digest")
    specification = {key: item for key, item in value.items() if key not in {"job_id", "specification_sha256"}}
    if hashlib.sha256(canonical_json(specification)).hexdigest() != digest:
        raise ProjectError("runtime job digest does not match canonical content")
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
        for name_part in ("runs", "results", "objects", "exports"):
            (root / name_part).mkdir()
        _write_json(root / "project.json", project)
        _write_json(root / "settings.json", {"schema":SETTINGS_SCHEMA,"local_corpus_root":None})
        _write_json(root / "index.json", {"schema":"HMS_PROJECT_INDEX_V1","runs":[],"results":[],"objects":[]})
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

    def save_expedition_receipt(self, receipt: dict[str, Any], *, instrument_version: str) -> dict[str, Any]:
        """Persist a verified remote receipt without retaining the submitted plaintext."""
        required = {
            "schema", "receipt_id", "expedition_id", "client_version", "accepted",
            "submission_sha256", "verified_at", "verification_authority",
            "signature_algorithm", "public_key_id", "server_verified",
            "solution_disclosed", "receipt_signature",
        }
        if not isinstance(receipt, dict) or set(receipt) != required:
            raise ProjectError("expedition receipt contract is invalid")
        if receipt.get("schema") != "HMS_EXPEDITION_VERIFICATION_RECEIPT_V2":
            raise ProjectError("expedition receipt schema is invalid")
        if receipt.get("server_verified") is not True or receipt.get("solution_disclosed") is not False:
            raise ProjectError("expedition receipt boundary is invalid")
        if not isinstance(receipt.get("accepted"), bool):
            raise ProjectError("expedition receipt acceptance state is invalid")
        submission_digest = receipt.get("submission_sha256")
        if not isinstance(submission_digest, str) or not re.fullmatch(r"[a-f0-9]{64}", submission_digest):
            raise ProjectError("expedition submission digest is invalid")
        envelope = create_result_envelope(
            project_id=self.project["project_id"],
            instrument_id="expedition-verifier",
            instrument_version=instrument_version,
            operation="REMOTE_SEALED_VERIFICATION",
            payload=receipt,
            parameters={
                "expedition_id": str(receipt.get("expedition_id", "")),
                "client_version": str(receipt.get("client_version", "")),
            },
            input_refs=[{"kind":"SUBMISSION_SHA256", "id":submission_digest}],
            evidence_label="TRAINING_ONLY",
            limitations=[
                "This receipt records a synthetic training-puzzle verification, not a Liber Primus research result.",
                "The submitted plaintext is intentionally not retained in the project Result.",
            ],
            provenance={
                "receipt_id": str(receipt.get("receipt_id", "")),
                "verification_authority": str(receipt.get("verification_authority", "")),
                "public_key_id": str(receipt.get("public_key_id", "")),
            },
        )
        self._immutable_write(Path("results") / f"{envelope['result_id']}.json", envelope)
        self.rebuild_index()
        return envelope

    def read_settings(self) -> dict[str, Any]:
        try:
            return validate_settings(json.loads((self.root / "settings.json").read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ProjectError(f"project settings could not be read: {error}") from error

    def set_local_corpus_root(self, root: Path | None) -> dict[str, Any]:
        value = None if root is None else str(Path(root).resolve())
        if value is not None and not Path(value).is_dir():
            raise ProjectError("local corpus root must be an existing folder")
        settings = validate_settings({"schema": SETTINGS_SCHEMA, "local_corpus_root": value})
        _write_json(self.root / "settings.json", settings)
        self.project["corpus"]["local_root_configured"] = value is not None
        self.project["application_version"] = PROJECT_VERSION
        _write_json(self.root / "project.json", self.project)
        return settings

    def save_research_object(
        self, object_type: str, title: str, payload: dict[str, Any], *,
        page_refs: list[str] | None = None, result_refs: list[str] | None = None,
        visibility: str = "PRIVATE",
    ) -> dict[str, Any]:
        value = create_research_object(
            project_id=self.project["project_id"], object_type=object_type, title=title,
            payload=payload, page_refs=page_refs, result_refs=result_refs, visibility=visibility,
        )
        self._immutable_write(Path("objects") / f"{value['object_id']}.json", value)
        self.rebuild_index()
        return value

    def list_research_objects(self) -> list[dict[str, Any]]:
        values = []
        object_root = self.root / "objects"
        object_root.mkdir(exist_ok=True)
        for path in sorted(object_root.glob("LOBJ-*.json")):
            values.append(validate_research_object(json.loads(path.read_text(encoding="utf-8"))))
        return values

    def export_research_object(self, object_id: str, destination: Path) -> Path:
        source = self.root / "objects" / f"{object_id}.json"
        if not source.is_file():
            raise ProjectError(f"unknown research object: {object_id}")
        value = validate_research_object(json.loads(source.read_text(encoding="utf-8")))
        _write_json(Path(destination), value)
        return Path(destination)

    def rebuild_index(self) -> dict[str, Any]:
        runs = sorted(path.stem for path in (self.root / "runs").glob("JOB-*.json"))
        results = sorted(path.stem for path in (self.root / "results").glob("LRES-*.json"))
        object_root = self.root / "objects"
        object_root.mkdir(exist_ok=True)
        objects = sorted(path.stem for path in object_root.glob("LOBJ-*.json"))
        index = {"schema":"HMS_PROJECT_INDEX_V1","runs":runs,"results":results,"objects":objects}
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

    def audit(self) -> dict[str, Any]:
        problems: list[str] = []
        try:
            validate_project(json.loads((self.root / "project.json").read_text(encoding="utf-8")))
        except (ProjectError, OSError, UnicodeError, json.JSONDecodeError) as error:
            problems.append(f"project.json: {error}")
        try:
            self.read_settings()
        except ProjectError as error:
            problems.append(f"settings.json: {error}")
        for folder, pattern, validator in (
            ("runs", "JOB-*.json", validate_runtime_job),
            ("results", "LRES-*.json", validate_result_envelope),
            ("objects", "LOBJ-*.json", validate_research_object),
        ):
            for path in sorted((self.root / folder).glob(pattern)):
                try:
                    validator(json.loads(path.read_text(encoding="utf-8")))
                except (ProjectError, OSError, UnicodeError, json.JSONDecodeError) as error:
                    problems.append(f"{path.relative_to(self.root).as_posix()}: {error}")
        expected = self.rebuild_index()
        return {
            "schema": "HMS_PROJECT_AUDIT_V1", "project_id": self.project["project_id"],
            "status": "PASS" if not problems else "FAIL", "problems": problems,
            "summary": {"runs": len(expected["runs"]), "results": len(expected["results"]), "objects": len(expected["objects"])},
            "privacy": {"network_access": False, "corpus_files_embedded": False, "local_path_in_backup": False},
        }

    def create_backup(self, destination: Path) -> Path:
        """Create a deterministic metadata backup with local paths and exports excluded."""
        audit = self.audit()
        if audit["status"] != "PASS":
            raise ProjectError("project audit must pass before backup")
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        entries: dict[str, bytes] = {}
        project = dict(self.project)
        project["corpus"] = dict(project["corpus"])
        project["corpus"]["local_root_configured"] = False
        entries["project.json"] = json.dumps(project, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        entries["settings.json"] = json.dumps({"schema": SETTINGS_SCHEMA, "local_corpus_root": None}, indent=2).encode("utf-8") + b"\n"
        entries["index.json"] = (self.root / "index.json").read_bytes()
        for folder, pattern in (("runs", "JOB-*.json"), ("results", "LRES-*.json"), ("objects", "LOBJ-*.json")):
            for path in sorted((self.root / folder).glob(pattern)):
                entries[path.relative_to(self.root).as_posix()] = path.read_bytes()
        checksums = "".join(f"{hashlib.sha256(entries[name]).hexdigest()}  {name}\n" for name in sorted(entries))
        entries["SHA256SUMS"] = checksums.encode("utf-8")
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(entries):
                info = zipfile.ZipInfo(name, date_time=(2026, 8, 15, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, entries[name], compresslevel=9)
        return destination
