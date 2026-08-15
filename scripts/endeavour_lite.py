#!/usr/bin/env python3
"""HMS Endeavour Lite project and instrument command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import CorpusManifestError, verify_manifest
from hms_tools.expedition_001 import CHALLENGE_ID, VERSION as EXPEDITION_VERSION
from hms_tools.expedition_client import ExpeditionClientError, verify_remote
from hms_tools.gp29 import GP29InputError
from hms_tools.project import ProjectError, ProjectStore
from hms_tools.runtime import create_corpus_report_job, create_gp29_experiment_job, create_job, execute_job
from scripts.endeavour_lite_app import VERSION, load_expedition_configuration, packaged_self_test


def configure_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    configure_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"HMS Endeavour Lite {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("self-test", help="Run the packaged project and GP29 control")
    create = commands.add_parser("create", help="Create a local project in an empty folder")
    create.add_argument("root", type=Path); create.add_argument("--name", required=True)
    gp29 = commands.add_parser("gp29", help="Calculate GP29 and save the Run and Result")
    gp29.add_argument("root", type=Path); gp29.add_argument("text"); gp29.add_argument("--mode", choices=("letters","latin","tokens","runes","auto"), default="letters")
    corpus = commands.add_parser("corpus", help="Verify a corpus and save the portable report Result")
    corpus.add_argument("root", type=Path); corpus.add_argument("manifest", type=Path); corpus.add_argument("corpus_root", type=Path); corpus.add_argument("--strict", action="store_true")
    experiment = commands.add_parser("experiment", help="Run a bounded declared GP29 comparison and save the Result")
    experiment.add_argument("root", type=Path); experiment.add_argument("--variant", action="append", required=True)
    experiment.add_argument("--hypothesis", required=True); experiment.add_argument("--target", type=int, required=True)
    experiment.add_argument("--mode", choices=("letters","latin","tokens","runes","auto"), default="letters")
    expedition = commands.add_parser("expedition", help="Verify Expedition 001 through the approved signed service")
    expedition.add_argument("root", type=Path); expedition.add_argument("submission")
    listing = commands.add_parser("list", help="List saved Result summaries")
    listing.add_argument("root", type=Path)
    export = commands.add_parser("export", help="Export one portable Result envelope")
    export.add_argument("root", type=Path); export.add_argument("result_id"); export.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "self-test":
            result = {"product":"HMS Endeavour Lite","version":VERSION,"self_test":"PASS" if packaged_self_test() else "FAIL"}; emit(result); return 0 if result["self_test"] == "PASS" else 1
        if args.command == "create":
            emit(ProjectStore.create(args.root, args.name).project); return 0
        store = ProjectStore.open(args.root)
        if args.command == "gp29":
            job = create_job(args.text, args.mode); result = execute_job(job)
            emit(store.save_execution(job, result, instrument_id="public-gp29-calculator", instrument_version="0.1.1")); return 0
        if args.command == "corpus":
            manifest = json.loads(args.manifest.read_text(encoding="utf-8")); report = verify_manifest(manifest, args.corpus_root, args.strict)
            job = create_corpus_report_job(report); result = execute_job(job)
            emit(store.save_execution(job, result, instrument_id="corpus-manifest-verifier", instrument_version="0.1.0-rc.1")); return 0 if report["status"] == "PASS" else 1
        if args.command == "experiment":
            job = create_gp29_experiment_job(args.variant, mode=args.mode, hypothesis=args.hypothesis, target_gp_sum=args.target)
            result = execute_job(job)
            emit(store.save_execution(job, result, instrument_id="endeavour-lite-experiment-engine", instrument_version=VERSION)); return 0
        if args.command == "expedition":
            state, configuration = load_expedition_configuration()
            if state != "OPEN" or configuration is None:
                raise ExpeditionClientError("verification is not active; the campaign remains closed")
            receipt = verify_remote(
                configuration.endpoint,
                CHALLENGE_ID,
                args.submission,
                EXPEDITION_VERSION,
                public_key_b64=configuration.public_key_b64,
                public_key_id=configuration.public_key_id,
            )
            emit(store.save_expedition_receipt(receipt, instrument_version=EXPEDITION_VERSION)); return 0 if receipt["accepted"] else 1
        if args.command == "list":
            emit([{"result_id":value["result_id"],"instrument":value["instrument"],"operation":value["operation"],"evidence_label":value["evidence_label"]} for value in store.list_results()]); return 0
        store.export_result(args.result_id, args.destination); emit({"exported":args.result_id,"path":args.destination.name}); return 0
    except (ProjectError, GP29InputError, CorpusManifestError, ExpeditionClientError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr); return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
