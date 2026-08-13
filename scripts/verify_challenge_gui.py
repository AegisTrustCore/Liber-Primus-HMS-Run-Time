#!/usr/bin/env python3
"""Small offline GUI for packaged HMS challenge verification."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.challenge_verifier import verify_answer
from hms_tools.expedition_001 import HINTS, VERSION, hint_text, instructions_text


class VerifierApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("HMS Endeavour — Expedition Verifier")
        root.geometry("600x370")
        root.minsize(560, 350)

        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Expedition 001 — The Evidence Ledger", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Local verifier · no account · no telemetry · no network request").pack(anchor="w", pady=(4, 20))

        ttk.Label(frame, text="Your five-letter answer").pack(anchor="w")
        self.answer = ttk.Entry(frame, font=("Segoe UI", 13))
        self.answer.pack(fill="x", pady=(6, 12))
        self.answer.bind("<Return>", lambda _event: self.verify())

        ttk.Button(frame, text="Verify answer", command=self.verify).pack(anchor="w")
        actions = ttk.Frame(frame)
        actions.pack(anchor="w", pady=(8, 0))
        ttk.Button(actions, text="How to solve", command=self.show_instructions).pack(side="left")
        ttk.Button(actions, text="Show next hint", command=self.show_hint).pack(side="left", padx=(8, 0))
        self.status = tk.StringVar(value="Enter an answer, then select Verify answer.")
        self.status_label = ttk.Label(frame, textvariable=self.status, wraplength=500)
        self.status_label.pack(anchor="w", fill="x", pady=(20, 0))

        ttk.Separator(frame).pack(fill="x", pady=(20, 10))
        ttk.Label(frame, text=f"Verifier version {VERSION} · XPD-0001 · Practice preview · Campaign closed").pack(anchor="w")
        self.hint_level = 0
        self.answer.focus_set()

    def verify(self) -> None:
        result = verify_answer("XPD-0001", self.answer.get())
        self.status.set(result.message)

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


def main() -> None:
    root = tk.Tk()
    VerifierApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
