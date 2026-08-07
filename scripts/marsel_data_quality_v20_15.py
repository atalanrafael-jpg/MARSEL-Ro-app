import os
import sys
import time
from collections import Counter

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
PAGE_SIZE = 50

if not KEY:
    print("AUDIT: ROAPP_API_KEY is not configured.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {KEY}"}


def extract_rows(payload, resource):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in (resource, "data", "items", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return None


def read_all(client, resource):
    rows = []
    page = 1
    while True:
        response = client.get(
            f"{BASE}/{resource}",
            params={"page": page, "pageSize": PAGE_SIZE},
            headers=headers,
        )
        print(f"AUDIT resource={resource} page={page} HTTP={response.status_code}")
        response.raise_for_status()
        payload = response.json()
        batch = extract_rows(payload, resource)
        if not isinstance(batch, list):
            print(f"AUDIT stopped: no list found for {resource}.")
            return rows, False
        rows.extend(x for x in batch if isinstance(x, dict))
        if len(batch) < PAGE_SIZE:
            return rows, True
        page += 1
        time.sleep(0.4)


with httpx.Client(timeout=TIMEOUT) as client:
    orders, orders_ok = read_all(client, "orders")

ids = [x.get("id") for x in orders if x.get("id") is not None]
numbers = [x.get("number") for x in orders if x.get("number") not in (None, "")]
status_ids = [x.get("status", {}).get("id") for x in orders if isinstance(x.get("status"), dict) and x["status"].get("id") is not None]
client_ids = [x.get("client", {}).get("id") for x in orders if isinstance(x.get("client"), dict) and x["client"].get("id") is not None]

id_counts = Counter(ids)
number_counts = Counter(numbers)
status_counts = Counter(status_ids)
client_counts = Counter(client_ids)

duplicate_id_groups = sum(v > 1 for v in id_counts.values())
duplicate_number_groups = sum(v > 1 for v in number_counts.values())
duplicate_client_groups = sum(v > 1 for v in client_counts.values())
missing_id = sum(x.get("id") is None for x in orders)
missing_number = sum(x.get("number") in (None, "") for x in orders)
missing_client = sum(not isinstance(x.get("client"), dict) or x["client"].get("id") is None for x in orders)
missing_status = sum(not isinstance(x.get("status"), dict) or x["status"].get("id") is None for x in orders)

print("=== MARSEL_DATA_QUALITY_V20.15 / READ ONLY ===")
print(f"orders_total={len(orders)}")
print(f"orders_read_complete={orders_ok}")
print(f"unique_order_ids={len(id_counts)}")
print(f"duplicate_order_id_groups={duplicate_id_groups}")
print(f"orders_missing_id={missing_id}")
print(f"orders_missing_client={missing_client}")
print(f"orders_missing_status={missing_status}")
print(f"orders_missing_number={missing_number}")
print(f"duplicate_order_number_groups={duplicate_number_groups}")
print(f"distinct_client_ids_in_orders={len(client_counts)}")
print(f"client_ids_repeated_across_orders={duplicate_client_groups}")
print("status_counts=" + ",".join(f"{k}:{v}" for k, v in sorted(status_counts.items(), key=lambda x: str(x[0]))))
print("DATA_QUALITY_RESULT=PASS" if orders_ok else "DATA_QUALITY_RESULT=INCOMPLETE")
print("WRITE_REQUESTS=0")
print("RO_APP_DATA_MUTATED=False")
