"""Minimal local HMS Runtime job engine using the public job/result contract."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .corpus_manifest import validate_verification_report
from .gp29 import calculate


SUPPORTED_OPERATIONS = {"gp29.calculate", "corpus.report.validate", "experiment.gp29.batch", "result.compare"}


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


def create_gp29_experiment_job(
    variants: list[str],
    *,
    mode: str = "letters",
    hypothesis: str,
    target_gp_sum: int,
    visibility: str = "PRIVATE",
) -> dict[str, Any]:
    """Create one bounded, declared GP29 comparison experiment.

    This intentionally supports only an explicit list and a single predeclared
    success gate. It is a reproducible measurement tool, not an optimizer or
    an automatic LP search.
    """
    cleaned = [str(value).strip() for value in variants]
    if not 2 <= len(cleaned) <= 100:
        raise ValueError("a GP29 experiment requires 2 to 100 declared variants")
    if any(not value for value in cleaned):
        raise ValueError("experiment variants cannot be empty")
    hypothesis = str(hypothesis).strip()
    if not hypothesis:
        raise ValueError("declare the hypothesis before running the experiment")
    if isinstance(target_gp_sum, bool) or not isinstance(target_gp_sum, int) or target_gp_sum < 0:
        raise ValueError("target GP sum must be a non-negative integer")
    return _create_job(
        "experiment.gp29.batch",
        {"variants": cleaned},
        {
            "mode": mode,
            "hypothesis": hypothesis,
            "success_gate": {"metric": "gp_sum", "operator": "equals", "target": target_gp_sum},
        },
        visibility,
    )


def create_result_comparison_job(left: dict[str, Any], right: dict[str, Any], visibility: str = "PRIVATE") -> dict[str, Any]:
    """Create a deterministic structural comparison of two validated Result envelopes."""
    from .project import validate_result_envelope

    left_value = validate_result_envelope(left)
    right_value = validate_result_envelope(right)
    if left_value["result_id"] == right_value["result_id"]:
        raise ValueError("select two different Results for comparison")
    return _create_job(
        "result.compare",
        {"left": left_value, "right": right_value},
        {"comparison_scope": "STRUCTURAL_ONLY"},
        visibility,
    )


def execute_job(job: dict[str, Any]) -> dict[str, Any]:
    operation = job.get("operation")
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(f"unsupported operation: {operation}")
    if operation == "gp29.calculate":
        expected = create_job(str(job.get("input", {}).get("text", "")), str(job.get("parameters", {}).get("mode", "auto")), str(job.get("visibility", "PRIVATE")))
    elif operation == "corpus.report.validate":
        report = job.get("input", {}).get("report", {})
        expected = create_corpus_report_job(report if isinstance(report, dict) else {}, str(job.get("visibility", "PRIVATE")))
    elif operation == "experiment.gp29.batch":
        input_value = job.get("input", {})
        parameters = job.get("parameters", {})
        gate = parameters.get("success_gate", {})
        expected = create_gp29_experiment_job(
            input_value.get("variants", []) if isinstance(input_value, dict) else [],
            mode=str(parameters.get("mode", "letters")),
            hypothesis=str(parameters.get("hypothesis", "")),
            target_gp_sum=gate.get("target") if isinstance(gate, dict) else None,
            visibility=str(job.get("visibility", "PRIVATE")),
        )
    else:
        input_value = job.get("input", {})
        expected = create_result_comparison_job(
            input_value.get("left", {}) if isinstance(input_value, dict) else {},
            input_value.get("right", {}) if isinstance(input_value, dict) else {},
            str(job.get("visibility", "PRIVATE")),
        )
    if job.get("job_id") != expected["job_id"] or job.get("specification_sha256") != expected["specification_sha256"]:
        raise ValueError("job identity does not match its canonical specification")
    if operation == "gp29.calculate":
        output = calculate(expected["input"]["text"], expected["parameters"]["mode"])
        evidence_label = "CALCULATION_ONLY"
        limitations = ["A deterministic GP29 calculation is not a plaintext, translation, or verified Liber Primus result."]
    elif operation == "corpus.report.validate":
        output = validate_verification_report(expected["input"]["report"])
        evidence_label = "PROVENANCE_ONLY"
        limitations = ["Report validation confirms canonical report integrity, not corpus authenticity, rights, transcription correctness, or a Liber Primus solution."]
    elif operation == "experiment.gp29.batch":
        gate = expected["parameters"]["success_gate"]
        rows = []
        for index, variant in enumerate(expected["input"]["variants"], start=1):
            calculation = calculate(variant, expected["parameters"]["mode"])
            rows.append(
                {
                    "index": index,
                    "variant": variant,
                    "rune_count": calculation["rune_count"],
                    "gp_sum": calculation["gp_sum"],
                    "gate_passed": calculation["gp_sum"] == gate["target"],
                    "calculation_sha256": hashlib.sha256(canonical_json(calculation)).hexdigest(),
                }
            )
        output = {
            "schema": "HMS_GP29_BATCH_EXPERIMENT_V1",
            "hypothesis": expected["parameters"]["hypothesis"],
            "input_mode": expected["parameters"]["mode"],
            "success_gate": gate,
            "variant_count": len(rows),
            "gate_pass_count": sum(row["gate_passed"] for row in rows),
            "rows": rows,
        }
        evidence_label = "EXPERIMENTAL"
        limitations = [
            "A gate match is a declared numerical observation, not a plaintext, route, translation, or verified Liber Primus solution.",
            "The Runtime does not rank, optimize, or generate candidate variants for this experiment.",
        ]
    else:
        left = expected["input"]["left"]
        right = expected["input"]["right"]
        comparable_fields = ("operation", "status", "visibility", "evidence_label", "parameters", "payload", "limitations")
        field_matches = {field: left.get(field) == right.get(field) for field in comparable_fields}
        output = {
            "schema": "HMS_RESULT_COMPARISON_V1",
            "left_result_id": left["result_id"],
            "right_result_id": right["result_id"],
            "left_instrument": left["instrument"],
            "right_instrument": right["instrument"],
            "matching_fields": [field for field, matches in field_matches.items() if matches],
            "different_fields": [field for field, matches in field_matches.items() if not matches],
            "field_matches": field_matches,
            "left_envelope_sha256": left["envelope_sha256"],
            "right_envelope_sha256": right["envelope_sha256"],
        }
        evidence_label = "STRUCTURAL"
        limitations = [
            "This comparison reports deterministic structural equality and difference only.",
            "It does not assess semantic truth, corroboration, translation quality, or Liber Primus solution status.",
        ]
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
