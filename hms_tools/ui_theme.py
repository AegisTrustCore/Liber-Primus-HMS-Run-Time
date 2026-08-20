"""Shared Aegis Trust Core / HMS Endeavour desktop visual system."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

NAVY = "#071820"
DEEP = "#0b222d"
SURFACE = "#10313d"
RAISED = "#174553"
BRASS = "#c6a15b"
BRASS_ACTIVE = "#dfbd77"
CYAN = "#52c7d4"
TEXT = "#edf5f6"
MUTED = "#9eb2b8"
SUCCESS = "#62c89b"
DANGER = "#ef7d75"
WARNING = "#e6bd68"


def apply_hms_theme(root: tk.Misc) -> ttk.Style:
    """Apply the dark nautical research-station theme to a Tk application."""
    root.configure(background=NAVY)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=DEEP, foreground=TEXT, fieldbackground=SURFACE, bordercolor=RAISED, lightcolor=RAISED, darkcolor=NAVY, font=("Segoe UI", 10))
    style.configure("TFrame", background=DEEP)
    style.configure("Shell.TFrame", background=NAVY)
    style.configure("Header.TFrame", background=NAVY)
    style.configure("Card.TFrame", background=SURFACE, relief="flat")
    style.configure("TLabel", background=DEEP, foreground=TEXT)
    style.configure("Brand.TLabel", background=NAVY, foreground=BRASS, font=("Segoe UI Semibold", 10))
    style.configure("Title.TLabel", background=NAVY, foreground=TEXT, font=("Segoe UI Semibold", 21))
    style.configure("Subtitle.TLabel", background=NAVY, foreground=MUTED)
    style.configure("Section.TLabel", background=DEEP, foreground=TEXT, font=("Segoe UI Semibold", 17))
    style.configure("Muted.TLabel", background=DEEP, foreground=MUTED)
    style.configure("Authority.TLabel", background=NAVY, foreground=CYAN, font=("Segoe UI Semibold", 9))
    style.configure("Status.TLabel", background=NAVY, foreground=MUTED)
    style.configure("Pass.TLabel", foreground=SUCCESS, font=("Segoe UI Semibold", 12))
    style.configure("Fail.TLabel", foreground=DANGER, font=("Segoe UI Semibold", 12))
    style.configure("TButton", background=RAISED, foreground=TEXT, padding=(11, 7), borderwidth=0)
    style.map("TButton", background=[("active", "#206173"), ("pressed", SURFACE)], foreground=[("disabled", MUTED)])
    style.configure("Primary.TButton", background=BRASS, foreground=NAVY, font=("Segoe UI Semibold", 10))
    style.map("Primary.TButton", background=[("active", BRASS_ACTIVE), ("pressed", "#a98545")])
    style.configure("TEntry", fieldbackground=SURFACE, foreground=TEXT, insertcolor=TEXT, padding=7)
    style.configure("TCombobox", fieldbackground=SURFACE, foreground=TEXT, arrowcolor=BRASS, padding=6)
    style.configure("TCheckbutton", background=DEEP, foreground=TEXT)
    style.configure("TNotebook", background=NAVY, borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background=SURFACE, foreground=MUTED, padding=(13, 9), borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", RAISED), ("active", "#143c49")], foreground=[("selected", TEXT), ("active", TEXT)])
    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=TEXT, rowheight=28, borderwidth=0)
    style.configure("Treeview.Heading", background=RAISED, foreground=TEXT, font=("Segoe UI Semibold", 9), padding=7)
    style.map("Treeview", background=[("selected", "#246477")], foreground=[("selected", TEXT)])
    style.configure("TLabelframe", background=DEEP, foreground=BRASS, bordercolor=RAISED)
    style.configure("TLabelframe.Label", background=DEEP, foreground=BRASS, font=("Segoe UI Semibold", 10))
    style.configure("TProgressbar", background=CYAN, troughcolor=SURFACE, borderwidth=0)
    return style


def build_brand_header(parent: tk.Misc, product: str, subtitle: str, authority: str) -> ttk.Frame:
    """Create the standard HMS masthead and Aegis Trust Core attribution."""
    header = ttk.Frame(parent, style="Header.TFrame", padding=(20, 15, 20, 14))
    left = ttk.Frame(header, style="Header.TFrame")
    left.pack(side="left", fill="x", expand=True)
    ttk.Label(left, text="AEGIS TRUST CORE  //  HMS ENDEAVOUR", style="Brand.TLabel").pack(anchor="w")
    ttk.Label(left, text=product, style="Title.TLabel").pack(anchor="w", pady=(2, 0))
    ttk.Label(left, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))
    ttk.Label(header, text=authority, style="Authority.TLabel").pack(side="right", anchor="n", pady=(8, 0))
    return header


def configure_text(widget: tk.Text, *, monospace: bool = False) -> None:
    widget.configure(background=SURFACE, foreground=TEXT, insertbackground=BRASS, selectbackground="#246477", selectforeground=TEXT, relief="flat", borderwidth=0, font=(("Cascadia Mono", 10) if monospace else ("Segoe UI", 10)))
