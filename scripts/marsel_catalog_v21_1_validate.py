#!/usr/bin/env python3
"""MARSEL V21.1 catalog quality gate.

Read-only validator for docs/MARSEL_MASTER_CATALOG_V21.md.
No RO App/API write operations are performed.
"""
from __future__ import annotations

import re
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "docs" / "MARSEL_MASTER_CATALOG_V21.md"
TOP_LEVEL_HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")


def normalize(value: str) -> str:
    return re.sub(r"[^а-яa-z0-9]+", " ", value.casefold()).strip()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not CATALOG.exists():
        print("ERROR|catalog_missing|docs/MARSEL_MASTER_CATALOG_V21.md")
        return 2

    text = CATALOG.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Do not hard-code section names: the catalog itself is the source of truth.
    # Require a continuous numeric sequence so a missing/duplicated top-level
    # section is caught without making legitimate new sections fail the gate.
    top_level: list[tuple[int, int, str]] = []
    for line_no, line in enumerate(lines, 1):
        match = TOP_LEVEL_HEADING_RE.match(line)
        if match:
            top_level.append((line_no, int(match.group(1)), match.group(2).strip()))

    if not top_level:
        errors.append("missing_top_level_sections")
    else:
        numbers = [number for _, number, _ in top_level]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            errors.append(
                "invalid_section_numbering|"
                f"actual={','.join(map(str, numbers))}|"
                f"expected={','.join(map(str, expected))}"
            )

    # Parse bullet items by their nearest top-level section. Duplicate names in
    # different sections are valid; duplicates inside the same section are not.
    current_section = "__preamble__"
    section_items: dict[str, list[tuple[int, str]]] = {}
    for line_no, line in enumerate(lines, 1):
        heading = TOP_LEVEL_HEADING_RE.match(line)
        if heading:
            current_section = f"{heading.group(1)}. {heading.group(2).strip()}"
            section_items.setdefault(current_section, [])
            continue
        if re.match(r"^\s*-\s+", line):
            item = re.sub(r"^\s*-\s+", "", line).strip()
            if not item:
                errors.append(f"empty_item|line={line_no}")
                continue
            section_items.setdefault(current_section, []).append((line_no, item))

    for section, items in section_items.items():
        seen: dict[str, list[int]] = {}
        for line_no, item in items:
            key = normalize(item)
            if key:
                seen.setdefault(key, []).append(line_no)
        for key, line_numbers in sorted(seen.items()):
            if len(line_numbers) > 1:
                warnings.append(
                    f"duplicate_item|section={section}|"
                    f"lines={','.join(map(str, line_numbers))}|{key}"
                )

    # Reject only explicit unfinished markers, not normal punctuation such as
    # three dots inside quoted/technical content.
    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped in {"...", "…"} or stripped.endswith("... (truncated)") or stripped.endswith("… (truncated)"):
            errors.append(f"unfinished_text|line={line_no}|{stripped}")

    # Financial values must be based on verified MARSEL data rather than guessed
    # prices. The gate warns instead of failing because prices may be intentional.
    for line_no, line in enumerate(lines, 1):
        if re.search(r"(?:₽|руб\.?|RUB)\s*\d|\d\s*(?:₽|руб\.?|RUB)", line, re.I):
            warnings.append(f"unverified_price_value|line={line_no}")

    # Basic punctuation/whitespace defects, excluding Markdown URLs/code spans.
    for line_no, line in enumerate(lines, 1):
        plain = re.sub(r"`[^`]*`|https?://\S+", "", line)
        if re.search(r"\s+[,:;!?]", plain):
            errors.append(f"space_before_punctuation|line={line_no}")
        if re.search(r" {2,}$", plain) and not line.endswith("  "):
            errors.append(f"trailing_spaces|line={line_no}")

    print(f"CATALOG={CATALOG.relative_to(CATALOG.parents[1])}")
    print(f"TOP_LEVEL_SECTIONS={len(top_level)} ITEMS={sum(len(v) for v in section_items.values())}")
    print(f"ERRORS={len(errors)} WARNINGS={len(warnings)}")
    for error in errors:
        print("ERROR|" + error)
    for warning in warnings:
        print("WARNING|" + warning)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
