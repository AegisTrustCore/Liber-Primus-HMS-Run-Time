"""Minimal local HMS Runtime job engine using the public job/result contract."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .gp29 import calculate


SUPPORTED_OPERATIONS = {"gp29.calculate"}


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def create_job(text: str, mode: str = "auto", visibility: str = "PRIVATE") -> dict[str, Any]:
    if visibility not in {"PRIVATE", "PROJECT", "GROUP", "HMS_REVIEW", "PUBLIC"}:
        raise ValueError(f"invalid visibility: {visibility}")
    specification = {
        "schema": "HMS_RUNTIME_JOB_V1",
        "operation": "gp29.calculate",
        "input": {"text": text},
        "parameters": {"mode": mode},
        "visibility": visibility,
    }
    digest = hashlib.sha256(canonical_json(specification)).hexdigest()
    return {**specification, "job_id": f"JOB-{digest[:16].upper()}", "specification_sha256": digest}


def execute_job(job: dict[str, Any]) -> dict[str, Any]:
    operation = job.get("operation")
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported operation: {operation}")
    expected = create_job(
        str(job.get("input", {}).get("text", "")),
        str(job.get("parameters", {}).get("mode", "auto")),
        str(job.get("visibility", "PRIVATE")),
    )
    if job.get("job_id") != expected["job_id"] or job.get("specification_sha256") != expected["specification_sha256"]:
        raise ValueError("job identity does not match its canonical specification")
    output = calculate(expected["input"]["text"], expected["parameters"]["mode"])
    result_core = {
        "schema": "HMS_RUNTIME_RESULT_V1",
        "job_id": expected["job_id"],
        "operation": operation,
        "status": "SUCCEEDED",
        "visibility": expected["visibility"],
        "evidence_label": "CALCULATION_ONLY",
        "output": output,
        "limitations": ["A deterministic GP29 calculation is not a plaintext, translation, or verified Liber Primus result."],
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
