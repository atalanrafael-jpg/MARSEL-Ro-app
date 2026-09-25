#!/usr/bin/env python3
"""Export the complete RO App product catalog using GET-only requests."""
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path
import httpx

BASE=os.environ.get("ROAPP_API_BASE","https://api.roapp.io/v2").rstrip("/")
KEY=os.environ.get("ROAPP_API_KEY","")
OUT=Path(os.environ.get("MARSEL_CATALOG_EXPORT_OUTPUT","marsel-roapp-catalog-readonly.json"))
PAGE_SIZE=min(int(os.environ.get("MARSEL_PAGE_SIZE","50")),50)
MAX_PAGES=int(os.environ.get("MARSEL_MAX_PAGES","10000"))
INTERVAL=max(float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL","0.34")),0.34)
TIMEOUT=float(os.environ.get("ROAPP_TIMEOUT","30"))
if not KEY: raise SystemExit("ROAPP_API_KEY is required")
HEADERS={"Authorization":f"Bearer {KEY}","Accept":"application/json","User-Agent":"MARSEL-Catalog-Export-V1-READONLY"}
rows=[]; pages=[]; expected_count=None; total_pages=None; last=0.0
with httpx.Client(timeout=TIMEOUT,follow_redirects=True) as client:
    for page in range(1,MAX_PAGES+1):
        wait=INTERVAL-(time.monotonic()-last)
        if wait>0: time.sleep(wait)
        started=time.monotonic()
        r=client.get(BASE+"/catalog/products",params={"page":page,"pageSize":PAGE_SIZE},headers=HEADERS)
        last=time.monotonic()
        if r.status_code!=200:
            raise SystemExit(f"ROAPP catalog GET failed: HTTP {r.status_code}: {r.text[:500]}")
        payload=r.json()
        batch=payload.get("data",[]) if isinstance(payload,dict) else []
        paging=payload.get("paging",{}) if isinstance(payload,dict) else {}
        if not isinstance(batch,list): raise SystemExit("Unexpected catalog response: data is not a list")
        if total_pages is None:
            total_pages=paging.get("total_pages"); expected_count=paging.get("count")
        rows.extend(x for x in batch if isinstance(x,dict))
        pages.append({"page":page,"http":200,"batch_size":len(batch),"paging":paging,"elapsed_s":round(time.monotonic()-started,3)})
        if total_pages is not None and page>=int(total_pages): break
        if total_pages is None and len(batch)<PAGE_SIZE: break
    else: raise SystemExit("Pagination safety limit exceeded")

ids=[x.get("id") for x in rows]
missing=sum(x in (None,"") for x in ids)
seen=set(); dup=set()
for x in ids:
    if x in seen and x not in (None,""): dup.add(str(x))
    seen.add(x)
complete=(total_pages is not None and len(pages)==int(total_pages)) or (total_pages is None and bool(pages) and pages[-1]["batch_size"]<PAGE_SIZE)
report={"system":"MARSEL ROAPP catalog export","status":"PASS" if complete and expected_count in (None,len(rows)) and missing==0 and not dup else "REVIEW_REQUIRED","generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"mode":"READ_ONLY","api_base":BASE,"path":"/catalog/products","method":"GET","write_requests_made":0,"ro_app_data_mutated":False,"expected_count":expected_count,"rows_read":len(rows),"expected_total_pages":total_pages,"pages_read":len(pages),"pagination_complete":complete,"missing_id":missing,"duplicate_id_values":sorted(dup),"pages":pages,"products":rows}
canonical=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":"))
report["sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"RESULT={report['status']}"); print(f"ROWS_READ={len(rows)}"); print(f"PAGES_READ={len(pages)}"); print(f"SHA256={report['sha256']}")
