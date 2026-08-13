#!/usr/bin/env python3
"""Offline Windows interface for the HMS GP29 calculator."""

from __future__ import annotations

import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.gp29 import GP29InputError, calculate, self_test

PRODUCT = "HMS GP29 Calculator"
VERSION = "0.1.0-rc.1"


class GP29App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT} {VERSION}")
        self.geometry("920x680")
        self.minsize(720, 520)
        self.result: dict[str, object] | None = None
        self.mode = tk.StringVar(value="auto")
        self.status = tk.StringVar(value="Ready. Input is never modified.")
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=PRODUCT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Deterministic Gematria Primus calculation — not a decoder or solve claim.").pack(anchor="w", pady=(0, 12))

        bar = ttk.Frame(frame)
        bar.pack(fill="x")
        ttk.Label(bar, text="Input mode:").pack(side="left")
        ttk.Combobox(bar, textvariable=self.mode, values=("auto", "runes", "tokens"), width=10, state="readonly").pack(side="left", padx=6)
        ttk.Button(bar, text="Load UTF-8 file", command=self.load_file).pack(side="left", padx=4)
        ttk.Button(bar, text="Calculate", command=self.run_calculation).pack(side="left", padx=4)
        ttk.Button(bar, text="Export JSON", command=self.export_json).pack(side="left", padx=4)
        ttk.Button(bar, text="Self-test", command=self.run_self_test).pack(side="left", padx=4)
        ttk.Button(bar, text="About", command=self.show_about).pack(side="right")

        ttk.Label(frame, text="Runes, or explicit tokens separated by spaces/commas (example: F U/V TH):").pack(anchor="w", pady=(12, 4))
        self.input_text = tk.Text(frame, height=7, wrap="word", undo=True)
        self.input_text.pack(fill="x")

        ttk.Label(frame, text="Result:").pack(anchor="w", pady=(12, 4))
        self.output_text = tk.Text(frame, wrap="none", state="disabled", font=("Consolas", 10))
        self.output_text.pack(fill="both", expand=True)
        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=(8, 0))

    def _display(self, value: object) -> None:
        rendered = json.dumps(value, ensure_ascii=False, indent=2)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", rendered)
        self.output_text.configure(state="disabled")

    def run_calculation(self) -> None:
        try:
            self.result = calculate(self.input_text.get("1.0", "end-1c"), self.mode.get())
        except GP29InputError as error:
            self.status.set(f"Input error: {error}")
            messagebox.showerror("GP29 input error", str(error), parent=self)
            return
        self._display(self.result)
        self.status.set(f"Calculated {self.result['rune_count']} runes; GP sum {self.result['gp_sum']}.")

    def load_file(self) -> None:
        selected = filedialog.askopenfilename(parent=self, title="Open UTF-8 input", filetypes=(("Text", "*.txt"), ("All files", "*.*")))
        if not selected:
            return
        try:
            value = Path(selected).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            messagebox.showerror("Unable to open file", str(error), parent=self)
            return
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", value)
        self.status.set(f"Loaded {Path(selected).name} as UTF-8.")

    def export_json(self) -> None:
        if self.result is None:
            messagebox.showinfo("Nothing to export", "Calculate a value first.", parent=self)
            return
        selected = filedialog.asksaveasfilename(parent=self, title="Export GP29 result", defaultextension=".json", filetypes=(("JSON", "*.json"),))
        if not selected:
            return
        try:
            Path(selected).write_text(json.dumps(self.result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Unable to export", str(error), parent=self)
            return
        self.status.set(f"Exported {Path(selected).name}.")

    def run_self_test(self) -> None:
        report = self_test()
        self._display(report)
        self.status.set(f"Self-test: {report['passed']} passed, {report['failed']} failed.")
        if report["failed"]:
            messagebox.showerror("Self-test failed", "Do not rely on this build.", parent=self)

    def show_about(self) -> None:
        messagebox.showinfo(
            "About HMS GP29",
            f"{PRODUCT} {VERSION}\n\nOffline and deterministic. No accounts, telemetry, or network access.\n\nGP29 calculates declared values; it does not decode Liber Primus.",
            parent=self,
        )


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        report = self_test()
        return 0 if report["failed"] == 0 else 1
    GP29App().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
