#!/usr/bin/env python3
"""Offline desktop interface for HMS Expedition verification."""

from __future__ import annotations

import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.challenge_verifier import verify_answer
from hms_tools.expedition_verifier import build_receipt, packaged_self_test
from hms_tools.expedition_001 import CHALLENGE_ID, HINTS, VERSION, hint_text, instructions_text


class VerifierApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(f"HMS Endeavour — Expedition Verifier {VERSION}")
        root.geometry("680x470")
        root.minsize(600, 420)
        self.receipt: dict[str, object] | None = None

        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="HMS ENDEAVOUR", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Expedition Verifier", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Local verifier · no account · no telemetry · no network request").pack(anchor="w", pady=(4, 20))

        ttk.Label(frame, text="Expedition").pack(anchor="w")
        ttk.Label(frame, text="XPD-0001 — The Evidence Ledger").pack(anchor="w", pady=(2, 12))
        ttk.Label(frame, text="Submission").pack(anchor="w")
        self.answer = ttk.Entry(frame, font=("Segoe UI", 13), show="")
        self.answer.pack(fill="x", pady=(6, 12))
        self.answer.bind("<Return>", lambda _event: self.verify())

        actions = ttk.Frame(frame)
        actions.pack(fill="x")
        ttk.Button(actions, text="Verify", command=self.verify).pack(side="left")
        ttk.Button(actions, text="Copy receipt", command=self.copy_receipt).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Save result", command=self.save_receipt).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="How to solve", command=self.show_instructions).pack(side="right")
        ttk.Button(actions, text="Next hint", command=self.show_hint).pack(side="right", padx=(0, 8))

        ttk.Separator(frame).pack(fill="x", pady=(20, 14))
        self.status = tk.StringVar(value="Ready. Enter a submission and select Verify.")
        ttk.Label(frame, textvariable=self.status, wraplength=610, font=("Segoe UI", 11, "bold")).pack(anchor="w", fill="x")
        self.details = tk.StringVar(value="No result yet.")
        ttk.Label(frame, textvariable=self.details, wraplength=610).pack(anchor="w", fill="x", pady=(8, 0))
        ttk.Label(frame, text=f"Verifier {VERSION} · {CHALLENGE_ID} · Practice preview · Campaign closed").pack(anchor="w", pady=(24, 0))
        self.hint_level = 0
        self.answer.focus_set()

    def verify(self) -> None:
        result = verify_answer(CHALLENGE_ID, self.answer.get())
        if result.code == 2:
            self.receipt = None
            self.status.set("INPUT ERROR")
            self.details.set(result.message)
            return
        self.receipt = build_receipt(CHALLENGE_ID, self.answer.get(), result, VERSION)
        if result.matched:
            self.status.set("VALID STAGE RESULT")
            self.details.set(f"Verifier: {VERSION}\nProof receipt: {self.receipt['receipt_id']}")
        else:
            self.status.set("NOT ACCEPTED")
            self.details.set("The submission did not satisfy the frozen verification contract.\nNo additional solution information is disclosed.\n" + f"Proof receipt: {self.receipt['receipt_id']}")

    def copy_receipt(self) -> None:
        if self.receipt is None:
            messagebox.showinfo("No receipt", "Verify a submission first.", parent=self.root)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(json.dumps(self.receipt, ensure_ascii=False, indent=2))
        self.details.set(f"Copied receipt {self.receipt['receipt_id']} to the clipboard.")

    def save_receipt(self) -> None:
        if self.receipt is None:
            messagebox.showinfo("No receipt", "Verify a submission first.", parent=self.root)
            return
        selected = filedialog.asksaveasfilename(parent=self.root, title="Save verification receipt", defaultextension=".json", filetypes=(("JSON", "*.json"),))
        if not selected:
            return
        try:
            Path(selected).write_text(json.dumps(self.receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        except OSError as error:
            messagebox.showerror("Unable to save", str(error), parent=self.root)
            return
        self.details.set(f"Saved receipt {self.receipt['receipt_id']}.")

    def show_instructions(self) -> None:
        self.show_text_window("How to solve Expedition 001", instructions_text())

    def show_hint(self) -> None:
        self.hint_level = min(self.hint_level + 1, len(HINTS))
        self.show_text_window(f"Expedition 001 — Hint {self.hint_level}", hint_text(self.hint_level))

    def show_text_window(self, title: str, content: str) -> None:
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("720x620")
        window.minsize(560, 420)
        body = tk.Text(window, wrap="word", padx=18, pady=18, font=("Segoe UI", 10))
        body.insert("1.0", content)
        body.configure(state="disabled")
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=body.yview)
        body.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        body.pack(fill="both", expand=True)


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return 0 if packaged_self_test(VERSION) else 1
    if sys.argv[1:] == ["--version"]:
        print(f"HMS Expedition Verifier {VERSION}")
        return 0
    root = tk.Tk()
    VerifierApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
