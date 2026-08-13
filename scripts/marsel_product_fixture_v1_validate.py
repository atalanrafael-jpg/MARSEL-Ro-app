#!/usr/bin/env python3
"""Validate the offline MARSEL canonical product fixture against master IDs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "config" / "marsel_master_directories_v1.json"
PRODUCTS = ROOT / "config" / "marsel_product_fixture_v1.json"
REQUIRED = {
    "marsel_id", "sku", "title", "product_type_id", "category_id", "collection_id",
    "status", "metal_ids", "stone_ids", "weight_g", "dimensions", "stock_status",
    "price", "cost", "made_to_order", "description", "created_at", "updated_at",
}


def main() -> int:
    errors: list[str] = []
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    fixture = json.loads(PRODUCTS.read_text(encoding="utf-8"))

    if fixture.get("production_import_allowed") is not False:
        errors.append("production_import_must_be_false")
    dirs = master["directories"]
    ids = {record["id"] for records in dirs.values() for record in records}

    products = fixture.get("products")
    if not isinstance(products, list) or not products:
        errors.append("products_missing")
        products = []

    marsel_ids: set[str] = set()
    skus: set[str] = set()
    for index, product in enumerate(products):
        prefix = f"products[{index}]"
        missing = REQUIRED - product.keys()
        errors.extend(f"missing_key|{prefix}|{key}" for key in sorted(missing))
        marsel_id = product.get("marsel_id")
        sku = product.get("sku")
        if marsel_id in marsel_ids:
            errors.append(f"duplicate_marsel_id|{marsel_id}")
        marsel_ids.add(marsel_id)
        if sku in skus:
            errors.append(f"duplicate_sku|{sku}")
        skus.add(sku)
        for field in ("product_type_id", "category_id"):
            if product.get(field) not in ids:
                errors.append(f"unresolved_reference|{prefix}|{field}|{product.get(field)}")
        for field in ("metal_ids", "stone_ids"):
            for ref_id in product.get(field, []):
                if ref_id not in ids:
                    errors.append(f"unresolved_reference|{prefix}|{field}|{ref_id}")

    print(f"PRODUCTS={len(products)}")
    print(f"ERRORS={len(errors)}")
    for error in errors:
        print("ERROR|" + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
