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

from hms_tools.gp29 import GP29InputError, TABLE, calculate, format_human, self_test

PRODUCT = "HMS GP29 Calculator"
VERSION = "0.1.1-rc.1"
MODE_LABELS = {
    "English letters (A-Z)": "letters",
    "Latin sounds (longest match)": "latin",
    "Explicit sound tokens": "tokens",
    "Gematria Primus runes": "runes",
    "Automatic (legacy)": "auto",
}
MODE_HELP = {
    "letters": "Each English letter stays separate: TH becomes T + H. Recommended for ordinary words.",
    "latin": "GP29 sound clusters take priority: TH is one rune and ING is one rune.",
    "tokens": "Use separated sounds for exact control, for example: T H I N G or TH ING.",
    "runes": "Enter or insert only the 29 Gematria Primus runes.",
    "auto": "Legacy detection chooses runes, explicit tokens, or Latin sounds. Use a named mode when precision matters.",
}


class GP29App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{PRODUCT} {VERSION}")
        self.geometry("1180x760")
        self.minsize(940, 620)
        self.result: dict[str, object] | None = None
        self.mode_label = tk.StringVar(value="English letters (A-Z)")
        self.mode_help = tk.StringVar(value=MODE_HELP["letters"])
        self.status = tk.StringVar(value="Ready. English-letter mode keeps H separate from TH.")
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=PRODUCT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Deterministic Gematria Primus calculation — not a decoder or solve claim.").pack(anchor="w", pady=(0, 12))

        bar = ttk.Frame(frame)
        bar.pack(fill="x")
        ttk.Label(bar, text="Input mode:").pack(side="left")
        mode_box = ttk.Combobox(bar, textvariable=self.mode_label, values=tuple(MODE_LABELS), width=29, state="readonly")
        mode_box.pack(side="left", padx=6)
        mode_box.bind("<<ComboboxSelected>>", self._mode_changed)
        ttk.Button(bar, text="Load UTF-8 file", command=self.load_file).pack(side="left", padx=4)
        ttk.Button(bar, text="Calculate", command=self.run_calculation).pack(side="left", padx=4)
        ttk.Button(bar, text="Export JSON", command=self.export_json).pack(side="left", padx=4)
        ttk.Button(bar, text="Clear", command=self.clear_input).pack(side="left", padx=4)
        ttk.Button(bar, text="Self-test", command=self.run_self_test).pack(side="left", padx=4)
        ttk.Button(bar, text="About", command=self.show_about).pack(side="right")
        ttk.Label(frame, textvariable=self.mode_help, foreground="#4a5568").pack(anchor="w", pady=(6, 10))

        workspace = ttk.Panedwindow(frame, orient="horizontal")
        workspace.pack(fill="both", expand=True)
        calculator = ttk.Frame(workspace, padding=(0, 0, 12, 0))
        alphabet = ttk.LabelFrame(workspace, text="Gematria Primus alphabet", padding=8)
        workspace.add(calculator, weight=3)
        workspace.add(alphabet, weight=2)

        ttk.Label(calculator, text="Input:").pack(anchor="w", pady=(0, 4))
        self.input_text = tk.Text(calculator, height=7, wrap="word", undo=True, font=("Segoe UI", 11))
        self.input_text.pack(fill="x")
        ttk.Label(calculator, text="Result:").pack(anchor="w", pady=(12, 4))
        self.output_text = tk.Text(calculator, wrap="none", state="disabled", font=("Consolas", 10))
        self.output_text.pack(fill="both", expand=True)

        ttk.Label(alphabet, text="Select a row, then insert its exact sound or rune.", wraplength=380).pack(anchor="w", pady=(0, 6))
        table_frame = ttk.Frame(alphabet)
        table_frame.pack(fill="both", expand=True)
        columns = ("rune", "sound", "prime", "L", "R", "N", "Q")
        self.alphabet_table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", height=20)
        widths = {"rune": 48, "sound": 75, "prime": 48, "L": 34, "R": 34, "N": 34, "Q": 34}
        for column in columns:
            self.alphabet_table.heading(column, text=column)
            self.alphabet_table.column(column, width=widths[column], minwidth=30, anchor="center", stretch=column == "sound")
        for entry in TABLE:
            self.alphabet_table.insert("", "end", iid=str(entry.index), values=(entry.rune, entry.sound, entry.prime, entry.L, entry.R, entry.N, entry.Q))
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.alphabet_table.yview)
        self.alphabet_table.configure(yscrollcommand=scrollbar.set)
        self.alphabet_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.alphabet_table.selection_set("0")
        self.alphabet_table.bind("<Double-1>", lambda _event: self.insert_selected_token())

        alphabet_buttons = ttk.Frame(alphabet)
        alphabet_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(alphabet_buttons, text="Insert sound token", command=self.insert_selected_token).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(alphabet_buttons, text="Insert rune", command=self.insert_selected_rune).pack(side="left", fill="x", expand=True, padx=(4, 0))
        ttk.Label(alphabet, text="Tip: double-click a row to insert its sound token.", foreground="#4a5568").pack(anchor="w", pady=(6, 0))
        ttk.Label(frame, textvariable=self.status).pack(anchor="w", pady=(8, 0))

    def _selected_mode(self) -> str:
        return MODE_LABELS[self.mode_label.get()]

    def _mode_changed(self, _event: object | None = None) -> None:
        self.mode_help.set(MODE_HELP[self._selected_mode()])

    def clear_input(self) -> None:
        self.input_text.delete("1.0", "end")
        self.result = None
        self.status.set("Input cleared.")

    def _prepare_insert(self, target_mode: str, target_label: str) -> bool:
        current = self._selected_mode()
        existing = self.input_text.get("1.0", "end-1c").strip()
        if existing and current != target_mode:
            approved = messagebox.askyesno(
                "Switch input mode?",
                f"The current input uses {self.mode_label.get()}.\n\nClear it and switch to {target_label}?",
                parent=self,
            )
            if not approved:
                return False
            self.input_text.delete("1.0", "end")
        label = next(label for label, mode in MODE_LABELS.items() if mode == target_mode)
        self.mode_label.set(label)
        self._mode_changed()
        return True

    def _selected_entry(self):
        selection = self.alphabet_table.selection()
        return TABLE[int(selection[0])] if selection else None

    def insert_selected_token(self) -> None:
        entry = self._selected_entry()
        if entry is None or not self._prepare_insert("tokens", "explicit sound tokens"):
            return
        existing = self.input_text.get("1.0", "end-1c")
        separator = " " if existing and not existing[-1].isspace() else ""
        self.input_text.insert("end", separator + entry.sound)
        self.input_text.focus_set()
        self.status.set(f"Inserted sound token {entry.sound} (prime {entry.prime}).")

    def insert_selected_rune(self) -> None:
        entry = self._selected_entry()
        if entry is None or not self._prepare_insert("runes", "Gematria Primus runes"):
            return
        self.input_text.insert("end", entry.rune)
        self.input_text.focus_set()
        self.status.set(f"Inserted rune {entry.rune} / {entry.sound} (prime {entry.prime}).")

    def _display(self, value: object) -> None:
        self._display_text(json.dumps(value, ensure_ascii=False, indent=2))

    def _display_text(self, rendered: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", rendered)
        self.output_text.configure(state="disabled")

    def run_calculation(self) -> None:
        try:
            self.result = calculate(self.input_text.get("1.0", "end-1c"), self._selected_mode())
        except GP29InputError as error:
            self.status.set(f"Input error: {error}")
            messagebox.showerror("GP29 input error", str(error), parent=self)
            return
        self._display_text(format_human(self.result))
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
            f"{PRODUCT} {VERSION}\n\nOffline and deterministic. No accounts, telemetry, or network access.\n\nEnglish-letter mode keeps adjacent letters separate. Latin-sound mode applies the documented longest-match rule.\n\nGP29 calculates declared values; it does not decode Liber Primus.",
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
