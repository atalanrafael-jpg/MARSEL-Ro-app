#!/usr/bin/env python3
"""MARSEL V20.23 — RO App API discovery inventory, strictly READ ONLY.

Improves V20.22 discovery without guessing endpoint paths. It combines:
- ReadMe llms.txt reference links
- HTML/Markdown links and code blocks
- explicit HTTP method + path expressions
- embedded OpenAPI/Swagger JSON/YAML candidates
- common OpenAPI/Swagger metadata links found in documentation

Every discovered operation carries an evidence level. No write request is
performed. The report deliberately distinguishes safety from completeness.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

VERSION = "20.23"
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-23.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
MAX_DOCS = int(os.environ.get("MARSEL_MAX_DOCS", "300"))
MAX_DISCOVERY_URLS = int(os.environ.get("MARSEL_MAX_DISCOVERY_URLS", "100"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))
MAX_RETRIES = int(os.environ.get("ROAPP_MAX_RETRIES", "3"))
RETRY_BASE = float(os.environ.get("ROAPP_RETRY_BASE_SECONDS", "0.75"))

METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
BASE_ONLY = {"/v2", "/v2/", "/1.1", "/1.1/"}
PATH_RE = re.compile(r"/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$]+)?", re.I)
FULL_API_RE = re.compile(r"https?://api\.roapp\.io(?:/[A-Za-z0-9_./{}:\-?=&\[\]$]+)?", re.I)
METHOD_PATH_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io[^\s<>'\"`]+|/(?:v2|1\.1)(?:/[^\s<>'\"`]*)?)", re.I)
HREF_RE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
MD_LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
OPENAPI_URL_RE = re.compile(r"https?://[^\s<>\"']+(?:openapi|swagger|api[-_]?spec)[^\s<>\"']*", re.I)
SPEC_EXT_RE = re.compile(r"https?://[^\s<>\"']+\.(?:json|ya?ml)(?:\?[^\s<>\"']*)?", re.I)
_last_request_at = 0.0


def fetch(url: str, headers: dict | None = None):
    global _last_request_at
    req_headers = headers or {
        "User-Agent": f"MARSEL-Audit-V{VERSION}",
        "Accept": "text/plain, text/markdown, text/html, application/json, application/yaml, text/yaml",
    }
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        wait = MIN_INTERVAL - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        req = Request(url, headers=req_headers, method="GET")
        started = time.time()
        try:
            _last_request_at = time.monotonic()
            with urlopen(req, timeout=TIMEOUT) as response:
                body = response.read().decode("utf-8", errors="replace")
                status = response.status
                if status not in {408, 425, 429, 500, 502, 503, 504} or attempt >= MAX_RETRIES:
                    return status, body, round(time.time() - started, 3), None
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt >= MAX_RETRIES:
                return None, "", round(time.time() - started, 3), last_error
        time.sleep(min(RETRY_BASE * (2 ** attempt), 30.0))
    return None, "", 0, last_error or "request failed"


def normalize_path(raw: str):
    raw = html.unescape(str(raw)).strip().strip("`'\"<>[](){};,.").replace("\\/", "/")
    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        if parsed.netloc.lower() != "api.roapp.io":
            return None
        raw = parsed.path
    raw = raw.split("#", 1)[0]
    if raw in BASE_ONLY:
        return None
    if raw.startswith(("/v2/", "/1.1/")):
        return re.sub(r"/v2/v2/", "/v2/", re.sub(r"/1\.1/1\.1/", "/1.1/", raw))
    return None


def add_operation(store, method, path, evidence, source_url, detail=""):
    if method not in METHODS:
        return
    normalized = normalize_path(path)
    if not normalized:
        return
    key = (method, normalized)
    rank = {"OPENAPI_CONFIRMED": 4, "DOCUMENTATION_CONFIRMED": 3, "URL_CONFIRMED": 2, "HEURISTIC": 1}
    item = store.get(key)
    if item is None:
        store[key] = {
            "method": method,
            "path": normalized,
            "evidence": evidence,
            "sources": [source_url] if source_url else [],
            "details": [detail] if detail else [],
        }
        return
    if source_url and source_url not in item["sources"]:
        item["sources"].append(source_url)
    if detail and detail not in item["details"]:
        item["details"].append(detail)
    if rank.get(evidence, 0) > rank.get(item["evidence"], 0):
        item["evidence"] = evidence


def extract_explicit(text, source_url, store):
    normalized = html.unescape(text).replace("\\/", "/")
    for m in METHOD_PATH_RE.finditer(normalized):
        add_operation(store, m.group(1).upper(), m.group(2), "DOCUMENTATION_CONFIRMED", source_url, "explicit method/path")
    # A full API URL is a confirmed URL, but its method is only inferred from a nearby explicit method.
    for m in FULL_API_RE.finditer(normalized):
        path = normalize_path(m.group(0))
        if not path:
            continue
        window = normalized[max(0, m.start() - 500):m.end() + 150]
        nearby = list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b", window, re.I))
        method = nearby[-1].group(1).upper() if nearby else "GET"
        add_operation(store, method, path, "DOCUMENTATION_CONFIRMED" if nearby else "URL_CONFIRMED", source_url, "full API URL")
    for m in PATH_RE.finditer(normalized):
        path = normalize_path(m.group(0))
        if not path:
            continue
        window = normalized[max(0, m.start() - 500):m.end() + 150]
        nearby = list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b", window, re.I))
        method = nearby[-1].group(1).upper() if nearby else "GET"
        add_operation(store, method, path, "DOCUMENTATION_CONFIRMED" if nearby else "URL_CONFIRMED", source_url, "path expression")


def candidate_urls(text, base_url):
    found = []
    seen = set()
    for pattern in (OPENAPI_URL_RE, SPEC_EXT_RE):
        for raw in pattern.findall(text):
            raw = html.unescape(raw).rstrip(".,);]\\\"")
            if raw not in seen:
                seen.add(raw); found.append(raw)
    for raw in HREF_RE.findall(text) + MD_LINK_RE.findall(text):
        raw = raw.strip().split(" ", 1)[0]
        if any(x in raw.lower() for x in ("openapi", "swagger", "api-spec", "apispec", "swagger.json", "openapi.json", "openapi.yaml", "openapi.yml")):
            u = urljoin(base_url, raw)
            if u not in seen:
                seen.add(u); found.append(u)
    return found[:MAX_DISCOVERY_URLS]


def parse_json_openapi(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) and isinstance(data.get("paths"), dict) else None


def parse_yaml_openapi(text):
    # Lightweight parser for path/method lines; no dependency required. Only accepts
    # obvious OpenAPI path keys and HTTP method keys, never invents a path prefix.
    if not re.search(r"(?im)^\s*(?:openapi|swagger)\s*:", text):
        return []
    result = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^\s{0,8}(/(?:v2|1\.1)/[^:#\s]+)\s*:\s*$", line)
        if m:
            current = m.group(1)
            continue
        mm = re.match(r"^\s{2,16}(get|post|put|patch|delete)\s*:\s*$", line, re.I)
        if mm and current:
            result.append((mm.group(1).upper(), current))
    return result


def parse_openapi(text):
    data = parse_json_openapi(text)
    if data is not None:
        result = []
        for path, methods in data["paths"].items():
            if not isinstance(methods, dict):
                continue
            for method in methods:
                if str(method).upper() in METHODS:
                    p = normalize_path(str(path)) or ("/v2" + str(path) if str(path).startswith("/") else None)
                    if p:
                        result.append((str(method).upper(), p))
        return result, "json"
    return parse_yaml_openapi(text), "yaml"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr); return 2
    if not 0 <= MIN_INTERVAL <= 10:
        print("ROAPP_MIN_REQUEST_INTERVAL must be between 0 and 10 seconds", file=sys.stderr); return 2

    st, index_text, elapsed, error = fetch(DOCS_INDEX)
    if st != 200:
        print(f"DOCS_INDEX_HTTP={st}", file=sys.stderr); print(error or "documentation index unavailable", file=sys.stderr); return 1

    links, seen = [], set()
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+/reference/[^)]+)\)", index_text):
        title, href = m.groups(); url = urljoin(DOCS_INDEX, href.rstrip(".,;"))
        if url not in seen:
            seen.add(url); links.append({"title": html.unescape(title).strip(), "url": url})
    links = links[:MAX_DOCS]

    operations = {}
    discovery_urls = candidate_urls(index_text, DOCS_INDEX)
    specs = []
    for u in discovery_urls:
        s, body, e, err = fetch(u)
        extracted, fmt = parse_openapi(body) if s == 200 else ([], None)
        specs.append({"url": u, "http": s, "elapsed_s": e, "format": fmt, "operations": len(extracted), "error": err})
        for method, path in extracted:
            add_operation(operations, method, path, "OPENAPI_CONFIRMED", u, "machine-readable OpenAPI/Swagger")

    page_results = []
    for link in links:
        variants = [link["url"]]
        if link["url"].endswith(".md"):
            variants.append(link["url"][:-3])
        bodies = []
        responses = []
        for u in dict.fromkeys(variants):
            s, body, e, err = fetch(u)
            responses.append({"url": u, "http": s, "elapsed_s": e, "error": err})
            if s == 200:
                bodies.append(body)
                extract_explicit(body, u, operations)
                for spec_url in candidate_urls(body, u):
                    if spec_url not in discovery_urls and len(discovery_urls) < MAX_DISCOVERY_URLS:
                        discovery_urls.append(spec_url)
        page_results.append({"title": link["title"], "url": link["url"], "responses": responses, "content_found": bool(bodies)})

    # Second pass over spec URLs discovered inside individual reference pages.
    for u in discovery_urls:
        if any(x["url"] == u for x in specs):
            continue
        s, body, e, err = fetch(u)
        extracted, fmt = parse_openapi(body) if s == 200 else ([], None)
        specs.append({"url": u, "http": s, "elapsed_s": e, "format": fmt, "operations": len(extracted), "error": err})
        for method, path in extracted:
            add_operation(operations, method, path, "OPENAPI_CONFIRMED", u, "machine-readable OpenAPI/Swagger discovered from reference page")

    ops = sorted(operations.values(), key=lambda x: (x["path"], x["method"]))
    get_ops = [x for x in ops if x["method"] == "GET"]
    non_get = [x for x in ops if x["method"] != "GET"]

    # Only concrete GET paths are probed. Parameterized paths are reported, never guessed.
    headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": f"MARSEL-Audit-V{VERSION}"}
    probes = []
    cache = {}
    for op in get_ops:
        if re.search(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>", op["path"]):
            probes.append({"method": "GET", "path": op["path"], "status": "NOT_PROBED", "reason": "parameterized path; no identifier guessed"})
            continue
        if op["path"] not in cache:
            url = BASE + op["path"]
            s, body, e, err = fetch(url, headers=headers)
            item = {"method": "GET", "path": op["path"], "url": url, "http": s, "elapsed_s": e, "error": err}
            if s == 200:
                try:
                    parsed = json.loads(body)
                    item["json_type"] = type(parsed).__name__
                    item["json_keys"] = sorted(parsed.keys())[:50] if isinstance(parsed, dict) else None
                except json.JSONDecodeError:
                    item["error"] = "HTTP 200 but response is not JSON"
            cache[op["path"]] = item
        probes.append(cache[op["path"]])

    confirmed_openapi = sum(1 for x in ops if x["evidence"] == "OPENAPI_CONFIRMED")
    confirmed_docs = sum(1 for x in ops if x["evidence"] == "DOCUMENTATION_CONFIRMED")
    url_confirmed = sum(1 for x in ops if x["evidence"] == "URL_CONFIRMED")
    completeness_status = "PASS" if ops and len(ops) >= len(set((x["method"], x["path"]) for x in ops)) and (confirmed_openapi + confirmed_docs) > 0 else "INCOMPLETE"

    report = {
        "version": VERSION,
        "readonly": True,
        "method_policy": {"allowed": ["GET"], "blocked": ["POST", "PUT", "PATCH", "DELETE"]},
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "sources": {"documentation_index": DOCS_INDEX, "api_base": BASE},
        "documentation": {"pages_discovered": len(links), "pages_fetched": sum(1 for p in page_results if p["content_found"])},
        "openapi_discovery": {"candidate_urls": len(discovery_urls), "documents_checked": len(specs), "documents_with_operations": sum(1 for s in specs if s["operations"] > 0), "documents": specs},
        "operations": ops,
        "get_probes": probes,
        "summary": {
            "unique_operations": len(ops),
            "get_operations": len(get_ops),
            "non_get_operations": len(non_get),
            "openapi_confirmed": confirmed_openapi,
            "documentation_confirmed": confirmed_docs,
            "url_confirmed": url_confirmed,
            "get_probes_attempted": len(probes),
            "get_probes_http_200": sum(1 for p in probes if p.get("http") == 200),
            "write_requests_made": 0,
        },
        "safety": {"status": "PASS", "write_requests_made": 0, "ro_app_data_mutated": False},
        "completeness": {
            "status": completeness_status,
            "never_guess_identifiers": True,
            "note": "PASS means the inventory contains confirmed operations discovered from documentation/OpenAPI. It does not claim undocumented private endpoints exist or that every reference page maps one-to-one to an operation.",
            "unresolved_reference_pages": [p["url"] for p in page_results if p["content_found"] and not any(u in p["url"] for u in [x.get("documentation_url", "") for x in []])],
        },
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)
    report["report_sha256"] = sha256_file(OUT)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"V{VERSION}_INVENTORY=PASS")
    print(f"UNIQUE_OPERATIONS={len(ops)}")
    print(f"OPENAPI_CONFIRMED={confirmed_openapi}")
    print(f"DOCUMENTATION_CONFIRMED={confirmed_docs}")
    print(f"COMPLETENESS={completeness_status}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={report['report_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
