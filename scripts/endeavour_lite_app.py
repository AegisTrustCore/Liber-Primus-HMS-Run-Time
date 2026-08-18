#!/usr/bin/env python3
"""HMS Endeavour Lite local research workstation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageOps, ImageTk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import CorpusManifestError, verify_manifest
from hms_tools.expedition_001 import CHALLENGE_ID, VERSION as EXPEDITION_VERSION, hint_text, instructions_text
from hms_tools.expedition_client import ExpeditionClientError, ServiceConfiguration, configured_service, verify_remote
from hms_tools.gp29 import GP29InputError, TABLE
from hms_tools.project import PROJECT_VERSION, ProjectError, ProjectStore
from hms_tools.runtime import create_corpus_report_job, create_gp29_experiment_job, create_job, create_result_comparison_job, execute_job
from hms_tools.ui_theme import SURFACE, apply_hms_theme, build_brand_header, configure_text


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
        atlas_page = Path(directory) / "atlas-control.png"
        Image.new("RGB", (29, 75), "#d4af37").save(atlas_page)
        with Image.open(atlas_page) as source:
            atlas_control = ImageOps.exif_transpose(source).copy()
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
        research_object = store.save_research_object(
            "REGION", "Self-test region", {"x":0.0,"y":0.0,"width":1.0,"height":1.0}, page_refs=["0.jpg"]
        )
        backup = store.create_backup(Path(directory) / "self-test-backup.zip")
        reopened = ProjectStore.open(store.root)
        return (
            envelope["payload"]["gp_sum"] == 10
            and experiment_envelope["payload"]["gate_pass_count"] == 1
            and len(reopened.list_results()) == 2
            and research_object["object_type"] == "REGION"
            and reopened.audit()["status"] == "PASS"
            and backup.is_file()
            and atlas_control.size == (29, 75)
        )


class EndeavourLiteApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT} {VERSION}")
        self.geometry("1180x760")
        self.minsize(940, 620)
        apply_hms_theme(self)
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
        self.atlas_summary = tk.StringVar(value="Select one or more registered pages.")
        self.atlas_page_title = tk.StringVar(value="No page selected")
        self.atlas_zoom_text = tk.StringVar(value="Fit")
        self.atlas_zoom = 1.0
        self.atlas_fit = True
        self._atlas_source_image: Image.Image | None = None
        self._atlas_photo: ImageTk.PhotoImage | None = None
        self._atlas_resize_job: str | None = None
        self.research_title = tk.StringVar()
        self.research_type = tk.StringVar(value="NOTE")
        self.research_pages = tk.StringVar()
        self.region_x = tk.StringVar(value="0.0")
        self.region_y = tk.StringVar(value="0.0")
        self.region_width = tk.StringVar(value="1.0")
        self.region_height = tk.StringVar(value="1.0")
        self.research_summary = tk.StringVar(value="Research objects are immutable, private, and local by default.")
        self.recovery_summary = tk.StringVar(value="Open a project to inspect integrity and privacy boundaries.")
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
        self._object_by_item: dict[str, dict[str, object]] = {}
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
        header = build_brand_header(self, PRODUCT, "Private local Liber Primus research station", "AEGIS-SERVED  ·  LOCAL-FIRST  ·  RC")
        header.pack(fill="x")
        project_strip = ttk.Frame(self, padding=(20, 7))
        project_strip.pack(fill="x")
        ttk.Label(project_strip, textvariable=self.project_title, font=("Segoe UI Semibold", 10)).pack(side="left")
        ttk.Label(project_strip, textvariable=self.project_detail, style="Muted.TLabel").pack(side="right")
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
        self._build_research_tab()
        self._build_recovery_tab()
        footer = ttk.Frame(self, style="Header.TFrame", padding=(18, 8))
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status, style="Status.TLabel").pack(side="left", fill="x", expand=True)
        ttk.Label(footer, text="POWERED AND SERVED BY AEGIS TRUST CORE", style="Brand.TLabel").pack(side="right")

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
            ("Lite workstation", "PUBLIC CANDIDATE", "Local Atlas, research objects, Results, audit, and recovery."),
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
        configure_text(self.gp_input)
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
        ttk.Label(frame, text="LP Atlas - all 75 registered pages", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="The manifest is preloaded. Link your private local corpus once, then view, zoom, pan, annotate, bookmark, and group pages without copying them into the project.").pack(anchor="w", pady=(4, 8))
        controls = ttk.Frame(frame); controls.pack(fill="x", pady=(0, 8))
        ttk.Button(controls, text="Previous", command=lambda: self.move_atlas_page(-1)).pack(side="left")
        ttk.Button(controls, text="Next", command=lambda: self.move_atlas_page(1)).pack(side="left", padx=(4, 10))
        ttk.Button(controls, text="Fit", command=self.fit_atlas_page).pack(side="left")
        ttk.Button(controls, text="-", width=3, command=lambda: self.zoom_atlas_page(0.8)).pack(side="left", padx=(4, 0))
        ttk.Button(controls, text="+", width=3, command=lambda: self.zoom_atlas_page(1.25)).pack(side="left", padx=(2, 8))
        ttk.Label(controls, textvariable=self.atlas_zoom_text, width=8).pack(side="left")
        ttk.Button(controls, text="Open externally", command=self.open_selected_page).pack(side="left", padx=(0, 6))
        ttk.Button(controls, text="Bookmark", command=self.save_atlas_bookmark).pack(side="left")
        ttk.Button(controls, text="Save selected as Page Set", command=self.save_atlas_pageset).pack(side="left")
        ttk.Label(controls, textvariable=self.atlas_summary).pack(side="right")
        pane = ttk.Panedwindow(frame, orient="horizontal"); pane.pack(fill="both", expand=True)
        list_frame = ttk.Frame(pane); viewer = ttk.Frame(pane)
        pane.add(list_frame, weight=1); pane.add(viewer, weight=4)
        self.atlas_table = ttk.Treeview(list_frame, columns=("page","bytes"), show="headings", selectmode="extended")
        self.atlas_table.heading("page", text="Page"); self.atlas_table.column("page", width=105, anchor="w")
        self.atlas_table.heading("bytes", text="Bytes"); self.atlas_table.column("bytes", width=90, anchor="e")
        atlas_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.atlas_table.yview)
        self.atlas_table.configure(yscrollcommand=atlas_scroll.set)
        self.atlas_table.pack(side="left", fill="both", expand=True); atlas_scroll.pack(side="right", fill="y")
        ttk.Label(viewer, textvariable=self.atlas_page_title, font=("Segoe UI", 11, "bold")).pack(fill="x", pady=(0, 4))
        canvas_frame = ttk.Frame(viewer); canvas_frame.pack(fill="both", expand=True)
        self.atlas_canvas = tk.Canvas(canvas_frame, background=SURFACE, highlightthickness=0)
        atlas_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.atlas_canvas.xview)
        atlas_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.atlas_canvas.yview)
        self.atlas_canvas.configure(xscrollcommand=atlas_x.set, yscrollcommand=atlas_y.set)
        self.atlas_canvas.grid(row=0, column=0, sticky="nsew"); atlas_y.grid(row=0, column=1, sticky="ns"); atlas_x.grid(row=1, column=0, sticky="ew")
        canvas_frame.rowconfigure(0, weight=1); canvas_frame.columnconfigure(0, weight=1)
        self.atlas_canvas.create_text(20, 20, anchor="nw", fill="#d7dde5", text="Link a local corpus folder in Project & Recovery, then select a page.", tags="message", font=("Segoe UI", 11))
        self.atlas_canvas.bind("<ButtonPress-1>", lambda event: self.atlas_canvas.scan_mark(event.x, event.y))
        self.atlas_canvas.bind("<B1-Motion>", lambda event: self.atlas_canvas.scan_dragto(event.x, event.y, gain=1))
        self.atlas_canvas.bind("<Control-MouseWheel>", self.atlas_mouse_zoom)
        self.atlas_canvas.bind("<Configure>", self.atlas_canvas_resized)
        self.atlas_table.bind("<<TreeviewSelect>>", self.atlas_selection_changed)
        self.atlas_table.bind("<Double-1>", lambda _event: self.fit_atlas_page())

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
        configure_text(self.experiment_input)
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
        configure_text(guidance)
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
        actions = ttk.Frame(left); actions.pack(fill="x", pady=(0, 6))
        ttk.Button(actions, text="Compare 2 selected", command=self.compare_selected_results).pack(side="left")
        self.history = ttk.Treeview(left, columns=("instrument","operation","evidence"), show="headings", selectmode="extended")
        for column, title, width in (("instrument","Instrument",150),("operation","Operation",150),("evidence","Evidence",130)):
            self.history.heading(column, text=title); self.history.column(column, width=width)
        self.history.pack(fill="both", expand=True)
        self.history.bind("<<TreeviewSelect>>", self.preview_result)
        self.result_preview = tk.Text(right, wrap="none", state="disabled", font=("Consolas", 9))
        configure_text(self.result_preview, monospace=True)
        self.result_preview.pack(fill="both", expand=True)

    def _build_research_tab(self) -> None:
        frame = self._tab("Research Objects")
        ttk.Label(frame, text="Saved evidence and research history", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Record bounded observations without turning a note into a solve claim. Page and Result references remain explicit.").pack(anchor="w", pady=(4, 10))
        row = ttk.Frame(frame); row.pack(fill="x")
        ttk.Label(row, text="Type").pack(side="left")
        ttk.Combobox(row, textvariable=self.research_type, values=("NOTE","REGION","EVIDENCE","CLAIM","RUNE_SELECTION"), state="readonly", width=16).pack(side="left", padx=6)
        ttk.Label(row, text="Title").pack(side="left")
        ttk.Entry(row, textvariable=self.research_title).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Label(row, text="Pages").pack(side="left")
        ttk.Entry(row, textvariable=self.research_pages, width=18).pack(side="left", padx=6)
        ttk.Button(row, text="Save object", command=self.save_research_object).pack(side="left")
        region = ttk.Frame(frame); region.pack(fill="x", pady=(8, 0))
        ttk.Label(region, text="Region (normalized 0-1):").pack(side="left")
        for label, variable in (("x",self.region_x),("y",self.region_y),("width",self.region_width),("height",self.region_height)):
            ttk.Label(region, text=label).pack(side="left", padx=(8, 2)); ttk.Entry(region, textvariable=variable, width=7).pack(side="left")
        ttk.Button(region, text="Export selected object", command=self.export_selected_object).pack(side="right")
        self.research_text = tk.Text(frame, height=7, wrap="word"); configure_text(self.research_text); self.research_text.pack(fill="x", pady=8)
        ttk.Label(frame, textvariable=self.research_summary, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        self.research_table = ttk.Treeview(frame, columns=("type","title","pages","created"), show="headings", selectmode="browse")
        for column, title, width in (("type","Type",120),("title","Title",340),("pages","Pages",180),("created","Created",220)):
            self.research_table.heading(column, text=title); self.research_table.column(column, width=width)
        self.research_table.pack(fill="both", expand=True)

    def _build_recovery_tab(self) -> None:
        frame = self._tab("Project & Recovery")
        ttk.Label(frame, text="Project settings, integrity, and recovery", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="The corpus root is a private machine-local pointer. Backups exclude that path, corpus images, and exports.").pack(anchor="w", pady=(4, 12))
        self._path_row(frame, "Corpus folder", self.corpus_root_path, self.choose_and_save_corpus_root)
        actions = ttk.Frame(frame); actions.pack(anchor="w", pady=10)
        ttk.Button(actions, text="Clear corpus link", command=self.clear_corpus_root).pack(side="left")
        ttk.Button(actions, text="Audit & rebuild index", command=self.audit_project).pack(side="left", padx=6)
        ttk.Button(actions, text="Create safe backup ZIP", command=self.backup_project).pack(side="left")
        ttk.Label(frame, textvariable=self.recovery_summary, font=("Segoe UI", 11, "bold"), wraplength=900).pack(anchor="w", pady=8)

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
        try:
            settings = store.read_settings()
            self.corpus_root_path.set(settings["local_corpus_root"] or "")
        except ProjectError as error:
            self.recovery_summary.set(f"Settings error: {error}")
        self.refresh_history()
        self.refresh_research_objects()
        self.render_atlas_page(reload_source=True)

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

    def choose_and_save_corpus_root(self) -> None:
        self.choose_corpus_root()
        if not self.corpus_root_path.get(): return
        try: settings = self._require_project().set_local_corpus_root(Path(self.corpus_root_path.get()))
        except (ProjectError, OSError) as error:
            messagebox.showerror("Corpus link failed", str(error), parent=self); return
        self.recovery_summary.set(f"Private local corpus linked: {settings['local_corpus_root']}")
        self.render_atlas_page()

    def clear_corpus_root(self) -> None:
        try: self._require_project().set_local_corpus_root(None)
        except (ProjectError, OSError) as error:
            messagebox.showerror("Unable to clear corpus link", str(error), parent=self); return
        self.corpus_root_path.set("")
        self.recovery_summary.set("Private corpus link cleared. No corpus files were changed.")
        self._atlas_source_image = None
        self._atlas_photo = None
        self.atlas_canvas.delete("all")
        self.atlas_canvas.create_text(20, 20, anchor="nw", fill="#d7dde5", text="Link a local corpus folder in Project & Recovery, then select a page.", tags="message", font=("Segoe UI", 11))

    def verify_corpus(self) -> None:
        try:
            store = self._require_project()
            manifest = json.loads(Path(self.corpus_manifest_path.get()).read_text(encoding="utf-8"))
            report = verify_manifest(manifest, Path(self.corpus_root_path.get()), self.corpus_strict.get())
            job = create_corpus_report_job(report)
            result = execute_job(job)
            envelope = store.save_execution(job, result, instrument_id="corpus-manifest-verifier", instrument_version="0.2.0-dev")
        except (ProjectError, CorpusManifestError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Corpus verification failed", str(error), parent=self); return
        for item in self.corpus_table.get_children(): self.corpus_table.delete(item)
        for finding in report["files"]:
            self.corpus_table.insert("", "end", values=(finding["status"],finding["path"],finding.get("expected_bytes",""),finding.get("actual_bytes","")))
        for path in report["unexpected_files"]:
            self.corpus_table.insert("", "end", values=("UNEXPECTED",path,"—","—"))
        summary = report["summary"]
        self.corpus_summary.set(f"{report['status']} · {summary['verified']} verified · {summary['mismatch']} altered · {summary['missing']} missing · {summary['unexpected']} extra")
        if report["status"] == "PASS":
            store.set_local_corpus_root(Path(self.corpus_root_path.get()))
            self.render_atlas_page(reload_source=True)
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
        children = self.atlas_table.get_children()
        if children:
            self.atlas_table.selection_set(children[0]); self.atlas_table.focus(children[0])

    def selected_atlas_pages(self) -> list[str]:
        return [str(self.atlas_table.item(item, "values")[0]) for item in self.atlas_table.selection()]

    def atlas_selection_changed(self, _event=None) -> None:
        pages = self.selected_atlas_pages()
        self.atlas_summary.set(f"{len(pages)} page(s) selected" if pages else "Select one or more registered pages.")
        self.research_pages.set(", ".join(pages))
        if len(pages) == 1:
            self.atlas_page_title.set(pages[0])
            self.atlas_fit = True
            self.render_atlas_page(reload_source=True)

    def atlas_page_path(self) -> Path:
        pages = self.selected_atlas_pages()
        if len(pages) != 1: raise ProjectError("select exactly one Atlas page")
        root = self._require_project().read_settings()["local_corpus_root"]
        if not root: raise ProjectError("link the private local corpus folder in Project & Recovery first")
        root_path = Path(root).resolve(); target = (root_path / pages[0]).resolve()
        if not target.is_relative_to(root_path) or not target.is_file():
            raise ProjectError(f"local corpus page is unavailable: {pages[0]}")
        return target

    def render_atlas_page(self, *, reload_source: bool = False) -> None:
        try:
            target = self.atlas_page_path()
            if reload_source or self._atlas_source_image is None:
                with Image.open(target) as image:
                    self._atlas_source_image = ImageOps.exif_transpose(image).convert("RGB")
            source = self._atlas_source_image
            if source is None: return
            if self.atlas_fit:
                self.update_idletasks()
                available_width = max(200, self.atlas_canvas.winfo_width() - 24)
                available_height = max(200, self.atlas_canvas.winfo_height() - 24)
                self.atlas_zoom = min(available_width / source.width, available_height / source.height, 1.0)
            width = max(1, round(source.width * self.atlas_zoom)); height = max(1, round(source.height * self.atlas_zoom))
            rendered = source.resize((width, height), Image.Resampling.LANCZOS)
            self._atlas_photo = ImageTk.PhotoImage(rendered)
            self.atlas_canvas.delete("all")
            self.atlas_canvas.create_image(0, 0, anchor="nw", image=self._atlas_photo, tags="page")
            self.atlas_canvas.configure(scrollregion=(0, 0, width, height))
            self.atlas_zoom_text.set(f"{round(self.atlas_zoom * 100)}%")
            self.atlas_page_title.set(f"{target.name}  ·  {source.width} x {source.height}px")
        except (ProjectError, OSError, ValueError) as error:
            self._atlas_source_image = None; self._atlas_photo = None
            self.atlas_canvas.delete("all")
            self.atlas_canvas.create_text(20, 20, anchor="nw", width=max(300, self.atlas_canvas.winfo_width() - 40), fill="#d7dde5", text=str(error), tags="message", font=("Segoe UI", 11))

    def fit_atlas_page(self) -> None:
        self.atlas_fit = True
        self.render_atlas_page()

    def zoom_atlas_page(self, factor: float) -> None:
        if self._atlas_source_image is None:
            self.render_atlas_page(reload_source=True)
            if self._atlas_source_image is None: return
        self.atlas_fit = False
        self.atlas_zoom = min(4.0, max(0.1, self.atlas_zoom * factor))
        self.render_atlas_page()

    def atlas_mouse_zoom(self, event) -> str:
        self.zoom_atlas_page(1.15 if event.delta > 0 else 1 / 1.15)
        return "break"

    def atlas_canvas_resized(self, _event=None) -> None:
        if not self.atlas_fit or self._atlas_source_image is None: return
        if self._atlas_resize_job is not None: self.after_cancel(self._atlas_resize_job)
        self._atlas_resize_job = self.after(120, self.render_atlas_page)

    def move_atlas_page(self, offset: int) -> None:
        children = list(self.atlas_table.get_children())
        if not children: return
        selected = self.atlas_table.selection()
        current = children.index(selected[0]) if selected and selected[0] in children else 0
        target = children[(current + offset) % len(children)]
        self.atlas_table.selection_set(target); self.atlas_table.focus(target); self.atlas_table.see(target)

    def open_selected_page(self) -> None:
        try:
            target = self.atlas_page_path()
            if os.name == "nt": os.startfile(target)  # type: ignore[attr-defined]
            elif sys.platform == "darwin": subprocess.Popen(["open", str(target)])
            else: subprocess.Popen(["xdg-open", str(target)])
        except (ProjectError, OSError) as error:
            messagebox.showerror("Unable to open page", str(error), parent=self)

    def save_atlas_bookmark(self) -> None:
        pages = self.selected_atlas_pages()
        if len(pages) != 1:
            messagebox.showinfo("Select one page", "Select exactly one Atlas page to bookmark.", parent=self); return
        try: value = self._require_project().save_research_object("BOOKMARK", f"Bookmark {pages[0]}", {}, page_refs=pages)
        except (ProjectError, OSError) as error:
            messagebox.showerror("Bookmark failed", str(error), parent=self); return
        self.status.set(f"Saved private bookmark {value['object_id']}.")
        self.refresh_research_objects()

    def save_atlas_pageset(self) -> None:
        pages = self.selected_atlas_pages()
        if not pages:
            messagebox.showinfo("Select pages", "Select one or more Atlas pages first.", parent=self); return
        title = simpledialog.askstring("Page Set", "Name this Page Set:", parent=self)
        if not title: return
        try: value = self._require_project().save_research_object("PAGE_SET", title, {"ordered_pages": pages}, page_refs=pages)
        except (ProjectError, OSError) as error:
            messagebox.showerror("Page Set failed", str(error), parent=self); return
        self.status.set(f"Saved Page Set {value['object_id']} with {len(pages)} page(s).")
        self.refresh_research_objects()

    def save_research_object(self) -> None:
        text_value = self.research_text.get("1.0", "end-1c").strip()
        pages = [item.strip() for item in self.research_pages.get().split(",") if item.strip()]
        try:
            payload: dict[str, object] = {"text": text_value}
            if self.research_type.get() == "REGION":
                coordinates = {"x":float(self.region_x.get()), "y":float(self.region_y.get()), "width":float(self.region_width.get()), "height":float(self.region_height.get())}
                if len(pages) != 1: raise ValueError("a Region must reference exactly one page")
                if any(value < 0 or value > 1 for value in coordinates.values()) or coordinates["width"] <= 0 or coordinates["height"] <= 0:
                    raise ValueError("Region coordinates must be normalized from 0 to 1 with positive width and height")
                payload.update(coordinates)
            result_refs = [str(self._result_by_item[item]["result_id"]) for item in self.history.selection()]
            value = self._require_project().save_research_object(self.research_type.get(), self.research_title.get(), payload, page_refs=pages, result_refs=result_refs)
        except (ProjectError, OSError, ValueError) as error:
            messagebox.showerror("Research object failed", str(error), parent=self); return
        self.research_text.delete("1.0", "end"); self.research_title.set("")
        self.research_summary.set(f"Saved {value['object_id']} as {value['object_type']}.")
        self.refresh_research_objects()

    def refresh_research_objects(self) -> None:
        for item in self.research_table.get_children(): self.research_table.delete(item)
        self._object_by_item.clear()
        if self.store is None: return
        try: values = self.store.list_research_objects()
        except (ProjectError, OSError, json.JSONDecodeError) as error:
            self.research_summary.set(f"Research history error: {error}"); return
        for value in reversed(values):
            item = self.research_table.insert("", "end", values=(value["object_type"], value["title"], ", ".join(value["page_refs"]), value["created_at"]))
            self._object_by_item[item] = value

    def export_selected_object(self) -> None:
        selected = self.research_table.selection()
        if not selected or self.store is None:
            messagebox.showinfo("Select an object", "Select a research object first.", parent=self); return
        value = self._object_by_item[selected[0]]
        destination = filedialog.asksaveasfilename(parent=self, title="Export portable research object", initialfile=f"{value['object_id']}.json", defaultextension=".json", filetypes=(("JSON","*.json"),))
        if not destination: return
        try: self.store.export_research_object(str(value["object_id"]), Path(destination))
        except (ProjectError, OSError, json.JSONDecodeError) as error:
            messagebox.showerror("Export failed", str(error), parent=self); return
        self.status.set(f"Exported research object {value['object_id']}.")

    def compare_selected_results(self) -> None:
        selected = self.history.selection()
        if len(selected) != 2:
            messagebox.showinfo("Select two Results", "Select exactly two different Results.", parent=self); return
        try:
            store = self._require_project()
            job = create_result_comparison_job(self._result_by_item[selected[0]], self._result_by_item[selected[1]])
            envelope = store.save_execution(job, execute_job(job), instrument_id="hms-result-comparator", instrument_version=VERSION)
        except (ProjectError, OSError, ValueError) as error:
            messagebox.showerror("Comparison failed", str(error), parent=self); return
        self.status.set(f"Saved structural comparison {envelope['result_id']}; no semantic conclusion was made.")
        self.refresh_history()

    def audit_project(self) -> None:
        try: report = self._require_project().audit()
        except (ProjectError, OSError, json.JSONDecodeError) as error:
            messagebox.showerror("Audit failed", str(error), parent=self); return
        counts = report["summary"]
        self.recovery_summary.set(f"{report['status']} - {counts['runs']} Runs, {counts['results']} Results, {counts['objects']} objects; index rebuilt. Problems: {len(report['problems'])}.")

    def backup_project(self) -> None:
        try: store = self._require_project()
        except ProjectError as error:
            messagebox.showerror("Backup failed", str(error), parent=self); return
        destination = filedialog.asksaveasfilename(parent=self, title="Create safe project backup", initialfile=f"{store.root.name}-metadata-backup.zip", defaultextension=".zip", filetypes=(("ZIP","*.zip"),))
        if not destination: return
        try: store.create_backup(Path(destination))
        except (ProjectError, OSError, zipfile.BadZipFile) as error:
            messagebox.showerror("Backup failed", str(error), parent=self); return
        self.recovery_summary.set("Backup created: corpus images, exports, and the private local corpus path were excluded.")

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
