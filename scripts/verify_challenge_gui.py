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


class VerifierApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("HMS Endeavour — Expedition Verifier")
        root.geometry("560x300")
        root.minsize(520, 280)

        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Expedition 001 — The Evidence Ledger", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Local verifier · no account · no telemetry · no network request").pack(anchor="w", pady=(4, 20))

        ttk.Label(frame, text="Your five-letter answer").pack(anchor="w")
        self.answer = ttk.Entry(frame, font=("Segoe UI", 13))
        self.answer.pack(fill="x", pady=(6, 12))
        self.answer.bind("<Return>", lambda _event: self.verify())

        ttk.Button(frame, text="Verify answer", command=self.verify).pack(anchor="w")
        self.status = tk.StringVar(value="Enter an answer, then select Verify answer.")
        self.status_label = ttk.Label(frame, textvariable=self.status, wraplength=500)
        self.status_label.pack(anchor="w", fill="x", pady=(20, 0))

        ttk.Separator(frame).pack(fill="x", pady=(20, 10))
        ttk.Label(frame, text="Verifier version 0.1.0 · XPD-0001 · Synthetic training puzzle").pack(anchor="w")
        self.answer.focus_set()

    def verify(self) -> None:
        result = verify_answer("XPD-0001", self.answer.get())
        self.status.set(result.message)


def main() -> None:
    root = tk.Tk()
    VerifierApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
