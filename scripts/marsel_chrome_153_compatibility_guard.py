#!/usr/bin/env python3
"""Fail-closed guard for Chrome 153 web-platform removals/deprecations.

Chrome 153 removed non-standard navigations targeted at ``_current`` and
announced deprecation/removal of several Privacy Sandbox APIs. This guard
checks application source/configuration files so browser compatibility
regressions are detected in CI before deployment.

It intentionally does not reject DOMParser/responseXML/SVG usage: Chrome 153
moved those non-XSLT XML parsing paths to a memory-safe Rust implementation
while preserving web-standard behavior.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUARD_PATH = pathlib.Path(__file__).resolve()
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "evidence"}
EXCLUDED_SUFFIXES = {".lock", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}

TEXT_SUFFIXES = {
    ".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".py", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".env", ".sh", ".bash", ".ps1",
}

REMOVED_PATTERNS = [
    (
        re.compile(
            r"(?:target\s*=\s*['\"]_current['\"]|['\"]_current['\"]\s*[,)]|target\s*[:=]\s*['\"]_current['\"])",
            re.I,
        ),
        "removed _current navigation target",
    ),
]

DEPRECATED_PATTERNS = [
    (re.compile(r"\brequestStorageAccessFor\b", re.I), "deprecated document.requestStorageAccessFor API"),
    (re.compile(r"\bjoinAdInterestGroup\b", re.I), "deprecated Protected Audience API"),
    (re.compile(r"\brunAdAuction\b", re.I), "deprecated Protected Audience API"),
    (re.compile(r"\bsharedStorage\b", re.I), "deprecated Shared Storage API"),
    (re.compile(r"\battributionReporting\b", re.I), "deprecated Attribution Reporting API"),
]


def should_scan(path: pathlib.Path) -> bool:
    if path.resolve() == GUARD_PATH:
        return False
    if any(part in EXCLUDED_DIRS for part in path.parts):
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
            for pattern, label in REMOVED_PATTERNS + DEPRECATED_PATTERNS:
                if pattern.search(line):
                    violations.append((path.relative_to(ROOT), line_no, label, line.strip()))

    if violations:
        print("Chrome 153 compatibility guard: FAILED")
        for path, line_no, label, line in violations:
            print(f"- {path}:{line_no}: {label}: {line[:240]}")
        print("Remove the affected browser API usage or replace it with a supported standard API.")
        return 1

    print("Chrome 153 compatibility guard: PASSED")
    print("No Chrome 153 removed/deprecated browser API usage found in scanned source/config files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
