#!/usr/bin/env python3
"""Reject workstation paths and local endpoints from public repository text."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".toml", ".ini", ".cfg"}
PATTERNS = {
    "Windows absolute path": re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"),
    "macOS user path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "Linux home path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "file URL": re.compile(r"file://", re.IGNORECASE),
    "localhost endpoint": re.compile(r"(?:https?://)?(?:localhost|127\.0\.0\.1)(?::\d+)?", re.IGNORECASE),
}


def candidate_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item.decode("utf-8") for item in completed.stdout.split(b"\0") if item]


def main() -> int:
    findings: list[str] = []
    for path in candidate_files():
        if path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{path.relative_to(ROOT)}:{line_number}: {label}")

    if findings:
        print("FAIL — public-boundary scan found local-only references:")
        print("\n".join(findings))
        return 1
    print("PASS — no workstation paths or local endpoints found in public text candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
