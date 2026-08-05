#!/usr/bin/env python3
"""MARSEL V20.5 - evidence-based list->detail reference audit.
READ ONLY: GET requests only. Detail IDs are taken only from the corresponding list response.
"""
import json, os, sys, time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_AUDIT_OUTPUT", "marsel-data-discovery-v20-5.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))

# Only endpoints whose list/detail relationship is explicit and safe to test with IDs
# returned by the list endpoint itself. More endpoints can be added after schema proof.
TARGETS = [
    {"entity":"orders", "list":"/orders", "detail":"/orders/{id}"},
    {"entity":"services", "list":"/catalog/services", "detail":"/catalog/services/{id}"},
    {"entity":"products", "list":"/catalog/products", "detail":"/catalog/products/{id}"},
    {"entity":"bundles", "list":"/catalog/bundles", "detail":"/catalog/bundles/{id}"},
    {"entity":"inquiries", "list":"/inquiries", "detail":"/inquiries/{id}"},
    {"entity":"bookings", "list":"/bookings", "detail":"/bookings/{id}"},
    {"entity":"estimates", "list":"/estimates", "detail":"/estimates/{id}"},
    {"entity":"invoices", "list":"/invoices", "detail":"/invoices/{id}"},
]


def get(path, params=None):
    url = BASE + path
    if params:
        from urllib.parse import urlencode
        url += ("&" if "?" in url else "?") + urlencode(params)
    req = Request(url, headers={"Authorization": f"Bearer {KEY}", "Accept":"application/json", "User-Agent":"MARSEL-Audit-V20.5"}, method="GET")
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            return r.status, json.loads(raw.decode("utf-8")), round(time.time()-started, 3), None
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:1000]
        return e.code, None, round(time.time()-started, 3), body
    except (URLError, TimeoutError, ValueError) as e:
        return None, None, round(time.time()-started, 3), str(e)


def extract_records(payload):
    if isinstance(payload, list): return payload
    if not isinstance(payload, dict): return []
    for key in ("data", "items", "results", "orders", "services", "products", "bundles", "inquiries", "bookings", "estimates", "invoices"):
        value = payload.get(key)
        if isinstance(value, list): return value
    for key in ("data", "result"):
        value = payload.get(key)
        if isinstance(value, dict):
            nested = extract_records(value)
            if nested: return nested
    return []


def record_id(item):
    if not isinstance(item, dict): return None
    for k in ("id", "ID", "uuid"):
        if item.get(k) is not None: return item[k]
    return None


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr); return 2
    report = {"version":"20.5", "readonly":True, "write_requests_made":False,
              "ro_app_data_mutated":False, "targets":[], "summary":{}}
    total_list_records = total_detail_checks = 0
    for target in TARGETS:
        entity = target["entity"]
        # V20.5 deliberately audits the list response first; no guessed IDs.
        status, payload, elapsed, error = get(target["list"], {"page":1,"page_size":100})
        entry = {"entity":entity, "list_endpoint":target["list"], "list_http":status,
                 "list_elapsed_s":elapsed, "list_error":error, "records_seen":0,
                 "ids_used_for_detail":0, "detail_endpoint":target["detail"], "detail_checks":[]}
        if status != 200 or payload is None:
            report["targets"].append(entry); continue
        records = extract_records(payload)
        ids = [record_id(x) for x in records]
        ids = [x for x in ids if x is not None]
        entry["records_seen"] = len(records); entry["ids_used_for_detail"] = len(ids)
        total_list_records += len(records)
        # Cap detail checks per entity to avoid excessive load; all IDs are still recorded as source evidence.
        for rid in ids[:100]:
            total_detail_checks += 1
            dpath = target["detail"].format(id=rid)
            ds, dp, de, derr = get(dpath)
            classification = {200:"OK", 401:"AUTH_FAILURE",403:"ACCESS_DENIED",404:"NOT_FOUND",429:"RATE_LIMIT"}.get(ds, "SERVER_ERROR" if ds and ds >= 500 else "UNEXPECTED_HTTP")
            entry["detail_checks"].append({"source_list":target["list"],"source_id":rid,"detail_path":dpath,"http":ds,"classification":classification,"elapsed_s":de,"error":derr})
        report["targets"].append(entry)
    report["summary"] = {"targets":len(TARGETS),"list_records_seen":total_list_records,"detail_checks":total_detail_checks,"write_requests_made":0,"readonly":True}
    with open(OUT,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    print("=== MARSEL AUDIT V20.5 / EVIDENCE-BASED LIST->DETAIL / READ ONLY ===")
    print(f"TARGETS={len(TARGETS)}")
    print(f"LIST_RECORDS_SEEN={total_list_records}")
    print(f"DETAIL_CHECKS={total_detail_checks}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; V20.5; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0

if __name__ == "__main__": sys.exit(main())
