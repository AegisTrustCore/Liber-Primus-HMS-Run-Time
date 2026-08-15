#!/usr/bin/env python3
"""Offline desktop interface for the HMS Corpus Manifest Verifier."""

from __future__ import annotations

import hashlib
import json
import queue
import sys
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import (
    CorpusManifestError,
    canonical_json,
    create_manifest,
    run_demo_self_test,
    validate_manifest,
    verify_manifest,
)

PRODUCT = "HMS Corpus Manifest Verifier"
VERSION = "0.1.0-rc.3"
CANONICAL_MANIFEST_NAME = "LP-75-IMAGES-v1.0.0.json"
FILTERS = ("All files", "Problems only", "Verified only")


def application_root() -> Path:
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else ROOT


def default_canonical_manifest() -> Path:
    if getattr(sys, "frozen", False):
        return application_root() / "canonical" / CANONICAL_MANIFEST_NAME
    return ROOT / "corpus" / "liber-primus" / "manifests" / CANONICAL_MANIFEST_NAME


def demo_root() -> Path:
    if getattr(sys, "frozen", False):
        return application_root() / "demo" / "corpus-verifier"
    return ROOT / "demo" / "corpus-verifier"


def inspect_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return safe, display-ready manifest identity information."""
    files = validate_manifest(manifest)
    return {
        "corpus_id": manifest["corpus_id"],
        "version": manifest["version"],
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "manifest_sha256": hashlib.sha256(canonical_json(manifest)).hexdigest(),
    }


def finding_matches(status: str, path: str, selected_filter: str, search: str) -> bool:
    if selected_filter == "Problems only" and status == "VERIFIED":
        return False
    if selected_filter == "Verified only" and status != "VERIFIED":
        return False
    needle = search.strip().casefold()
    return not needle or needle in path.casefold() or needle in status.casefold()


def infer_corpus_root(selected_files: list[Path], manifest: dict[str, Any]) -> tuple[Path, list[str]]:
    """Resolve selected declared files to one manifest root without enabling partial PASS."""
    if not selected_files:
        raise CorpusManifestError("select at least one corpus file")
    declared = {item["path"] for item in validate_manifest(manifest)}
    candidates: list[tuple[Path, str]] = []
    for selected in selected_files:
        selected = Path(selected).resolve(strict=True)
        if not selected.is_file():
            raise CorpusManifestError(f"selected path is not a file: {selected}")
        matches: list[tuple[Path, str]] = []
        for relative in declared:
            parts = Path(*relative.split("/")).parts
            if len(selected.parts) >= len(parts) and tuple(selected.parts[-len(parts):]) == parts:
                matches.append((selected.parents[len(parts) - 1], relative))
        if len(matches) != 1:
            raise CorpusManifestError(f"selected file does not map uniquely to the manifest: {selected.name}")
        candidates.append(matches[0])
    roots = {root for root, _relative in candidates}
    if len(roots) != 1:
        raise CorpusManifestError("selected files do not share one manifest root")
    relative_paths = [relative for _root, relative in candidates]
    if len(relative_paths) != len(set(relative_paths)):
        raise CorpusManifestError("the same declared file was selected more than once")
    return roots.pop(), sorted(relative_paths)


def packaged_self_test() -> dict[str, Any]:
    packaged_demo = demo_root()
    if packaged_demo.is_dir():
        return run_demo_self_test(packaged_demo)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "known.txt").write_text("HMS corpus control\n", encoding="utf-8")
        manifest = create_manifest(root, "HMS-CORPUS-CONTROL", "1")
        passed = verify_manifest(manifest, root, strict=True)["status"] == "PASS"
        (root / "known.txt").write_text("tampered\n", encoding="utf-8")
        rejected = verify_manifest(manifest, root, strict=True)["status"] == "FAIL"
        return {
            "schema": "HMS_CORPUS_FALLBACK_SELF_TEST_V1",
            "passed": passed and rejected,
            "cases": {
                "GOOD": {"passed": passed},
                "ALTERED": {"passed": rejected},
            },
        }


class CorpusVerifierApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT} {VERSION}")
        self.geometry("1120x760")
        self.minsize(820, 590)
        canonical = default_canonical_manifest()
        self.manifest_path = tk.StringVar(value=str(canonical) if canonical.is_file() else "")
        self.root_path = tk.StringVar()
        self.strict = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Ready. Choose the folder containing the corpus files.")
        self.summary = tk.StringVar(value="No verification has been run.")
        self.manifest_summary = tk.StringVar(value="No manifest selected.")
        self.selection_summary = tk.StringVar(value="Choose the corpus folder or select one or more declared page files.")
        self.filter_mode = tk.StringVar(value=FILTERS[0])
        self.search_text = tk.StringVar()
        self.report: dict[str, Any] | None = None
        self._rows: list[dict[str, Any]] = []
        self._work_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._busy = False
        self._build()
        self._bind_shortcuts()
        self.search_text.trace_add("write", lambda *_: self._render_findings())
        self.filter_mode.trace_add("write", lambda *_: self._render_findings())
        if canonical.is_file():
            self._inspect_selected_manifest(show_error=False)

    def _build(self) -> None:
        style = ttk.Style(self)
        style.configure("Authority.TLabel", foreground="#315f7d", font=("Segoe UI", 9, "bold"))
        style.configure("Pass.TLabel", foreground="#177245", font=("Segoe UI", 12, "bold"))
        style.configure("Fail.TLabel", foreground="#a32626", font=("Segoe UI", 12, "bold"))

        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)
        header = ttk.Frame(frame)
        header.pack(fill="x")
        ttk.Label(header, text=PRODUCT, font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Label(header, text="PROVENANCE | OFFLINE | READ-ONLY", style="Authority.TLabel").pack(side="right", pady=(7, 0))
        ttk.Label(frame, text="Verify local file identity without uploading or modifying corpus material.").pack(anchor="w", pady=(0, 12))

        self._path_row(frame, "Manifest", self.manifest_path, self.choose_manifest, ("Use canonical", self.use_canonical))
        ttk.Label(frame, textvariable=self.manifest_summary, foreground="#4a5568").pack(anchor="w", padx=(106, 0), pady=(0, 4))
        self._path_row(frame, "Corpus root", self.root_path, self.choose_root, ("Select page files", self.choose_page_files))
        ttk.Label(frame, textvariable=self.selection_summary, foreground="#4a5568").pack(anchor="w", padx=(106, 0), pady=(0, 4))

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(8, 4))
        ttk.Checkbutton(controls, text="Strict: reject undeclared files", variable=self.strict).pack(side="left")
        self.verify_button = ttk.Button(controls, text="Verify corpus", command=self.verify)
        self.verify_button.pack(side="left", padx=(12, 4))
        self.export_button = ttk.Button(controls, text="Export report", command=self.export, state="disabled")
        self.export_button.pack(side="left", padx=4)
        ttk.Button(controls, text="Clear", command=self.clear_results).pack(side="left", padx=4)
        ttk.Button(controls, text="Self-test", command=self.self_test).pack(side="left", padx=4)
        ttk.Button(controls, text="About", command=self.about).pack(side="right")

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(2, 6))
        self.summary_label = ttk.Label(frame, textvariable=self.summary, font=("Segoe UI", 11, "bold"))
        self.summary_label.pack(anchor="w", pady=(2, 4))

        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True, pady=(2, 0))
        findings_tab = ttk.Frame(notebook, padding=6)
        raw_tab = ttk.Frame(notebook, padding=6)
        notebook.add(findings_tab, text="File findings")
        notebook.add(raw_tab, text="Portable report JSON")

        filter_bar = ttk.Frame(findings_tab)
        filter_bar.pack(fill="x", pady=(0, 6))
        ttk.Label(filter_bar, text="Show").pack(side="left")
        ttk.Combobox(filter_bar, textvariable=self.filter_mode, values=FILTERS, state="readonly", width=16).pack(side="left", padx=(5, 12))
        ttk.Label(filter_bar, text="Search").pack(side="left")
        self.search_entry = ttk.Entry(filter_bar, textvariable=self.search_text)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 8))
        ttk.Button(filter_bar, text="Copy selected", command=self.copy_selected).pack(side="right")

        columns = ("status", "path", "expected", "actual", "expected_hash", "actual_hash")
        tree_frame = ttk.Frame(findings_tab)
        tree_frame.pack(fill="both", expand=True)
        self.findings = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        column_settings = (
            ("status", "Status", 100),
            ("path", "File", 240),
            ("expected", "Expected bytes", 110),
            ("actual", "Actual bytes", 110),
            ("expected_hash", "Expected SHA-256", 170),
            ("actual_hash", "Actual SHA-256", 170),
        )
        for column, label, width in column_settings:
            self.findings.heading(column, text=label, command=lambda name=column: self.sort_findings(name))
            self.findings.column(column, width=width, minwidth=80, anchor="w")
        self.findings.tag_configure("VERIFIED", foreground="#177245")
        self.findings.tag_configure("MISMATCH", foreground="#a32626")
        self.findings.tag_configure("MISSING", foreground="#a32626")
        self.findings.tag_configure("UNSAFE", foreground="#a32626")
        self.findings.tag_configure("UNEXPECTED", foreground="#995500")
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.findings.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.findings.xview)
        self.findings.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.findings.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        raw_frame = ttk.Frame(raw_tab)
        raw_frame.pack(fill="both", expand=True)
        self.output = tk.Text(raw_frame, wrap="none", state="disabled", font=("Consolas", 10))
        raw_y = ttk.Scrollbar(raw_frame, orient="vertical", command=self.output.yview)
        raw_x = ttk.Scrollbar(raw_frame, orient="horizontal", command=self.output.xview)
        self.output.configure(yscrollcommand=raw_y.set, xscrollcommand=raw_x.set)
        self.output.grid(row=0, column=0, sticky="nsew")
        raw_y.grid(row=0, column=1, sticky="ns")
        raw_x.grid(row=1, column=0, sticky="ew")
        raw_frame.rowconfigure(0, weight=1)
        raw_frame.columnconfigure(0, weight=1)

        footer = ttk.Frame(frame)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Label(footer, textvariable=self.status).pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="Copy report digest", command=self.copy_report_digest).pack(side="right")

    def _path_row(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        command: object,
        extra: tuple[str, object] | None = None,
    ) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=14).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=command).pack(side="left", padx=(6, 0))
        if extra:
            ttk.Button(row, text=extra[0], command=extra[1]).pack(side="left", padx=(6, 0))

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-o>", lambda _event: self.choose_manifest())
        self.bind("<Control-Shift-O>", lambda _event: self.choose_root())
        self.bind("<Control-Return>", lambda _event: self.verify())
        self.bind("<Control-s>", lambda _event: self.export())
        self.bind("<Control-f>", lambda _event: self.search_entry.focus_set())
        self.bind("<F1>", lambda _event: self.about())

    def _inspect_selected_manifest(self, show_error: bool = True) -> dict[str, Any] | None:
        try:
            manifest = json.loads(Path(self.manifest_path.get()).read_text(encoding="utf-8"))
            identity = inspect_manifest(manifest)
        except (CorpusManifestError, OSError, UnicodeError, json.JSONDecodeError) as error:
            self.manifest_summary.set(f"Manifest unavailable: {error}")
            if show_error:
                messagebox.showerror("Manifest error", str(error), parent=self)
            return None
        size_mib = identity["total_bytes"] / (1024 * 1024)
        self.manifest_summary.set(
            f"{identity['corpus_id']} v{identity['version']} | {identity['file_count']} files | "
            f"{size_mib:.1f} MiB | SHA-256 {identity['manifest_sha256']}"
        )
        return manifest

    def choose_manifest(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self,
            title="Choose corpus manifest",
            filetypes=(("JSON", "*.json"), ("All files", "*.*")),
        )
        if selected:
            self.manifest_path.set(selected)
            self._inspect_selected_manifest()

    def use_canonical(self) -> None:
        canonical = default_canonical_manifest()
        if not canonical.is_file():
            messagebox.showerror("Canonical manifest unavailable", f"Not found: {canonical}", parent=self)
            return
        self.manifest_path.set(str(canonical))
        self._inspect_selected_manifest()
        self.status.set("Canonical 75-page manifest selected.")

    def choose_root(self) -> None:
        selected = filedialog.askdirectory(parent=self, title="Choose corpus root", mustexist=True)
        if selected:
            self.root_path.set(selected)
            self.selection_summary.set("Corpus folder selected directly. Full-manifest verification will check every declared file.")
            self.status.set("Corpus folder selected. Verification has not run yet.")

    def choose_page_files(self) -> None:
        manifest = self._inspect_selected_manifest()
        if manifest is None:
            return
        selected = filedialog.askopenfilenames(
            parent=self,
            title="Select one or more declared corpus page files",
            initialdir=self.root_path.get().strip() or None,
            filetypes=(("Page images", "*.jpg *.jpeg *.png"), ("All files", "*.*")),
        )
        if not selected:
            return
        try:
            root, relative_paths = infer_corpus_root([Path(path) for path in selected], manifest)
        except (CorpusManifestError, OSError) as error:
            messagebox.showerror("Page selection error", str(error), parent=self)
            return
        declared_count = len(validate_manifest(manifest))
        self.root_path.set(str(root))
        self.selection_summary.set(
            f"Selected {len(relative_paths)} of {declared_count} declared files. "
            "Their shared root is loaded; Verify corpus will still check the complete manifest."
        )
        self.status.set(f"Loaded corpus root from selected file(s): {', '.join(relative_paths[:4])}" + ("..." if len(relative_paths) > 4 else ""))

    def verify(self) -> None:
        if self._busy:
            return
        manifest = self._inspect_selected_manifest()
        if manifest is None:
            return
        root_text = self.root_path.get().strip()
        if not root_text:
            messagebox.showinfo("Choose a corpus folder", "Select the folder containing the declared files first.", parent=self)
            return
        root = Path(root_text)
        if not root.is_dir():
            messagebox.showerror("Corpus folder unavailable", f"Not a readable folder: {root}", parent=self)
            return
        strict = self.strict.get()
        if not strict:
            proceed = messagebox.askokcancel(
                "Strict mode is off",
                "Undeclared files will not be reported. Continue with a non-strict check?",
                parent=self,
            )
            if not proceed:
                return
        self._set_busy(True)
        self.status.set("Verifying locally. Files are being read but are never uploaded or modified...")
        worker = threading.Thread(target=self._verify_worker, args=(manifest, root, strict), daemon=True)
        worker.start()
        self.after(100, self._poll_worker)

    def _verify_worker(self, manifest: dict[str, Any], root: Path, strict: bool) -> None:
        try:
            self._work_queue.put(("result", verify_manifest(manifest, root, strict)))
        except Exception as error:  # surfaced safely on the UI thread
            self._work_queue.put(("error", error))

    def _poll_worker(self) -> None:
        try:
            kind, value = self._work_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_worker)
            return
        self._set_busy(False)
        if kind == "error":
            self.status.set(f"Error: {value}")
            messagebox.showerror("Verification error", str(value), parent=self)
            return
        self.report = value if isinstance(value, dict) else None
        if self.report is None:
            messagebox.showerror("Verification error", "The verifier returned no report.", parent=self)
            return
        self._display_report()

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.verify_button.configure(state="disabled" if busy else "normal")
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _display_report(self) -> None:
        assert self.report is not None
        self._rows = [finding for finding in self.report.get("files", []) if isinstance(finding, dict)]
        for path in self.report.get("unexpected_files", []):
            self._rows.append({"status": "UNEXPECTED", "path": path})
        self._render_findings()
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", json.dumps(self.report, ensure_ascii=False, indent=2))
        self.output.configure(state="disabled")
        summary = self.report["summary"]
        self.summary.set(
            f"{self.report['status']} | {summary['verified']} verified | {summary['mismatch']} altered | "
            f"{summary['missing']} missing | {summary['unsafe']} unsafe | {summary['unexpected']} extra"
        )
        self.summary_label.configure(style="Pass.TLabel" if self.report["status"] == "PASS" else "Fail.TLabel")
        self.status.set(
            f"{self.report['status']}: report digest {self.report['report_sha256']}. "
            "PASS means declared byte identity only."
        )
        self.export_button.configure(state="normal")

    def _render_findings(self) -> None:
        if not hasattr(self, "findings"):
            return
        for item in self.findings.get_children():
            self.findings.delete(item)
        selected_filter = self.filter_mode.get()
        search = self.search_text.get()
        for row in self._rows:
            status = str(row.get("status", ""))
            path = str(row.get("path", ""))
            if not finding_matches(status, path, selected_filter, search):
                continue
            values = (
                status,
                path,
                row.get("expected_bytes", ""),
                row.get("actual_bytes", ""),
                row.get("expected_sha256", ""),
                row.get("actual_sha256", ""),
            )
            self.findings.insert("", "end", values=values, tags=(status,))

    def sort_findings(self, column: str) -> None:
        if not hasattr(self, "_sort_state"):
            self._sort_state: dict[str, bool] = {}
        descending = self._sort_state.get(column, False)
        self._sort_state[column] = not descending
        items = [(self.findings.set(item, column), item) for item in self.findings.get_children("")]

        def key(item: tuple[str, str]) -> tuple[int, object]:
            value = item[0]
            try:
                return (0, int(value))
            except ValueError:
                return (1, value.casefold())

        for index, (_value, item) in enumerate(sorted(items, key=key, reverse=descending)):
            self.findings.move(item, "", index)

    def copy_selected(self) -> None:
        selected = self.findings.selection()
        if not selected:
            messagebox.showinfo("Nothing selected", "Select one or more finding rows first.", parent=self)
            return
        lines = ["\t".join(str(value) for value in self.findings.item(item, "values")) for item in selected]
        self.clipboard_clear()
        self.clipboard_append("\n".join(lines))
        self.status.set(f"Copied {len(lines)} finding row(s).")

    def copy_report_digest(self) -> None:
        if self.report is None:
            messagebox.showinfo("No report", "Run verification first.", parent=self)
            return
        digest = str(self.report["report_sha256"])
        self.clipboard_clear()
        self.clipboard_append(digest)
        self.status.set("Copied the portable report SHA-256 digest.")

    def export(self) -> None:
        if self.report is None:
            messagebox.showinfo("Nothing to export", "Run verification first.", parent=self)
            return
        corpus = str(self.report.get("corpus_id", "corpus")).replace("/", "-")
        default_name = f"{corpus}-{self.report['status'].lower()}-verification.json"
        selected = filedialog.asksaveasfilename(
            parent=self,
            title="Export portable verification report",
            initialfile=default_name,
            defaultextension=".json",
            filetypes=(("JSON", "*.json"),),
        )
        if selected:
            try:
                Path(selected).write_text(json.dumps(self.report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except OSError as error:
                messagebox.showerror("Unable to export", str(error), parent=self)
                return
            self.status.set(f"Exported {Path(selected).name}. The report contains no corpus-root path.")

    def clear_results(self) -> None:
        if self._busy:
            return
        self.report = None
        self._rows = []
        self._render_findings()
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.summary.set("No verification has been run.")
        self.summary_label.configure(style="TLabel")
        self.export_button.configure(state="disabled")
        self.status.set("Results cleared. Selected paths were kept for another check.")

    def self_test(self) -> None:
        try:
            result = packaged_self_test()
        except (CorpusManifestError, OSError, UnicodeError, json.JSONDecodeError) as error:
            self.status.set("Self-test failed. Do not rely on this build.")
            messagebox.showerror("Self-test failed", str(error), parent=self)
            return
        cases = result.get("cases", {})
        lines = [f"{name}: {'PASS' if details.get('passed') else 'FAIL'}" for name, details in cases.items()]
        passed = bool(result.get("passed"))
        self.status.set("Self-test passed." if passed else "Self-test failed. Do not rely on this build.")
        if passed:
            messagebox.showinfo("Self-test passed", "All packaged controls behaved as expected.\n\n" + "\n".join(lines), parent=self)
        else:
            messagebox.showerror("Self-test failed", "Do not rely on this build.\n\n" + "\n".join(lines), parent=self)

    def about(self) -> None:
        messagebox.showinfo(
            "About",
            f"{PRODUCT} {VERSION}\n\n"
            "Authority: PROVENANCE\n"
            "Offline, read-only, no accounts, telemetry, or network access.\n\n"
            "A matching hash establishes byte identity only - not authenticity, rights, "
            "transcription correctness, or a solve.\n\n"
            "Select page files can locate a corpus root from one or more declared pages; verification still checks the full manifest.\n\n"
            "Shortcuts: Ctrl+O manifest | Ctrl+Shift+O corpus folder | Ctrl+Enter verify | "
            "Ctrl+S export | Ctrl+F search | F1 help",
            parent=self,
        )


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return 0 if packaged_self_test()["passed"] else 1
    CorpusVerifierApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
