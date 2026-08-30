#!/usr/bin/env python3
"""Fail-closed guard against accidental use of RO App's deprecated API.

RO App states that the deprecated API version is supported only until
2026-09-01. This guard intentionally checks source/configuration files and
fails on legacy versioned API paths or legacy header authentication markers.
It does not inspect documentation files, evidence, or lockfiles.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "evidence"}
EXCLUDED_SUFFIXES = {".lock", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}
EXCLUDED_DOC_NAMES = {"README.md"}

# These are intentionally narrow. They target executable/configuration source,
# not historical documentation. Expand only when a confirmed legacy marker is
# found in production code.
PATTERNS = [
    (re.compile(r"(?:https?://[^\s'\"]+)?/api/v1(?:[/\"'\s?#]|$)", re.I), "legacy /api/v1 path"),
    (re.compile(r"https?://[^\s'\"]*roapp[^\s'\"]*/v1(?:[/\"'\s?#]|$)", re.I), "legacy RO App /v1 URL"),
    (re.compile(r"\bX-API-Key\b", re.I), "legacy X-API-Key authentication header"),
]

TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".conf", ".env", ".sh", ".bash", ".ps1", ".txt",
}


def should_scan(path: pathlib.Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.name in EXCLUDED_DOC_NAMES:
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    return path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith(".env")


def main() -> int:
    violations: list[tuple[pathlib.Path, int, str, str]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(lines, 1):
            for pattern, label in PATTERNS:
                if pattern.search(line):
                    violations.append((path.relative_to(ROOT), line_no, label, line.strip()))

    if violations:
        print("RO App API v2 guard: FAILED")
        for path, line_no, label, line in violations:
            print(f"- {path}:{line_no}: {label}: {line[:240]}")
        print("Replace legacy API usage with the current RO App Public API v2 contract.")
        return 1

    print("RO App API v2 guard: PASSED")
    print("No legacy /api/v1 paths or X-API-Key authentication markers found in scanned source/config files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
