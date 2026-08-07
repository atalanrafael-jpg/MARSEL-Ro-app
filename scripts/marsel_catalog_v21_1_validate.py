#!/usr/bin/env python3
"""MARSEL V21.1 catalog quality gate.

Read-only validator for docs/MARSEL_MASTER_CATALOG_V21.md.
No RO App/API write operations are performed.
"""
from __future__ import annotations
import re
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "docs" / "MARSEL_MASTER_CATALOG_V21.md"

REQUIRED_HEADINGS = [
    "## 1. Типы изделий", "## 2. Атрибуты изделия", "## 3. Причина обращения",
    "## 4. Ювелирный ремонт", "## 5. Камни и закрепка", "## 6. Обработка поверхности",
    "## 7. Изготовление и индивидуальные заказы", "## 8. Металл клиента",
    "## 9. Часовые услуги", "## 10. Справочник результатов диагностики",
    "## 11. Справочник причин отказа", "## 12. Справочник источника клиента",
    "## 13. Справочник причины скидки", "## 14. Справочник гарантийного обращения",
    "## 15. Формы", "## 16. Документы и шаблоны", "## 17. Структура склада",
    "## 18. Обязательные контрольные правила",
]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not CATALOG.exists():
        print("ERROR|catalog_missing|docs/MARSEL_MASTER_CATALOG_V21.md")
        return 2
    text = CATALOG.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = [x.strip() for x in lines if x.startswith("## ")]
    for h in REQUIRED_HEADINGS:
        if h not in headings:
            errors.append(f"missing_heading|{h}")

    items: list[tuple[int, str]] = []
    for n, line in enumerate(lines, 1):
        if re.match(r"^\s*-\s+", line):
            item = re.sub(r"^\s*-\s+", "", line).strip()
            if not item:
                errors.append(f"empty_item|line={n}")
            else:
                items.append((n, item))

    norm = lambda s: re.sub(r"[^а-яa-z0-9]+", " ", s.lower()).strip()
    seen: dict[str, list[int]] = {}
    for n, item in items:
        seen.setdefault(norm(item), []).append(n)
    for key, nums in sorted(seen.items()):
        if key and len(nums) > 1:
            warnings.append(f"duplicate_item|lines={','.join(map(str, nums))}|{key}")

    # Obvious unfinished/truncated markers are errors.
    for n, line in enumerate(lines, 1):
        if "..." in line or "…" in line:
            errors.append(f"unfinished_text|line={n}|{line.strip()}")

    # Keep financial/technical values factual: flag invented-looking numeric pricing data.
    for n, line in enumerate(lines, 1):
        if re.search(r"(?:₽|руб\.?|RUB)\s*\d|\d\s*(?:₽|руб\.?|RUB)", line, re.I):
            warnings.append(f"unverified_price_value|line={n}")

    # Basic punctuation/whitespace defects, excluding Markdown URLs/code spans.
    for n, line in enumerate(lines, 1):
        plain = re.sub(r"`[^`]*`|https?://\S+", "", line)
        if re.search(r"\s+[,:;!?]", plain):
            errors.append(f"space_before_punctuation|line={n}")
        if re.search(r" {2,}$", plain) and not line.endswith("  "):
            errors.append(f"trailing_spaces|line={n}")

    print(f"CATALOG={CATALOG.relative_to(CATALOG.parents[1])}")
    print(f"HEADINGS={len(headings)} ITEMS={len(items)}")
    print(f"ERRORS={len(errors)} WARNINGS={len(warnings)}")
    for x in errors:
        print("ERROR|" + x)
    for x in warnings:
        print("WARNING|" + x)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
