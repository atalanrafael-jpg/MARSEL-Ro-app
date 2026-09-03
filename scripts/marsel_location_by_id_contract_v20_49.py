#!/usr/bin/env python3
"""MARSEL V20.49 — RO App Get Location by ID contract discovery.

Safety contract:
- READ_ONLY only.
- Never guesses or hard-codes a location detail endpoint.
- Downloads the exact official ReadMe page supplied by the project contract.
- Extracts candidate HTTP GET paths only from that documentation page.
- A live RO App request is made only when exactly one parameterized GET path is
  explicitly present in the official documentation and the path contains a
  location identifier placeholder.
- The identifier is obtained from a live confirmed locations collection; it is
  never invented.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from html import unescape
from urllib.request import Request, urlopen

BASE = os.getenv("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.getenv("ROAPP_API_KEY", "")
DOC = "https://roapp.readme.io/reference/get-location-by-id"
LOCATIONS_PATH = "/company/locations"
TIMEOUT = min(int(os.getenv("ROAPP_TIMEOUT", "15")), 15)
INTERVAL = max(float(os.getenv("ROAPP_MIN_REQUEST_INTERVAL", "0.34")), 0.34)
OUT = os.getenv("LOCATION_BY_ID_OUTPUT", "marsel-location-by-id-contract-v20-49.json")

PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(/(?:v2/)?[A-Za-z0-9_.\-/{}:<>]+)")
PLACEHOLDER_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")


def fetch_doc() -> tuple[int, str]:
    req = Request(DOC, headers={"Accept": "text/html, text/plain, */*", "User-Agent": "MARSEL-V20.49-READONLY"}, method="GET")
    with urlopen(req, timeout=TIMEOUT) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def clean_doc(body: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", body, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(re.sub(r"\s+", " ", text))


def documented_paths(text: str) -> list[str]:
    found = []
    for raw in PATH_RE.findall(text):
        path = raw.rstrip(".,);]}`\"'")
        if "{" in path or ":" in path or "<" in path:
            if path not in found:
                found.append(path)
    return found


def get(path: str):
    time.sleep(INTERVAL)
    url = f"{BASE}{path if path.startswith('/') else '/' + path}"
    req = Request(url, headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-V20.49-READONLY"}, method="GET")
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"url": url, "http": response.status, "elapsed_s": round(time.time() - started, 3), "body": body, "error": None}
    except Exception as exc:
        body = ""
        status = getattr(exc, "code", None)
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return {"url": url, "http": status, "elapsed_s": round(time.time() - started, 3), "body": body, "error": f"{type(exc).__name__}: {exc}"}


def extract_ids(payload):
    rows = payload if isinstance(payload, list) else payload.get("data", []) if isinstance(payload, dict) else []
    return [x.get("id") for x in rows if isinstance(x, dict) and x.get("id") is not None]


def main() -> int:
    if not KEY:
        raise SystemExit("ROAPP_API_KEY is required")

    doc_status, doc_body = fetch_doc()
    text = clean_doc(doc_body)
    candidates = [p for p in documented_paths(text) if "location" in p.lower() and PLACEHOLDER_RE.search(p)]

    # Fail closed unless documentation exposes exactly one location-detail GET path.
    if doc_status != 200:
        result = "NOT_VERIFIED"
        reason = f"official documentation HTTP status {doc_status}"
        probes = []
    elif len(candidates) != 1:
        result = "NOT_VERIFIED"
        reason = f"official documentation exposed {len(candidates)} candidate location-detail paths; no endpoint selected"
        probes = []
    else:
        template = candidates[0]
        parent = get(LOCATIONS_PATH)
        if parent["http"] != 200:
            result = "NOT_VERIFIED"
            reason = "confirmed locations collection did not return HTTP 200"
            probes = [{"stage": "locations_collection", **{k: parent.get(k) for k in ("url", "http", "elapsed_s", "error")}}]
        else:
            try:
                payload = json.loads(parent["body"])
                ids = extract_ids(payload)
            except Exception as exc:
                ids = []
                reason = f"locations collection returned invalid JSON: {type(exc).__name__}: {exc}"
            if not ids:
                result = "NOT_VERIFIED"
                reason = reason if "reason" in locals() else "locations collection returned no usable real IDs"
                probes = [{"stage": "locations_collection", "url": parent["url"], "http": parent["http"]}]
            else:
                probes = []
                for location_id in ids:
                    path = template.replace("{id}", str(location_id)).replace("{location_id}", str(location_id))
                    probe = get(path)
                    probes.append({"location_id": location_id, "path": path, **{k: probe.get(k) for k in ("url", "http", "elapsed_s", "error")}})
                result = "PASS" if all(p.get("http") == 200 for p in probes) else "NOT_VERIFIED"
                reason = "all real location IDs returned HTTP 200" if result == "PASS" else "one or more documented location detail GETs did not return HTTP 200"

    report = {
        "version": "20.49",
        "mode": "READ_ONLY",
        "readonly": True,
        "result": result,
        "official_documentation": DOC,
        "documentation_http": doc_status,
        "documented_candidate_paths": candidates,
        "selected_path": candidates[0] if len(candidates) == 1 else None,
        "reason": reason,
        "probes": probes,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    raw = json.dumps(report, ensure_ascii=False, indent=2).encode()
    report["report_sha256"] = hashlib.sha256(raw).hexdigest()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"LOCATION_BY_ID_RESULT={result}")
    print(f"DOCUMENTATION_HTTP={doc_status}")
    print(f"DOCUMENTED_CANDIDATE_PATHS={len(candidates)}")
    print(f"SELECTED_PATH={candidates[0] if len(candidates) == 1 else 'NONE'}")
    print(f"WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
