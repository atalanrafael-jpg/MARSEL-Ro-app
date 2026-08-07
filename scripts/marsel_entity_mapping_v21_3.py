#!/usr/bin/env python3
"""MARSEL V21.3 read-only entity mapping.

Consumes a RO App entity-inventory JSON and normalizes discovered entities into
MARSEL's business taxonomy. This script NEVER sends requests to RO App.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

INPUT = Path(os.getenv("MARSEL_ENTITY_INVENTORY_INPUT", "marsel-entity-inventory-v20-19.json"))
OUTPUT = Path(os.getenv("MARSEL_ENTITY_MAPPING_OUTPUT", "marsel-entity-mapping-v21-3.json"))

RULES = [
    ("FG", "Изделие", ("кольцо", "серьги", "браслет", "цепь", "подвес", "кулон", "колье", "брошь", "крест", "печатк", "часы")),
    ("MAT", "Материал", ("золото", "серебро", "платин", "бриллиант", "рубин", "сапфир", "изумруд", "фианит", "муассанит", "металл", "камень")),
    ("CON", "Расходный материал", ("припой", "флюс", "абразив", "паста", "полиров", "раствор", "химичес", "очист", "упаков", "этикет")),
    ("DET", "Деталь", ("замок", "карабин", "кольцо соедин", "звено", "штифт", "каст", "крапан", "заготов")),
    ("SPR", "Запчасть", ("механизм", "стекло", "батаре", "аккумулятор", "заводн", "кнопк", "крышк", "уплотн", "ремеш", "браслет часов")),
    ("TLS", "Инструмент", ("пинцет", "штангенцирк", "луп", "надфил", "отвертк", "молоток", "инструмент")),
    ("EQP", "Оборудование", ("станок", "установк", "ванн", "компрессор", "печь", "вытяж", "оборудован", "полировальн")),
]


def die(message: str) -> None:
    print(f"ERROR={message}", file=sys.stderr)
    raise SystemExit(1)


def text_of(obj: object) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        values = []
        for key in ("name", "title", "label", "type", "category", "group", "description", "path"):
            value = obj.get(key)
            if isinstance(value, (str, int, float)):
                values.append(str(value))
        return " ".join(values)
    return ""


def classify(obj: object) -> tuple[str, str, str]:
    text = text_of(obj).lower().replace("ё", "е")
    hits = [(code, name) for code, name, words in RULES if any(word in text for word in words)]
    if not hits:
        return "UNMAPPED", "Не классифицировано", "NO_RULE_MATCH"
    if len(hits) > 1:
        return "AMBIGUOUS", "Требует проверки", "MULTIPLE_RULE_MATCHES:" + ",".join(code for code, _ in hits)
    code, name = hits[0]
    return code, name, "RULE_MATCH"


def flatten_results(data: object) -> list[object]:
    if isinstance(data, dict):
        for key in ("results", "entities", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    if isinstance(data, list):
        return data
    return []


def main() -> None:
    if not INPUT.exists():
        die(f"input_missing:{INPUT}")
    try:
        data = json.loads(INPUT.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"invalid_json:{type(exc).__name__}")

    source = flatten_results(data)
    mapped = []
    for index, obj in enumerate(source, 1):
        code, label, reason = classify(obj)
        mapped.append({
            "source_index": index,
            "source": obj,
            "marsel_type_code": code,
            "marsel_type": label,
            "classification": reason,
        })

    normalized_names = []
    for row in mapped:
        name = text_of(row["source"]).strip().lower().replace("ё", "е")
        normalized_names.append(re.sub(r"\s+", " ", name))
    duplicates = Counter(n for n in normalized_names if n)
    duplicate_groups = {name: count for name, count in duplicates.items() if count > 1}

    counts = Counter(row["marsel_type_code"] for row in mapped)
    report = {
        "version": "21.3",
        "mode": "READ_ONLY_MAPPING",
        "source": str(INPUT),
        "source_sha256": sha256(INPUT.read_bytes()).hexdigest(),
        "entities_considered": len(mapped),
        "classification_counts": dict(sorted(counts.items())),
        "duplicate_name_groups": duplicate_groups,
        "review_required": sum(counts[k] for k in ("UNMAPPED", "AMBIGUOUS")),
        "write_requests": 0,
        "ro_app_data_mutated": False,
        "mapping": mapped,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("=== MARSEL V21.3 / ENTITY MAPPING / READ ONLY ===")
    print(f"ENTITIES_CONSIDERED={len(mapped)}")
    print(f"CLASSIFICATION_COUNTS={json.dumps(dict(sorted(counts.items())), ensure_ascii=False, sort_keys=True)}")
    print(f"DUPLICATE_NAME_GROUPS={len(duplicate_groups)}")
    print(f"REVIEW_REQUIRED={report['review_required']}")
    print("WRITE_REQUESTS=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT={OUTPUT}")
    print("RESULT=OK")


if __name__ == "__main__":
    main()
