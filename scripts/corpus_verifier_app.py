#!/usr/bin/env python3
"""Offline desktop interface for the HMS Corpus Manifest Verifier."""

from __future__ import annotations

import json
import sys
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.corpus_manifest import CorpusManifestError, create_manifest, verify_manifest

PRODUCT = "HMS Corpus Manifest Verifier"
VERSION = "0.1.0-dev"


def packaged_self_test() -> bool:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "known.txt").write_text("HMS corpus control\n", encoding="utf-8")
        manifest = create_manifest(root, "HMS-CORPUS-CONTROL", "1")
        passed = verify_manifest(manifest, root, strict=True)["status"] == "PASS"
        (root / "known.txt").write_text("tampered\n", encoding="utf-8")
        rejected = verify_manifest(manifest, root, strict=True)["status"] == "FAIL"
        return passed and rejected


class CorpusVerifierApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT} {VERSION}")
        self.geometry("960x680")
        self.minsize(740, 520)
        self.manifest_path = tk.StringVar()
        self.root_path = tk.StringVar()
        self.strict = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Ready. Verification is read-only.")
        self.report: dict[str, object] | None = None
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=PRODUCT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Verify local file identity without uploading or modifying corpus material.").pack(anchor="w", pady=(0, 14))
        self._path_row(frame, "Manifest", self.manifest_path, self.choose_manifest)
        self._path_row(frame, "Corpus root", self.root_path, self.choose_root)
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=8)
        ttk.Checkbutton(controls, text="Strict: reject undeclared files", variable=self.strict).pack(side="left")
        ttk.Button(controls, text="Verify", command=self.verify).pack(side="left", padx=6)
        ttk.Button(controls, text="Export report", command=self.export).pack(side="left", padx=6)
        ttk.Button(controls, text="Self-test", command=self.self_test).pack(side="left", padx=6)
        ttk.Button(controls, text="About", command=self.about).pack(side="right")
        self.output = tk.Text(frame, wrap="none", state="disabled", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, pady=(8, 0))
        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=(8, 0))

    def _path_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, command: object) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=12).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=command).pack(side="left", padx=(6, 0))

    def _display(self, value: object) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", json.dumps(value, ensure_ascii=False, indent=2))
        self.output.configure(state="disabled")

    def choose_manifest(self) -> None:
        selected = filedialog.askopenfilename(parent=self, title="Choose corpus manifest", filetypes=(("JSON", "*.json"), ("All files", "*.*")))
        if selected:
            self.manifest_path.set(selected)

    def choose_root(self) -> None:
        selected = filedialog.askdirectory(parent=self, title="Choose corpus root")
        if selected:
            self.root_path.set(selected)

    def verify(self) -> None:
        try:
            manifest = json.loads(Path(self.manifest_path.get()).read_text(encoding="utf-8"))
            self.report = verify_manifest(manifest, Path(self.root_path.get()), self.strict.get())
        except (CorpusManifestError, OSError, UnicodeError, json.JSONDecodeError) as error:
            self.status.set(f"Error: {error}")
            messagebox.showerror("Verification error", str(error), parent=self)
            return
        self._display(self.report)
        summary = self.report["summary"]
        self.status.set(f"{self.report['status']}: {summary['verified']} verified, {summary['mismatch']} mismatched, {summary['missing']} missing, {summary['unexpected']} unexpected.")

    def export(self) -> None:
        if self.report is None:
            messagebox.showinfo("Nothing to export", "Run verification first.", parent=self)
            return
        selected = filedialog.asksaveasfilename(parent=self, title="Export verification report", defaultextension=".json", filetypes=(("JSON", "*.json"),))
        if selected:
            try:
                Path(selected).write_text(json.dumps(self.report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except OSError as error:
                messagebox.showerror("Unable to export", str(error), parent=self)
                return
            self.status.set(f"Exported {Path(selected).name}.")

    def self_test(self) -> None:
        passed = packaged_self_test()
        self.status.set("Self-test passed." if passed else "Self-test failed. Do not rely on this build.")
        if not passed:
            messagebox.showerror("Self-test failed", "Do not rely on this build.", parent=self)

    def about(self) -> None:
        messagebox.showinfo("About", f"{PRODUCT} {VERSION}\n\nOffline, read-only, no accounts, telemetry, or network access.\n\nA matching hash establishes byte identity only—not authenticity, rights, transcription correctness, or a solve.", parent=self)


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return 0 if packaged_self_test() else 1
    CorpusVerifierApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
