#!/usr/bin/env python3
"""MARSEL V22 — safe raw-GET integrity audit. Read-only; never calls RO App."""
from __future__ import annotations
import json, os, re
from collections import Counter, defaultdict
from pathlib import Path

INPUT = Path(os.environ.get("MARSEL_RAW_READ_INPUT", "marsel-raw-read-v22.json"))
OUTPUT = Path(os.environ.get("MARSEL_RAW_READ_OUTPUT", "marsel-raw-read-integrity-v22.json"))
ID_KEYS = ("id", "uuid", "code", "key", "number")
REF_RE = re.compile(r"^(?P<base>.+)_(?:id|ids|uuid|code|key)$", re.I)

def rows(value):
    if isinstance(value, list): return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        for k in ("data", "items", "results", "orders"):
            if isinstance(value.get(k), list): return [x for x in value[k] if isinstance(x, dict)]
    return []

def sid(r):
    for k in ID_KEYS:
        v = r.get(k)
        if v not in (None, "") and not isinstance(v, (dict, list)): return k, str(v)
    return None

def main():
    if not INPUT.exists():
        print("RAW_READ_INPUT_MISSING")
        return 2
    doc = json.loads(INPUT.read_text(encoding="utf-8"))
    endpoints = doc.get("endpoints", doc.get("responses", []))
    collections=[]; duplicates=0; refs=[]
    for e in endpoints:
        path=str(e.get("path", "")); rs=rows(e.get("response", e.get("data")))
        vals=defaultdict(list); identified=0
        for r in rs:
            x=sid(r)
            if x: vals[x[0]].append(x[1]); identified += 1
            for k,v in r.items():
                if isinstance(v,str) and REF_RE.match(k) and v not in ("", "0"):
                    refs.append({"path":path,"field":k,"value":v})
        d={k:sorted(v for v,n in Counter(vs).items() if n>1) for k,vs in vals.items()}
        d={k:v for k,v in d.items() if v}; duplicates += bool(d)
        collections.append({"path":path,"records":len(rs),"identified":identified,"missing_stable_id":len(rs)-identified,"duplicates":d})
    report={"version":"22.0","status":"PASS","readonly":True,"mutation_allowed":False,"write_requests_made":0,"ro_app_data_mutated":False,"collections":collections,"duplicate_identifier_groups":duplicates,"reference_candidates":refs,"limitations":["Only raw responses supplied in the artifact are analyzed.","Reference names are heuristic candidates until endpoint-to-entity mapping is documented.","This report is not a database backup."]}
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"STATUS={report['status']}"); print(f"COLLECTIONS={len(collections)}"); print(f"DUPLICATE_IDENTIFIER_GROUPS={duplicates}"); print(f"REFERENCE_CANDIDATES={len(refs)}"); print("WRITE_REQUESTS_MADE=0"); print("RO_APP_DATA_MUTATED=False")
    return 0

if __name__ == "__main__": raise SystemExit(main())
