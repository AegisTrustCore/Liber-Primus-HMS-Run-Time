#!/usr/bin/env python3
"""HMS Endeavour Lite local research workstation development shell."""

from __future__ import annotations

import json
import sys
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import CorpusManifestError, verify_manifest
from hms_tools.expedition_001 import CHALLENGE_ID, VERSION as EXPEDITION_VERSION, hint_text, instructions_text
from hms_tools.expedition_client import ExpeditionClientError, ServiceConfiguration, configured_service, verify_remote
from hms_tools.gp29 import GP29InputError, TABLE
from hms_tools.project import PROJECT_VERSION, ProjectError, ProjectStore
from hms_tools.runtime import create_corpus_report_job, create_gp29_experiment_job, create_job, execute_job


PRODUCT = "HMS Endeavour Lite"
VERSION = PROJECT_VERSION


def application_root() -> Path:
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else ROOT


def default_canonical_manifest() -> Path:
    if getattr(sys, "frozen", False):
        return application_root() / "canonical" / "LP-75-IMAGES-v1.0.0.json"
    return ROOT / "corpus/liber-primus/manifests/LP-75-IMAGES-v1.0.0.json"


def default_expedition_manifest() -> Path:
    if getattr(sys, "frozen", False):
        return application_root() / "expedition" / "manifest.json"
    return ROOT / "challenges/manifest.json"


def load_expedition_configuration() -> tuple[str, ServiceConfiguration | None]:
    path = default_expedition_manifest()
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExpeditionClientError(f"campaign manifest could not be loaded: {error}") from error
    challenge = next((item for item in manifest.get("challenges", []) if item.get("id") == CHALLENGE_ID), None)
    if not isinstance(challenge, dict):
        raise ExpeditionClientError(f"{CHALLENGE_ID} is absent from the campaign manifest")
    state = str(challenge.get("status", "CLOSED")).upper()
    if state != "OPEN":
        return state, None
    configuration = configured_service(path)
    if configuration is None:
        raise ExpeditionClientError("open campaign has no approved verification service configuration")
    return state, configuration


def packaged_self_test() -> bool:
    with tempfile.TemporaryDirectory() as directory:
        store = ProjectStore.create(Path(directory) / "project", "Self Test", created_at="2026-08-14T00:00:00Z")
        job = create_job("F U/V TH", "tokens")
        result = execute_job(job)
        envelope = store.save_execution(job, result, instrument_id="public-gp29-calculator", instrument_version="0.1.1")
        experiment_job = create_gp29_experiment_job(
            ["A", "B", "AB"], hypothesis="One declared variant has GP sum 61.", target_gp_sum=61
        )
        experiment = execute_job(experiment_job)
        experiment_envelope = store.save_execution(
            experiment_job,
            experiment,
            instrument_id="endeavour-lite-experiment-engine",
            instrument_version=VERSION,
        )
        reopened = ProjectStore.open(store.root)
        return (
            envelope["payload"]["gp_sum"] == 10
            and experiment_envelope["payload"]["gate_pass_count"] == 1
            and len(reopened.list_results()) == 2
        )


class EndeavourLiteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT} {VERSION}")
        self.geometry("1180x760")
        self.minsize(940, 620)
        self.store: ProjectStore | None = None
        self.status = tk.StringVar(value="Create or open a local project to begin.")
        self.project_title = tk.StringVar(value="No project open")
        self.project_detail = tk.StringVar(value="Projects are private and local by default.")
        self.gp_mode = tk.StringVar(value="letters")
        self.gp_summary = tk.StringVar(value="No calculation yet.")
        self.experiment_mode = tk.StringVar(value="letters")
        self.experiment_hypothesis = tk.StringVar()
        self.experiment_target = tk.StringVar()
        self.experiment_summary = tk.StringVar(value="Declare the hypothesis and success gate before execution.")
        canonical = default_canonical_manifest()
        self.corpus_manifest_path = tk.StringVar(value=str(canonical) if canonical.is_file() else "")
        self.corpus_root_path = tk.StringVar()
        self.corpus_strict = tk.BooleanVar(value=True)
        self.corpus_summary = tk.StringVar(value="No verification yet.")
        self.expedition_summary = tk.StringVar(value="Loading campaign boundary.")
        try:
            self.expedition_state, self.expedition_configuration = load_expedition_configuration()
            if self.expedition_configuration is None:
                self.expedition_summary.set(f"CAMPAIGN {self.expedition_state} — no submission will be sent.")
            else:
                self.expedition_summary.set("CAMPAIGN OPEN — signed official verification is available.")
        except ExpeditionClientError as error:
            self.expedition_state, self.expedition_configuration = "CONFIGURATION ERROR", None
            self.expedition_summary.set(f"FAIL-CLOSED — {error}")
        self._result_by_item: dict[str, dict[str, object]] = {}
        self._build_menu()
        self._build_shell()
        self._load_atlas()

    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        project = tk.Menu(menu, tearoff=False)
        project.add_command(label="New project…", command=self.new_project, accelerator="Ctrl+N")
        project.add_command(label="Open project…", command=self.open_project, accelerator="Ctrl+O")
        project.add_separator()
        project.add_command(label="Export selected result…", command=self.export_selected_result)
        project.add_separator()
        project.add_command(label="Exit", command=self.destroy)
        menu.add_cascade(label="Project", menu=project)
        tools = tk.Menu(menu, tearoff=False)
        tools.add_command(label="Run workstation self-test", command=self.run_self_test)
        tools.add_command(label="Refresh history", command=self.refresh_history)
        menu.add_cascade(label="Tools", menu=tools)
        self.configure(menu=menu)
        self.bind_all("<Control-n>", lambda _event: self.new_project())
        self.bind_all("<Control-o>", lambda _event: self.open_project())

    def _build_shell(self) -> None:
        header = ttk.Frame(self, padding=(18, 14))
        header.pack(fill="x")
        ttk.Label(header, text="HMS ENDEAVOUR", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        title_row = ttk.Frame(header)
        title_row.pack(fill="x")
        ttk.Label(title_row, text=PRODUCT, font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Label(title_row, textvariable=self.project_title, font=("Segoe UI", 11, "bold")).pack(side="right")
        ttk.Label(header, textvariable=self.project_detail).pack(anchor="e")
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 10))
        self._build_bridge_tab()
        self._build_rune_tab()
        self._build_gp29_tab()
        self._build_corpus_tab()
        self._build_atlas_tab()
        self._build_experiment_tab()
        self._build_expedition_tab()
        self._build_history_tab()
        ttk.Label(self, textvariable=self.status, padding=(18, 8)).pack(fill="x")

    def _tab(self, title: str) -> ttk.Frame:
        frame = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(frame, text=title)
        return frame

    def _build_bridge_tab(self) -> None:
        frame = self._tab("Bridge")
        ttk.Label(frame, text="Local research bridge", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="One private project, shared result records, and explicit exports. No account, telemetry, or silent upload.").pack(anchor="w", pady=(4, 18))
        actions = ttk.Frame(frame)
        actions.pack(anchor="w")
        ttk.Button(actions, text="Create project", command=self.new_project).pack(side="left")
        ttk.Button(actions, text="Open project", command=self.open_project).pack(side="left", padx=8)
        cards = ttk.Frame(frame)
        cards.pack(fill="x", pady=24)
        for column, (title, state, detail) in enumerate((
            ("GP29", "RELEASED", "Calculate and save deterministic GP29 Results."),
            ("Corpus", "RC", "Verify the canonical 75-page identity manifest."),
            ("Expedition", self.expedition_state, "Signed remote receipts; submitted plaintext is never saved."),
            ("Runtime", "DEVELOPMENT", "Local jobs, Results, provenance, and history."),
        )):
            card = ttk.LabelFrame(cards, text=title, padding=12)
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 6, 0))
            cards.columnconfigure(column, weight=1)
            ttk.Label(card, text=state, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(card, text=detail, wraplength=220).pack(anchor="w", pady=(6, 0))

    def _build_gp29_tab(self) -> None:
        frame = self._tab("GP29")
        ttk.Label(frame, text="GP29 Workbench", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Deterministic calculation only; numerical relationships are not LP solve evidence.").pack(anchor="w", pady=(4, 12))
        controls = ttk.Frame(frame)
        controls.pack(fill="x")
        ttk.Label(controls, text="Input mode").pack(side="left")
        ttk.Combobox(controls, textvariable=self.gp_mode, values=("letters","latin","tokens","runes","auto"), state="readonly", width=12).pack(side="left", padx=8)
        ttk.Button(controls, text="Calculate and save", command=self.calculate_gp29).pack(side="left")
        self.gp_input = tk.Text(frame, height=5, wrap="word", font=("Segoe UI", 11))
        self.gp_input.pack(fill="x", pady=10)
        ttk.Label(frame, textvariable=self.gp_summary, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        columns = ("index","rune","sound","prime","L","R","N","Q")
        self.gp_table = ttk.Treeview(frame, columns=columns, show="headings")
        for column in columns:
            self.gp_table.heading(column, text=column)
            self.gp_table.column(column, width=80 if column != "sound" else 120, anchor="center")
        self.gp_table.pack(fill="both", expand=True)

    def _build_rune_tab(self) -> None:
        frame = self._tab("Rune Workbench")
        ttk.Label(frame, text="Rune Workbench", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="The canonical 29-symbol calculation alphabet. Double-click a row to append its explicit sound token to GP29.").pack(anchor="w", pady=(4, 12))
        columns = ("index", "rune", "sound", "prime", "L", "R", "N", "Q")
        self.rune_table = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.rune_table.heading(column, text=column)
            self.rune_table.column(column, width=90 if column != "sound" else 130, anchor="center")
        for entry in TABLE:
            self.rune_table.insert("", "end", values=(entry.index, entry.rune, entry.sound, entry.prime, entry.L, entry.R, entry.N, entry.Q))
        self.rune_table.pack(fill="both", expand=True)
        self.rune_table.bind("<Double-1>", self.append_selected_rune_token)

    def append_selected_rune_token(self, _event=None) -> None:
        selected = self.rune_table.selection()
        if not selected:
            return
        sound = str(self.rune_table.item(selected[0], "values")[2])
        existing = self.gp_input.get("1.0", "end-1c").rstrip()
        self.gp_input.delete("1.0", "end")
        self.gp_input.insert("1.0", f"{existing} {sound}".strip())
        self.gp_mode.set("tokens")
        self.tabs.select(self.gp_input.master)
        self.status.set(f"Appended explicit token {sound}; GP29 mode set to tokens.")

    def _path_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, command) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=14).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=command).pack(side="left", padx=(8, 0))

    def _build_corpus_tab(self) -> None:
        frame = self._tab("Corpus Verify")
        ttk.Label(frame, text="Corpus Verification", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Read-only local byte verification. The project stores the report, not the page images or local root path.").pack(anchor="w", pady=(4, 12))
        self._path_row(frame, "Manifest", self.corpus_manifest_path, self.choose_manifest)
        self._path_row(frame, "Corpus folder", self.corpus_root_path, self.choose_corpus_root)
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=8)
        ttk.Checkbutton(controls, text="Strict: reject undeclared files", variable=self.corpus_strict).pack(side="left")
        ttk.Button(controls, text="Verify and save", command=self.verify_corpus).pack(side="left", padx=10)
        ttk.Label(frame, textvariable=self.corpus_summary, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 6))
        self.corpus_table = ttk.Treeview(frame, columns=("status","path","expected","actual"), show="headings")
        for column, title, width in (("status","Status",110),("path","File",260),("expected","Expected bytes",130),("actual","Actual bytes",130)):
            self.corpus_table.heading(column, text=title); self.corpus_table.column(column, width=width, anchor="w")
        self.corpus_table.pack(fill="both", expand=True)

    def _build_atlas_tab(self) -> None:
        frame = self._tab("LP Atlas")
        ttk.Label(frame, text="LP Atlas — metadata foundation", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="All 75 registered carriers are navigable by identity. Page rendering, notes, Regions, and transcriptions follow in later increments.").pack(anchor="w", pady=(4, 12))
        self.atlas_table = ttk.Treeview(frame, columns=("page","bytes","sha256"), show="headings")
        self.atlas_table.heading("page", text="Page"); self.atlas_table.column("page", width=100)
        self.atlas_table.heading("bytes", text="Bytes"); self.atlas_table.column("bytes", width=120)
        self.atlas_table.heading("sha256", text="SHA-256"); self.atlas_table.column("sha256", width=620)
        self.atlas_table.pack(fill="both", expand=True)

    def _build_experiment_tab(self) -> None:
        frame = self._tab("Experiments")
        ttk.Label(frame, text="Bounded Experiment Engine", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Compare 2-100 declared inputs against one predeclared GP-sum gate. This tool does not generate, rank, or optimize candidates.", wraplength=900).pack(anchor="w", pady=(4, 12))
        declaration = ttk.Frame(frame)
        declaration.pack(fill="x")
        ttk.Label(declaration, text="Hypothesis").grid(row=0, column=0, sticky="w")
        ttk.Entry(declaration, textvariable=self.experiment_hypothesis).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Label(declaration, text="Target GP sum").grid(row=0, column=2, sticky="w")
        ttk.Entry(declaration, textvariable=self.experiment_target, width=10).grid(row=0, column=3, padx=8)
        ttk.Combobox(declaration, textvariable=self.experiment_mode, values=("letters", "latin", "tokens", "runes", "auto"), state="readonly", width=10).grid(row=0, column=4)
        ttk.Button(declaration, text="Run and save", command=self.run_gp29_experiment).grid(row=0, column=5, padx=(8, 0))
        declaration.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Variants (one per line)").pack(anchor="w", pady=(12, 2))
        self.experiment_input = tk.Text(frame, height=6, wrap="word", font=("Segoe UI", 10))
        self.experiment_input.pack(fill="x")
        ttk.Label(frame, textvariable=self.experiment_summary, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=8)
        self.experiment_table = ttk.Treeview(frame, columns=("index", "variant", "runes", "gp_sum", "gate"), show="headings")
        for column, title, width in (("index", "#", 50), ("variant", "Variant", 440), ("runes", "Runes", 80), ("gp_sum", "GP sum", 90), ("gate", "Gate", 90)):
            self.experiment_table.heading(column, text=title); self.experiment_table.column(column, width=width)
        self.experiment_table.pack(fill="both", expand=True)

    def _build_expedition_tab(self) -> None:
        frame = self._tab("Expedition")
        ttk.Label(frame, text="Expedition 001", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, textvariable=self.expedition_summary, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6, 8))
        guidance = tk.Text(frame, height=14, wrap="word", font=("Segoe UI", 10))
        guidance.insert("1.0", instructions_text(self.expedition_state))
        guidance.configure(state="disabled")
        guidance.pack(fill="both", expand=True)
        hint_row = ttk.Frame(frame)
        hint_row.pack(fill="x", pady=(8, 4))
        ttk.Label(hint_row, text="Progressive hints:").pack(side="left")
        for level in range(1, 5):
            ttk.Button(hint_row, text=str(level), command=lambda value=level: self.show_expedition_hint(value), width=3).pack(side="left", padx=(6, 0))
        submission_row = ttk.Frame(frame)
        submission_row.pack(fill="x", pady=(4, 0))
        ttk.Label(submission_row, text="Answer").pack(side="left")
        self.expedition_submission = ttk.Entry(submission_row)
        self.expedition_submission.pack(side="left", fill="x", expand=True, padx=8)
        self.expedition_verify_button = ttk.Button(submission_row, text="Verify and save receipt", command=self.verify_expedition)
        self.expedition_verify_button.pack(side="left")
        if self.expedition_configuration is None:
            self.expedition_verify_button.configure(state="disabled")
        ttk.Label(frame, text="Only the signed receipt and normalized submission hash enter project history; the answer text is discarded.").pack(anchor="w", pady=(6, 0))

    def show_expedition_hint(self, level: int) -> None:
        messagebox.showinfo(f"Expedition 001 — Hint {level}", hint_text(level), parent=self)

    def verify_expedition(self) -> None:
        try:
            store = self._require_project()
            configuration = self.expedition_configuration
            if configuration is None:
                raise ExpeditionClientError("verification is not active; the campaign remains closed")
            submitted = self.expedition_submission.get()
            if not submitted.strip():
                raise ExpeditionClientError("enter an answer before verification")
            receipt = verify_remote(
                configuration.endpoint,
                CHALLENGE_ID,
                submitted,
                EXPEDITION_VERSION,
                public_key_b64=configuration.public_key_b64,
                public_key_id=configuration.public_key_id,
            )
            envelope = store.save_expedition_receipt(receipt, instrument_version=EXPEDITION_VERSION)
        except (ProjectError, ExpeditionClientError, OSError, ValueError) as error:
            messagebox.showerror("Expedition verification failed", str(error), parent=self)
            return
        self.expedition_submission.delete(0, "end")
        verdict = "ACCEPTED" if receipt["accepted"] else "NOT ACCEPTED"
        self.expedition_summary.set(f"{verdict} — receipt {receipt['receipt_id']} saved as {envelope['result_id']}")
        self.status.set("Signed Expedition receipt saved with TRAINING_ONLY evidence; submitted plaintext was not retained.")
        self.refresh_history()

    def _build_history_tab(self) -> None:
        frame = self._tab("Runs & Results")
        ttk.Label(frame, text="Project history", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        pane = ttk.Panedwindow(frame, orient="horizontal")
        pane.pack(fill="both", expand=True, pady=(12, 0))
        left = ttk.Frame(pane); right = ttk.Frame(pane)
        pane.add(left, weight=1); pane.add(right, weight=2)
        self.history = ttk.Treeview(left, columns=("instrument","operation","evidence"), show="headings", selectmode="browse")
        for column, title, width in (("instrument","Instrument",150),("operation","Operation",150),("evidence","Evidence",130)):
            self.history.heading(column, text=title); self.history.column(column, width=width)
        self.history.pack(fill="both", expand=True)
        self.history.bind("<<TreeviewSelect>>", self.preview_result)
        self.result_preview = tk.Text(right, wrap="none", state="disabled", font=("Consolas", 9))
        self.result_preview.pack(fill="both", expand=True)

    def _require_project(self) -> ProjectStore:
        if self.store is None:
            raise ProjectError("Create or open a project first.")
        return self.store

    def new_project(self) -> None:
        selected = filedialog.askdirectory(parent=self, title="Choose an empty project folder", mustexist=False)
        if not selected:
            return
        name = simpledialog.askstring("Project name", "Name this research project:", parent=self)
        if not name:
            return
        try:
            canonical = default_canonical_manifest()
            self._set_project(ProjectStore.create(Path(selected), name, manifest_ref=canonical.name if canonical.is_file() else None))
        except (ProjectError, OSError) as error:
            messagebox.showerror("Unable to create project", str(error), parent=self)

    def open_project(self) -> None:
        selected = filedialog.askdirectory(parent=self, title="Open HMS project")
        if not selected:
            return
        try:
            self._set_project(ProjectStore.open(Path(selected)))
        except ProjectError as error:
            messagebox.showerror("Unable to open project", str(error), parent=self)

    def _set_project(self, store: ProjectStore) -> None:
        self.store = store
        self.project_title.set(store.project["name"])
        self.project_detail.set(f"{store.project['project_id']} · PRIVATE · {store.root.name}")
        self.status.set("Project ready. Changes remain local until you explicitly export them.")
        self.refresh_history()

    def calculate_gp29(self) -> None:
        try:
            store = self._require_project()
            job = create_job(self.gp_input.get("1.0", "end-1c"), self.gp_mode.get())
            result = execute_job(job)
            envelope = store.save_execution(job, result, instrument_id="public-gp29-calculator", instrument_version="0.1.1")
        except (ProjectError, GP29InputError, ValueError) as error:
            messagebox.showerror("GP29 calculation failed", str(error), parent=self); return
        for item in self.gp_table.get_children(): self.gp_table.delete(item)
        payload = envelope["payload"]
        for entry in payload["entries"]:
            self.gp_table.insert("", "end", values=(entry["index"],entry["rune"],entry["sound"],entry["prime"],entry["L"],entry["R"],entry["N"],entry["Q"]))
        self.gp_summary.set(f"Saved {envelope['result_id']} · {payload['rune_count']} runes · Prime/GP sum {payload['gp_sum']}")
        self.status.set("GP29 Result saved with CALCULATION_ONLY evidence.")
        self.refresh_history()

    def choose_manifest(self) -> None:
        selected = filedialog.askopenfilename(parent=self, title="Choose corpus manifest", filetypes=(("JSON","*.json"),("All files","*.*")))
        if selected: self.corpus_manifest_path.set(selected)

    def choose_corpus_root(self) -> None:
        selected = filedialog.askdirectory(parent=self, title="Choose local corpus folder")
        if selected: self.corpus_root_path.set(selected)

    def verify_corpus(self) -> None:
        try:
            store = self._require_project()
            manifest = json.loads(Path(self.corpus_manifest_path.get()).read_text(encoding="utf-8"))
            report = verify_manifest(manifest, Path(self.corpus_root_path.get()), self.corpus_strict.get())
            job = create_corpus_report_job(report)
            result = execute_job(job)
            envelope = store.save_execution(job, result, instrument_id="corpus-manifest-verifier", instrument_version="0.1.0-rc.3")
        except (ProjectError, CorpusManifestError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Corpus verification failed", str(error), parent=self); return
        for item in self.corpus_table.get_children(): self.corpus_table.delete(item)
        for finding in report["files"]:
            self.corpus_table.insert("", "end", values=(finding["status"],finding["path"],finding.get("expected_bytes",""),finding.get("actual_bytes","")))
        for path in report["unexpected_files"]:
            self.corpus_table.insert("", "end", values=("UNEXPECTED",path,"—","—"))
        summary = report["summary"]
        self.corpus_summary.set(f"{report['status']} · {summary['verified']} verified · {summary['mismatch']} altered · {summary['missing']} missing · {summary['unexpected']} extra")
        self.status.set(f"Corpus report saved as {envelope['result_id']} with PROVENANCE_ONLY evidence.")
        self.refresh_history()

    def run_gp29_experiment(self) -> None:
        try:
            store = self._require_project()
            variants = self.experiment_input.get("1.0", "end-1c").splitlines()
            target = int(self.experiment_target.get().strip())
            job = create_gp29_experiment_job(
                variants,
                mode=self.experiment_mode.get(),
                hypothesis=self.experiment_hypothesis.get(),
                target_gp_sum=target,
            )
            result = execute_job(job)
            envelope = store.save_execution(job, result, instrument_id="endeavour-lite-experiment-engine", instrument_version=VERSION)
        except (ProjectError, GP29InputError, ValueError) as error:
            messagebox.showerror("Experiment failed", str(error), parent=self); return
        for item in self.experiment_table.get_children(): self.experiment_table.delete(item)
        payload = envelope["payload"]
        for row in payload["rows"]:
            self.experiment_table.insert("", "end", values=(row["index"], row["variant"], row["rune_count"], row["gp_sum"], "PASS" if row["gate_passed"] else "NO"))
        self.experiment_summary.set(f"Saved {envelope['result_id']} · {payload['gate_pass_count']} of {payload['variant_count']} passed the declared gate · EXPERIMENTAL")
        self.status.set("Experiment saved. A numerical gate match is not LP solve evidence.")
        self.refresh_history()

    def _load_atlas(self) -> None:
        canonical = default_canonical_manifest()
        if not canonical.is_file(): return
        try: manifest = json.loads(canonical.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError): return
        for item in manifest.get("files", []):
            self.atlas_table.insert("", "end", values=(item.get("path",""),item.get("bytes",""),item.get("sha256","")))

    def refresh_history(self) -> None:
        for item in self.history.get_children(): self.history.delete(item)
        self._result_by_item.clear()
        if self.store is None: return
        try: results = self.store.list_results()
        except (ProjectError, OSError, json.JSONDecodeError) as error:
            self.status.set(f"History error: {error}"); return
        for result in reversed(results):
            item = self.history.insert("", "end", values=(result["instrument"]["id"],result["operation"],result["evidence_label"]))
            self._result_by_item[item] = result

    def preview_result(self, _event=None) -> None:
        selected = self.history.selection()
        if not selected: return
        value = self._result_by_item[selected[0]]
        self.result_preview.configure(state="normal")
        self.result_preview.delete("1.0", "end")
        self.result_preview.insert("1.0", json.dumps(value, ensure_ascii=False, indent=2))
        self.result_preview.configure(state="disabled")

    def export_selected_result(self) -> None:
        selected = self.history.selection()
        if not selected or self.store is None:
            messagebox.showinfo("Select a result", "Select a Result in Runs & Results first.", parent=self); return
        result = self._result_by_item[selected[0]]
        destination = filedialog.asksaveasfilename(parent=self, title="Export portable HMS Result", initialfile=f"{result['result_id']}.json", defaultextension=".json", filetypes=(("JSON","*.json"),))
        if not destination: return
        try: self.store.export_result(result["result_id"], Path(destination))
        except (ProjectError, OSError, json.JSONDecodeError) as error:
            messagebox.showerror("Export failed", str(error), parent=self); return
        self.status.set(f"Exported {result['result_id']}; no source corpus files were included.")

    def run_self_test(self) -> None:
        passed = packaged_self_test()
        self.status.set("Workstation self-test passed." if passed else "Workstation self-test failed.")
        if not passed: messagebox.showerror("Self-test failed", "Do not rely on this build.", parent=self)


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return 0 if packaged_self_test() else 1
    EndeavourLiteApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
