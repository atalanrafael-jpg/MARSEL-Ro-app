#!/usr/bin/env python3
"""MARSEL V21.5 reference-directory Quality Gate.

Read-only static validation of the V21.5 master reference specification.
It does not call RO App and cannot mutate remote data.
"""
from pathlib import Path
import re
import sys

DOC = Path("docs/MARSEL_V21_5_MASTER_REFERENCE_DIRECTORIES.md")
REQUIRED = [
    "Клиенты и контрагенты", "Виды работ и услуг", "Причины обращения",
    "Статусы заказа", "Причины задержки", "Гарантия", "Причины отказа/отмены",
    "Дефекты", "Причины брака", "Каналы обращения", "Каналы продаж",
    "Способы оплаты", "Скидки и основания скидки", "Мастера и компетенции",
    "Синонимы и нормализация", "Источники данных", "История изменения данных",
]
FORBIDDEN_AUTO_WRITE = ["POST", "PUT", "PATCH", "DELETE", "create_customer", "update_customer"]

def main() -> int:
    if not DOC.exists():
        print("ERROR=missing_v21_5_document")
        return 1
    text = DOC.read_text(encoding="utf-8")
    errors = []
    warnings = []
    for name in REQUIRED:
        if name not in text:
            errors.append(f"missing_directory:{name}")
    if "Дефект ≠ причина брака" not in text:
        errors.append("defect_and_failure_cause_not_separated")
    if "автоматическое объединение запрещено" not in text:
        errors.append("synonym_auto_merge_guard_missing")
    if "не является автоматическим импортом" not in text:
        errors.append("import_boundary_missing")
    if "write-операций" not in text:
        warnings.append("write_guard_wording_missing")
    for token in FORBIDDEN_AUTO_WRITE:
        if re.search(rf"\b{re.escape(token)}\b", text, re.I):
            warnings.append(f"forbidden_token_in_spec:{token}")
    print("MARSEL_V21_5_QUALITY_GATE")
    print(f"DOCUMENT={DOC}")
    print(f"ERRORS={len(errors)}")
    for e in errors:
        print(f"ERROR={e}")
    print(f"WARNINGS={len(warnings)}")
    for w in warnings:
        print(f"WARNING={w}")
    print("RO_APP_DATA_MUTATED=False")
    print("WRITE_REQUESTS_MADE=0")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
