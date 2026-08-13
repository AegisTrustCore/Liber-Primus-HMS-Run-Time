#!/usr/bin/env python3
"""Generate the static HMS Research Archive from canonical package manifests."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import sys
import zipfile
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
EVIDENCE_CLASSES = {
    "VERIFIED", "KNOWN_CONTROL", "STRUCTURAL", "BOUNDED_NEGATIVE",
    "HYPOTHESIS", "RESEARCH_PATH", "CORRECTION", "RETRACTED",
}
REPRODUCTION_STATES = {
    "NOT_ATTEMPTED", "PARTIAL", "REPRODUCED",
    "FAILED_REPRODUCTION", "HISTORICAL_ONLY",
}


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2))


def canonical_file_hash(path: Path) -> str:
    data = path.read_bytes()
    if b"\0" not in data:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def badge(value: str) -> str:
    return f'<span class="badge">{html.escape(value.replace("_", " "))}</span>'


def list_html(items: list[str], empty: str = "None recorded.") -> str:
    if not items:
        return f"<p>{html.escape(empty)}</p>"
    return "<ul>" + "".join(f"<li>{html.escape(str(item))}</li>" for item in items) + "</ul>"


def shell(title: str, object_id: str, status: str, body: str, script: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(object_id)} — {html.escape(title)}</title>
<style>
:root{{--bg:#0b1014;--panel:#121a20;--ink:#e7edf0;--muted:#9aabb4;--cyan:#64d8e8;--brass:#d1ad62;--line:#263740}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}}
main{{max-width:1040px;margin:auto;padding:3rem 1.25rem}} header{{border-bottom:1px solid var(--line);padding-bottom:1.5rem;margin-bottom:2rem}}
h1{{margin:.2rem 0;color:var(--cyan);font-size:clamp(1.8rem,4vw,3rem)}} h2{{color:var(--brass);margin-top:2rem;font-size:1.05rem;letter-spacing:.08em}}
a{{color:var(--cyan)}} .eyebrow{{color:var(--muted);letter-spacing:.16em}} .badge{{display:inline-block;border:1px solid var(--brass);border-radius:999px;padding:.18rem .65rem;margin:.2rem .35rem .2rem 0;color:var(--brass);font-size:.78rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}} section,.card{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:1rem 1.2rem}}
table{{width:100%;border-collapse:collapse}} td,th{{padding:.55rem;border-bottom:1px solid var(--line);text-align:left}} code{{overflow-wrap:anywhere}} input,select{{background:var(--panel);color:var(--ink);border:1px solid var(--line);padding:.7rem;border-radius:4px}}
</style></head><body><main><header><div class="eyebrow">HMS ENDEAVOUR · RESEARCH ARCHIVE</div><h1>{html.escape(object_id)}</h1><p>{html.escape(title)}</p>{badge(status)}</header>{body}</main>{script}</body></html>"""


def run_text(run: dict) -> str:
    metrics = "\n".join(f"- {m['name']}: {m['value']} {m['unit']}" for m in run["output"]["metrics"])
    return f"""HMS ENDEAVOUR
{run['id']}

TITLE:
{run['title']}

STATUS:
{run['evidence_class']} / {run['reproduction_status']}

SUMMARY:
{run['summary']}

WHY THIS RUN EXISTS:
{run['why_run']}

TARGET:
{run['target']['description']}

METHOD:
{run['pipeline']['description']}

PARAMETERS:
{json.dumps(run['parameters'], ensure_ascii=False, sort_keys=True)}

RESULT:
{run['output']['summary']}

METRICS:
{metrics}

CONTROLS:
{chr(10).join('- ' + item for item in run['controls'])}

INTERPRETATION:
{run['interpretation']}

LIMITATIONS:
{chr(10).join('- ' + item for item in run['limitations'])}

SOURCE:
{run['provenance']['source_system']} / {run['provenance']['historical_source']['original_identifier']}
"""


def run_html(run: dict) -> str:
    inputs = "".join(f"<tr><td>{html.escape(i['id'])}</td><td><code>{html.escape(i['path'])}</code></td><td>{badge(i['availability'])}</td></tr>" for i in run["inputs"])
    metrics = "".join(f"<tr><td>{html.escape(m['name'])}</td><td>{html.escape(str(m['value']))}</td><td>{html.escape(m['unit'])}</td></tr>" for m in run["output"]["metrics"])
    related = " ".join(f'<a href="../../results/{rid}/result.html">{rid}</a>' for rid in run["result_ids"])
    body = f"""<div>{badge(run['evidence_class'])}{badge(run['reproduction_status'])}{badge(run['migration_confidence'] + ' MIGRATION')}</div>
<section><h2>SUMMARY</h2><p>{html.escape(run['summary'])}</p></section>
<div class="grid"><section><h2>WHY THIS RUN EXISTS</h2><p>{html.escape(run['why_run'])}</p></section><section><h2>TARGET</h2><p>{html.escape(run['target']['description'])}</p></section></div>
<section><h2>INPUTS</h2><table><tr><th>ID</th><th>Path</th><th>Availability</th></tr>{inputs}</table></section>
<section><h2>PIPELINE / METHOD</h2><p>{html.escape(run['pipeline']['description'])}</p><p><code>{html.escape(run['pipeline']['implementation'])}</code></p></section>
<section><h2>PARAMETERS</h2><pre>{html.escape(json.dumps(run['parameters'], ensure_ascii=False, indent=2))}</pre></section>
<section><h2>OUTPUT</h2><p>{html.escape(run['output']['summary'])}</p><pre>{html.escape(run['output']['stdout'])}</pre></section>
<section><h2>METRICS</h2><table><tr><th>Metric</th><th>Value</th><th>Unit</th></tr>{metrics}</table></section>
<div class="grid"><section><h2>CONTROLS</h2>{list_html(run['controls'])}</section><section><h2>INTERPRETATION</h2><p>{html.escape(run['interpretation'])}</p></section></div>
<section><h2>LIMITATIONS</h2>{list_html(run['limitations'])}</section>
<section><h2>RELATED RESULT</h2><p>{related}</p></section>
<section><h2>PROVENANCE</h2><p>Source system: <code>{html.escape(run['provenance']['source_system'])}</code></p><p>Environment: <code>{html.escape(run['provenance']['environment_manifest'])}</code></p><p>Raw historical output: {badge(run['raw_artifacts']['availability'])}</p></section>
<section><h2>REPRODUCE</h2><pre>{html.escape(run['parameters']['command'])}</pre></section>
<section><h2>RAW FILES & DOWNLOAD</h2><p><a href="manifest.json">Manifest JSON</a> · <a href="result.json">Result JSON</a> · <a href="output/metrics.csv">Metrics CSV</a> · <a href="provenance/provenance.json">Provenance</a> · <a href="{run['id']}.zip">Download package</a></p></section>"""
    return shell(run["title"], run["id"], run["publication_status"], body)


def package_run(path: Path, run: dict) -> None:
    result = {"run_id": run["id"], "status": run["output"]["status"], "result_class": run["output"]["result_class"], "summary": run["output"]["summary"], "metrics": {m["name"]: m["value"] for m in run["output"]["metrics"]}, "acceptance": run["output"]["acceptance"]}
    write_json(path / "result.json", result)
    write_json(path / "output" / "result.json", result)
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=["name", "value", "unit"], lineterminator="\n")
    writer.writeheader(); writer.writerows(run["output"]["metrics"])
    write_text(path / "output" / "metrics.csv", buffer.getvalue())
    write_text(path / "output" / "stdout.txt", run["output"]["stdout"])
    write_json(path / "input" / "input-manifest.json", {"run_id": run["id"], "inputs": run["inputs"]})
    write_json(path / "config" / "parameters.json", run["parameters"])
    write_json(path / "config" / "pipeline.json", run["pipeline"])
    write_json(path / "config" / "environment.json", {"manifest": run["provenance"]["environment_manifest"], "availability": "PUBLIC"})
    write_json(path / "provenance" / "provenance.json", run["provenance"])
    write_text(path / "result.txt", run_text(run))
    write_text(path / "result.html", run_html(run))
    write_text(path / "README.md", f"# {run['id']} — {run['title']}\n\n{run['summary']}\n\n- [Readable result](result.html)\n- [Plain text](result.txt)\n- [Canonical manifest](manifest.json)\n- [Structured result](result.json)\n- [Metrics](output/metrics.csv)\n- [Provenance](provenance/provenance.json)\n- [Download package]({run['id']}.zip)\n\n## Reproduce\n\n```text\n{run['parameters']['command']}\n```\n\n## Limits\n\n" + "\n".join(f"- {item}" for item in run["limitations"]))
    finalize_package(path, f"{run['id']}.zip")


def result_text(result: dict) -> str:
    return f"""HMS ENDEAVOUR
{result['id']}

TITLE:
{result['title']}

STATUS:
{result['evidence_class']} / {result['reproduction_status']}

CLAIM:
{result['claim']}

WHY IT MATTERS:
{result['why_it_matters']}

SUPPORTED BY:
{chr(10).join(result['supporting_runs'])}

WHAT THIS DOES NOT CLAIM:
{chr(10).join('- ' + item for item in result['does_not_claim'])}

LIMITATIONS:
{chr(10).join('- ' + item for item in result['limitations'])}

CURRENT INTERPRETATION:
{result['current_interpretation']}
"""


def result_html(result: dict) -> str:
    runs = " ".join(f'<a href="../../runs/{rid}/result.html">{rid}</a>' for rid in result["supporting_runs"])
    body = f"""<div>{badge(result['evidence_class'])}{badge(result['reproduction_status'])}</div>
<section><h2>CLAIM</h2><p>{html.escape(result['claim'])}</p></section>
<section><h2>WHY IT MATTERS</h2><p>{html.escape(result['why_it_matters'])}</p></section>
<section><h2>WHAT SUPPORTS IT</h2><p>{runs}</p></section>
<div class="grid"><section><h2>CONTROLS</h2>{list_html(result['controls'])}</section><section><h2>CONTRADICTIONS</h2>{list_html(result['contradictions'])}</section></div>
<section><h2>LIMITATIONS</h2>{list_html(result['limitations'])}</section>
<section><h2>WHAT IT DOES NOT CLAIM</h2>{list_html(result['does_not_claim'])}</section>
<section><h2>REPRODUCTION</h2><p>{badge(result['reproduction_status'])}</p></section>
<section><h2>CURRENT INTERPRETATION</h2><p>{html.escape(result['current_interpretation'])}</p></section>
<section><h2>CORRECTIONS / SUPERSESSIONS</h2>{list_html(result['corrections'] + result['superseded_by'])}</section>
<section><h2>PROOFLINK / PROOFLOCK</h2>{list_html(result['prooflinks'])}</section>
<section><h2>DOWNLOAD</h2><p><a href="manifest.json">Manifest JSON</a> · <a href="evidence.json">Evidence JSON</a> · <a href="supporting-runs.json">Supporting runs</a> · <a href="{result['id']}.zip">Download package</a></p></section>"""
    return shell(result["title"], result["id"], result["publication_status"], body)


def package_result(path: Path, result: dict) -> None:
    write_json(path / "result.json", {"result_id": result["id"], "evidence_class": result["evidence_class"], "claim": result["claim"], "current_interpretation": result["current_interpretation"]})
    write_json(path / "evidence.json", {"result_id": result["id"], "controls": result["controls"], "contradictions": result["contradictions"], "prooflinks": result["prooflinks"]})
    write_json(path / "supporting-runs.json", {"result_id": result["id"], "run_ids": result["supporting_runs"]})
    write_text(path / "result.txt", result_text(result))
    write_text(path / "result.html", result_html(result))
    write_text(path / "README.md", f"# {result['id']} — {result['title']}\n\n{result['claim']}\n\n- [Readable result](result.html)\n- [Plain text](result.txt)\n- [Canonical manifest](manifest.json)\n- [Evidence](evidence.json)\n- [Supporting runs](supporting-runs.json)\n- [Download package]({result['id']}.zip)\n\n## Does not claim\n\n" + "\n".join(f"- {item}" for item in result["does_not_claim"]))
    finalize_package(path, f"{result['id']}.zip")


def package_capsule(path: Path, cap: dict) -> None:
    run_links = " ".join(f'<a href="../../runs/{item}/result.html">{item}</a>' for item in cap["run_ids"])
    result_links = " ".join(f'<a href="../../results/{item}/result.html">{item}</a>' for item in cap["result_ids"])
    body = f'''<section><h2>SUMMARY</h2><p>{html.escape(cap['summary'])}</p></section><section><h2>RUNS</h2><p>{run_links}</p></section><section><h2>RESULTS</h2><p>{result_links}</p></section><section><h2>CONTROLS</h2>{list_html(cap['control_ids'])}</section><section><h2>NEGATIVES</h2>{list_html(cap['negative_result_ids'])}</section><section><h2>CORRECTIONS</h2>{list_html(cap['correction_ids'])}</section><section><h2>LIMITATIONS</h2>{list_html(cap['limitations'])}</section><section><h2>DOWNLOAD</h2><p><a href="manifest.json">Manifest JSON</a> · <a href="{cap['id']}.zip">Download package</a></p></section>'''
    write_text(path / "result.html", shell(cap["title"], cap["id"], cap["publication_status"], body))
    write_text(path / "result.txt", f"HMS ENDEAVOUR\n{cap['id']}\n\n{cap['title']}\n\n{cap['summary']}\n\nRUNS:\n" + "\n".join(cap["run_ids"]) + "\n\nRESULTS:\n" + "\n".join(cap["result_ids"]))
    write_text(path / "README.md", f"# {cap['id']} — {cap['title']}\n\n{cap['summary']}\n\n- [Readable capsule](result.html)\n- [Canonical manifest](manifest.json)\n- [Download package]({cap['id']}.zip)")
    finalize_package(path, f"{cap['id']}.zip")


def finalize_package(path: Path, zip_name: str) -> None:
    zip_path = path / zip_name
    files = sorted(p for p in path.rglob("*") if p.is_file() and p.name != "SHA256SUMS" and p != zip_path)
    lines = [f"{canonical_file_hash(file)}  {file.relative_to(path).as_posix()}" for file in files]
    write_text(path / "SHA256SUMS", "\n".join(lines))
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(p for p in path.rglob("*") if p.is_file() and p != zip_path):
            info = zipfile.ZipInfo(f"{path.name}/{file.relative_to(path).as_posix()}", date_time=(2026, 8, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())


def index_html(kind: str, entries: list[dict]) -> str:
    cards = []
    for item in entries:
        status = item.get("evidence_class", item.get("publication_status", "PUBLISHED"))
        searchable = " ".join([item["id"], item["title"], status, item.get("reproduction_status", ""), " ".join(item.get("finding_tags", []))]).lower()
        cards.append(f'<article class="card item" data-status="{html.escape(status)}" data-search="{html.escape(searchable)}"><h2><a href="{item["id"]}/result.html">{item["id"]}</a></h2><h3>{html.escape(item["title"])}</h3>{badge(status)}{badge(item.get("reproduction_status", "")) if item.get("reproduction_status") else ""}<p>{html.escape(item.get("summary", item.get("claim", item.get("purpose", ""))))}</p><a href="{item["id"]}/{item["id"]}.zip">Download</a></article>')
    options = "".join(f'<option value="{s}">{s.replace("_", " ")}</option>' for s in sorted({item.get("evidence_class", item.get("publication_status", "PUBLISHED")) for item in entries}))
    script = """<script>const q=document.querySelector('#q'),s=document.querySelector('#status');function f(){document.querySelectorAll('.item').forEach(x=>x.hidden=!(x.dataset.search.includes(q.value.toLowerCase())&&(!s.value||x.dataset.status===s.value)))}q.addEventListener('input',f);s.addEventListener('change',f)</script>"""
    body = f'<section><h2>SEARCH & FILTER</h2><p><input id="q" aria-label="Search" placeholder="ID, title, method, tag…"> <select id="status"><option value="">All statuses</option>{options}</select></p></section><div class="grid">{"".join(cards)}</div>'
    return shell(f"HMS Research {kind.title()}", kind.upper(), f"{len(entries)} OBJECTS", body, script)


def write_index(directory: Path, kind: str, entries: list[dict]) -> None:
    rows = []
    for item in entries:
        package = directory / item["id"] / f"{item['id']}.zip"
        rows.append({"id": item["id"], "title": item["title"], "status": item.get("evidence_class", item.get("publication_status")), "reproduction_status": item.get("reproduction_status"), "page": item.get("target", {}).get("page") if isinstance(item.get("target"), dict) else None, "method": item.get("method_family"), "capsule": item.get("capsule_id"), "package": f"{item['id']}/{item['id']}.zip", "package_sha256": canonical_file_hash(package), "result_page": f"{item['id']}/result.html"})
    write_json(directory / "index.json", {"schema_version": "1.0.0", "object_type": kind.upper(), "count": len(rows), "entries": rows})
    fields = ["id", "title", "status", "reproduction_status", "page", "method", "capsule", "package", "package_sha256", "result_page"]
    buffer = StringIO(newline=""); writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    write_text(directory / "index.csv", buffer.getvalue())
    write_text(directory / "index.html", index_html(kind, entries))
    write_text(directory / "README.md", f"# HMS Research {kind.title()}\n\nThe JSON index is authoritative for discovery; HTML, CSV, and Markdown are generated views.\n\n- [Searchable offline index](index.html)\n- [Machine index](index.json)\n- [CSV index](index.csv)\n\n" + "\n".join(f"- [{item['id']} — {item['title']}]({item['id']}/README.md)" for item in entries))


def package_runset(path: Path, item: dict, objects: dict[str, dict]) -> None:
    bundle_dir = path / "bundles"
    if bundle_dir.exists(): shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)
    members = []
    for kind, ids in (("runs", item["run_ids"]), ("results", item["result_ids"]), ("capsules", item["capsule_ids"])):
        for object_id in ids:
            source = RESEARCH / kind / object_id / f"{object_id}.zip"
            target = bundle_dir / source.name
            shutil.copyfile(source, target)
            members.append({"id": object_id, "type": kind[:-1].upper(), "path": f"bundles/{source.name}", "sha256": canonical_file_hash(target)})
    write_json(path / "downloads.json", {"run_set_id": item["id"], "members": members})
    body = f'''<section><h2>PURPOSE</h2><p>{html.escape(item['purpose'])}</p></section><section><h2>RUNS</h2>{list_html(item['run_ids'])}</section><section><h2>RESULTS</h2>{list_html(item['result_ids'])}</section><section><h2>CAPSULES</h2>{list_html(item['capsule_ids'])}</section><section><h2>SELECTION NOTES</h2>{list_html(item['selection_notes'])}</section><section><h2>RELEASE STATE</h2><p>{html.escape(item['release_notes'])}</p></section><section><h2>DOWNLOAD</h2><p><a href="{item['id']}.zip">Download complete staged run set</a> · <a href="downloads.json">Member hashes</a></p></section>'''
    write_text(path / "result.html", shell(item["title"], item["id"], item["publication_status"], body))
    write_text(path / "result.txt", f"HMS ENDEAVOUR\n{item['id']}\n\n{item['title']}\n\nSTATUS: {item['publication_status']}\n\n{item['purpose']}\n\nRUNS:\n" + "\n".join(item["run_ids"]) + "\n\nRESULTS:\n" + "\n".join(item["result_ids"]))
    write_text(path / "README.md", f"# {item['id']} — {item['title']}\n\n**Status: {item['publication_status']}**\n\n{item['purpose']}\n\n- [Readable overview](result.html)\n- [Member downloads and hashes](downloads.json)\n- [Complete staged bundle]({item['id']}.zip)")
    finalize_package(path, f"{item['id']}.zip")


def manifests(kind: str) -> list[tuple[Path, dict]]:
    return [(path.parent, load(path)) for path in sorted((RESEARCH / kind).glob("*/manifest.json"))]


def validate_archive() -> list[str]:
    errors: list[str] = []
    runs = {item["id"]: (path, item) for path, item in manifests("runs")}
    results = {item["id"]: (path, item) for path, item in manifests("results")}
    capsules = {item["id"]: (path, item) for path, item in manifests("capsules")}
    runsets = {item["id"]: (path, item) for path, item in manifests("runsets")}
    for object_id, (path, item) in runs.items():
        if path.name != object_id or not re.fullmatch(r"RUN-\d{4,}", object_id): errors.append(f"{object_id}: invalid run path or ID")
        if item.get("classification") != "PUBLIC" or item.get("publication_status") != "PUBLISHED": errors.append(f"{object_id}: public run must be PUBLIC/PUBLISHED")
        if item.get("evidence_class") not in EVIDENCE_CLASSES: errors.append(f"{object_id}: invalid evidence_class")
        if item.get("reproduction_status") not in REPRODUCTION_STATES: errors.append(f"{object_id}: invalid reproduction_status")
        for rid in item.get("result_ids", []):
            if rid not in results: errors.append(f"{object_id}: missing result {rid}")
        if item.get("capsule_id") not in capsules: errors.append(f"{object_id}: missing capsule {item.get('capsule_id')}")
        for source in item.get("inputs", []):
            source_path = ROOT / source.get("path", "")
            if source.get("availability") == "PUBLIC" and not source_path.is_file(): errors.append(f"{object_id}: missing public input {source.get('path')}")
            expected = source.get("sha256")
            if expected and source_path.is_file() and canonical_file_hash(source_path) != expected: errors.append(f"{object_id}: input hash mismatch for {source.get('path')}")
    for object_id, (_, item) in results.items():
        if item.get("classification") != "PUBLIC" or item.get("publication_status") != "PUBLISHED": errors.append(f"{object_id}: public result must be PUBLIC/PUBLISHED")
        for rid in item.get("supporting_runs", []):
            if rid not in runs: errors.append(f"{object_id}: missing supporting run {rid}")
            elif object_id not in runs[rid][1].get("result_ids", []): errors.append(f"{object_id}: run {rid} lacks reciprocal link")
    for object_id, (_, item) in capsules.items():
        for rid in item.get("run_ids", []):
            if rid not in runs: errors.append(f"{object_id}: missing run {rid}")
        for rid in item.get("result_ids", []):
            if rid not in results: errors.append(f"{object_id}: missing result {rid}")
    for object_id, (_, item) in runsets.items():
        for field, collection in (("run_ids", runs), ("result_ids", results), ("capsule_ids", capsules)):
            for member in item.get(field, []):
                if member not in collection: errors.append(f"{object_id}: missing member {member}")
    for kind, collection in (("runs", runs), ("results", results), ("capsules", capsules), ("runsets", runsets)):
        for object_id, (path, _) in collection.items():
            for required in ("manifest.json", "result.html", "result.txt", "README.md", "SHA256SUMS", f"{object_id}.zip"):
                if not (path / required).is_file(): errors.append(f"{object_id}: missing generated {required}")
            zip_path = path / f"{object_id}.zip"
            if zip_path.is_file():
                with zipfile.ZipFile(zip_path) as archive:
                    if archive.testzip() is not None:
                        errors.append(f"{object_id}: ZIP integrity check failed")
                    names = archive.namelist()
                    if any(".." in Path(name).parts for name in names):
                        errors.append(f"{object_id}: ZIP contains an unsafe path")
                    if f"{object_id}/manifest.json" not in names or f"{object_id}/SHA256SUMS" not in names:
                        errors.append(f"{object_id}: ZIP lacks its manifest or checksums")
            sums = path / "SHA256SUMS"
            if sums.is_file():
                for line in sums.read_text(encoding="utf-8").splitlines():
                    digest, name = line.split("  ", 1); target = path / name
                    if not target.is_file() or canonical_file_hash(target) != digest: errors.append(f"{object_id}: checksum mismatch for {name}")
    for page in RESEARCH.rglob("*.html"):
        content = page.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', content):
            if href.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = (page.parent / href.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: broken link {href}")
    for page in RESEARCH.rglob("*.md"):
        content = page.read_text(encoding="utf-8")
        for href in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
            if href.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = (page.parent / href.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"{page.relative_to(ROOT)}: broken Markdown link {href}")
    return errors


def build() -> None:
    run_items = manifests("runs"); result_items = manifests("results"); capsule_items = manifests("capsules"); runset_items = manifests("runsets")
    for path, item in run_items: package_run(path, item)
    for path, item in result_items: package_result(path, item)
    for path, item in capsule_items: package_capsule(path, item)
    objects = {item["id"]: item for _, item in run_items + result_items + capsule_items}
    for path, item in runset_items: package_runset(path, item, objects)
    write_index(RESEARCH / "runs", "runs", [item for _, item in run_items])
    write_index(RESEARCH / "results", "results", [item for _, item in result_items])
    write_index(RESEARCH / "capsules", "capsules", [item for _, item in capsule_items])
    write_index(RESEARCH / "runsets", "runsets", [item for _, item in runset_items])
    audit_text = (ROOT / "audit" / "README.md").read_text(encoding="utf-8")
    audit_match = re.search(r"Personal Research tree audit found ([0-9,]+) files", audit_text)
    if audit_match is None:
        raise ValueError("audit/README.md does not expose the reviewed source-artifact count")
    source_artifact_count = int(audit_match.group(1).replace(",", ""))
    archive = {
        "schema_version": "1.0.0",
        "source_artifact_count": source_artifact_count,
        "source_artifact_count_note": "Hash-inventoried source artifacts; not a result count.",
        "published_runs": len(run_items),
        "published_results": len(result_items),
        "published_capsules": len(capsule_items),
        "staged_run_sets": sum(1 for _, item in runset_items if item["publication_status"] == "STAGED"),
        "indexes": {"runs": "runs/index.json", "results": "results/index.json", "capsules": "capsules/index.json", "runsets": "runsets/index.json"},
    }
    write_json(RESEARCH / "archive-index.json", archive)
    source_count_display = f"{source_artifact_count:,}"
    counts = f"""<div class="grid"><div class="card"><strong>{source_count_display}</strong><p>source artifacts cataloged</p></div><div class="card"><strong>{len(run_items)}</strong><p>published runs</p></div><div class="card"><strong>{len(result_items)}</strong><p>published results</p></div><div class="card"><strong>{len(capsule_items)}</strong><p>research capsules</p></div></div>"""
    nav = '<section><h2>RESEARCH ARCHIVE</h2><p><a href="results/index.html">Results</a> · <a href="runs/index.html">Runs</a> · <a href="capsules/index.html">Capsules</a> · <a href="runsets/index.html">Run sets</a> · <a href="../KNOWN_CONTROLS.md">Known controls</a> · <a href="../NEGATIVE_RESULTS.md">Negative results</a> · <a href="../CORRECTIONS.md">Corrections</a></p><p>Source-artifact counts are inventory counts, not result or discovery counts.</p></section>'
    write_text(RESEARCH / "index.html", shell("HMS Endeavour Research Archive", "RESEARCH ARCHIVE", "PUBLIC", counts + nav))
    write_text(RESEARCH / "README.md", f"""# HMS Endeavour Research Archive

Structured objects—not prose alone—are the public research record.

[**EXPLORE RESULTS**](results/README.md) · [Browse runs](runs/README.md) · [Research capsules](capsules/README.md) · [Curated run sets](runsets/README.md) · [Searchable offline archive](index.html)

## Current computed inventory

| Category | Count |
|---|---:|
| Hash-inventoried source artifacts | {source_count_display} |
| Published Runs | {len(run_items)} |
| Published Results | {len(result_items)} |
| Published Capsules | {len(capsule_items)} |
| Staged Run Sets | {archive['staged_run_sets']} |

**{source_count_display} source artifacts does not mean {source_count_display} results.** It is the audited file count in the supplied Personal Research tree.

## Object hierarchy

```text
RAW EXECUTION → RUN-#### → RES-#### → CAP-#### → RSET-####
```

- A **Run** records what was executed.
- A **Result** records what one or more runs support.
- A **Capsule** groups a coherent investigation.
- A **Run Set** is a curated distribution unit.

`manifest.json` is authoritative inside each package. HTML, text, Markdown, CSV, indexes, checksums, and ZIP files are generated with `python scripts/build_research_archive.py`.

Legacy flat objects under `records/` are retained as historical release snapshots. New consumers should use the package indexes above.
""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true", help="Validate existing generated packages without rebuilding")
    args = parser.parse_args()
    if not args.validate_only: build()
    errors = validate_archive()
    if errors:
        print("Research Archive validation failed:")
        for error in errors: print(f"- {error}")
        return 1
    print("Research Archive is generated and internally consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
