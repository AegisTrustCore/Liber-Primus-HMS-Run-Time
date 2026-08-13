"""Minimal local HMS Runtime job engine using the public job/result contract."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .corpus_manifest import validate_verification_report
from .gp29 import calculate


SUPPORTED_OPERATIONS = {"gp29.calculate", "corpus.report.validate"}


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _create_job(operation: str, input_value: dict[str, Any], parameters: dict[str, Any], visibility: str) -> dict[str, Any]:
    if visibility not in {"PRIVATE", "PROJECT", "GROUP", "HMS_REVIEW", "PUBLIC"}:
        raise ValueError(f"invalid visibility: {visibility}")
    specification = {
        "schema": "HMS_RUNTIME_JOB_V1",
        "operation": operation,
        "input": input_value,
        "parameters": parameters,
        "visibility": visibility,
    }
    digest = hashlib.sha256(canonical_json(specification)).hexdigest()
    return {**specification, "job_id": f"JOB-{digest[:16].upper()}", "specification_sha256": digest}


def create_job(text: str, mode: str = "auto", visibility: str = "PRIVATE") -> dict[str, Any]:
    return _create_job("gp29.calculate", {"text": text}, {"mode": mode}, visibility)


def create_corpus_report_job(report: dict[str, Any], visibility: str = "PRIVATE") -> dict[str, Any]:
    return _create_job("corpus.report.validate", {"report": report}, {}, visibility)


def execute_job(job: dict[str, Any]) -> dict[str, Any]:
    operation = job.get("operation")
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported operation: {operation}")
    if operation == "gp29.calculate":
        expected = create_job(str(job.get("input", {}).get("text", "")), str(job.get("parameters", {}).get("mode", "auto")), str(job.get("visibility", "PRIVATE")))
    else:
        report = job.get("input", {}).get("report", {})
        expected = create_corpus_report_job(report if isinstance(report, dict) else {}, str(job.get("visibility", "PRIVATE")))
    if job.get("job_id") != expected["job_id"] or job.get("specification_sha256") != expected["specification_sha256"]:
        raise ValueError("job identity does not match its canonical specification")
    if operation == "gp29.calculate":
        output = calculate(expected["input"]["text"], expected["parameters"]["mode"])
        evidence_label = "CALCULATION_ONLY"
        limitations = ["A deterministic GP29 calculation is not a plaintext, translation, or verified Liber Primus result."]
    else:
        output = validate_verification_report(expected["input"]["report"])
        evidence_label = "PROVENANCE_ONLY"
        limitations = ["Report validation confirms canonical report integrity, not corpus authenticity, rights, transcription correctness, or a Liber Primus solution."]
    result_core = {
        "schema": "HMS_RUNTIME_RESULT_V1",
        "job_id": expected["job_id"],
        "operation": operation,
        "status": "SUCCEEDED",
        "visibility": expected["visibility"],
        "evidence_label": evidence_label,
        "output": output,
        "limitations": limitations,
    }
    result_digest = hashlib.sha256(canonical_json(result_core)).hexdigest()
    return {**result_core, "result_sha256": result_digest}


@dataclass
class RuntimeStore:
    """In-memory reference queue; no authentication, networking, or persistence."""

    jobs: dict[str, dict[str, Any]]
    results: dict[str, dict[str, Any]]

    def __init__(self) -> None:
        self.jobs = {}
        self.results = {}

    def submit(self, job: dict[str, Any]) -> str:
        job_id = str(job["job_id"])
        self.jobs[job_id] = job
        return job_id

    def run(self, job_id: str) -> dict[str, Any]:
        result = execute_job(self.jobs[job_id])
        self.results[job_id] = result
        return result

    def get_result(self, job_id: str) -> dict[str, Any] | None:
        return self.results.get(job_id)
