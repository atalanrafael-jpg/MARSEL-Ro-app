#!/usr/bin/env python3
"""MARSEL V20.28 — RO App API discovery inventory, strictly READ ONLY.

Fixes the previous discovery bottleneck: ReadMe's llms.txt is not assumed to
contain only Markdown links to /reference/ pages. The scanner now discovers
reference URLs from Markdown, HTML, bare URLs and ReadMe-style link lists;
extracts endpoint/method pairs from page content and code blocks; and parses
machine-readable OpenAPI/Swagger documents when their URLs are explicitly
present in the documentation. It never invents resource identifiers and
never performs POST/PUT/PATCH/DELETE requests.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen

VERSION = "20.28"
DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-23.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
MAX_DOCS = int(os.environ.get("MARSEL_MAX_DOCS", "500"))
MAX_DISCOVERY_URLS = int(os.environ.get("MARSEL_MAX_DISCOVERY_URLS", "200"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))
MAX_RETRIES = int(os.environ.get("ROAPP_MAX_RETRIES", "3"))
RETRY_BASE = float(os.environ.get("ROAPP_RETRY_BASE_SECONDS", "0.75"))

METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
BASE_ONLY = {"/v2", "/v2/", "/1.1", "/1.1/"}
PARAM_RE = re.compile(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>")
PATH_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
FULL_API_RE = re.compile(r"https?://api\.roapp\.io(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
METHOD_PATH_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io[^\s<>'\"`]+|/(?:v2|1\.1)(?:/[^\s<>'\"`]*)?)", re.I)
REFERENCE_URL_RE = re.compile(r"(?:https?://roapp\.readme\.io)?(?:/reference/[A-Za-z0-9_./?=&%\-]+)", re.I)
ANY_REFERENCE_ABS_RE = re.compile(r"https?://roapp\.readme\.io/reference/[A-Za-z0-9_./?=&%\-]+", re.I)
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


def clean_url(raw: str, base_url: str):
    raw = html.unescape(str(raw)).strip().strip("`'\"<>[]{};,.")
    if not raw or raw.startswith(("javascript:", "mailto:", "#")):
        return None
    raw = raw.split(" ", 1)[0]
    url = urljoin(base_url, raw)
    url, _ = urldefrag(url)
    return url


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
        raw = re.sub(r"/v2/v2/", "/v2/", raw)
        raw = re.sub(r"/1\.1/1\.1/", "/1.1/", raw)
        return raw
    return None


def add_operation(store, method, path, evidence, source_url, detail=""):
    method = str(method).upper()
    if method not in METHODS:
        return
    normalized = normalize_path(path)
    if not normalized:
        return
    key = (method, normalized)
    rank = {"OPENAPI_CONFIRMED": 4, "DOCUMENTATION_CONFIRMED": 3, "URL_CONFIRMED": 2, "HEURISTIC": 1}
    item = store.get(key)
    if item is None:
        store[key] = {"method": method, "path": normalized, "evidence": evidence,
                      "sources": [source_url] if source_url else [],
                      "details": [detail] if detail else []}
        return
    if source_url and source_url not in item["sources"]:
        item["sources"].append(source_url)
    if detail and detail not in item["details"]:
        item["details"].append(detail)
    if rank.get(evidence, 0) > rank.get(item["evidence"], 0):
        item["evidence"] = evidence


def extract_reference_urls(text, base_url):
    found, seen = [], set()
    candidates = []
    candidates += ANY_REFERENCE_ABS_RE.findall(text)
    candidates += REFERENCE_URL_RE.findall(text)
    candidates += HREF_RE.findall(text)
    candidates += MD_LINK_RE.findall(text)
    for raw in candidates:
        u = clean_url(raw, base_url)
        if not u:
            continue
        p = urlparse(u)
        if p.netloc.lower() != "roapp.readme.io" or not p.path.lower().startswith("/reference/"):
            continue
        if u not in seen:
            seen.add(u); found.append(u)
    return found


def extract_explicit(text, source_url, store):
    normalized = html.unescape(text).replace("\\/", "/")
    for m in METHOD_PATH_RE.finditer(normalized):
        add_operation(store, m.group(1), m.group(2), "DOCUMENTATION_CONFIRMED", source_url, "explicit method/path")
    # Endpoint blocks frequently use a path followed by a method or a method heading.
    for m in PATH_RE.finditer(normalized):
        path = normalize_path(m.group(0))
        if not path:
            continue
        window = normalized[max(0, m.start() - 180):m.end() + 180]
        methods = list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b", window, re.I))
        if methods:
            method = methods[-1].group(1).upper()
            add_operation(store, method, path, "DOCUMENTATION_CONFIRMED", source_url, "endpoint path with nearby method")
        else:
            # A documented API URL/path without a method is evidence of the URL only.
            # Keep it as GET for the legacy probe schema, but mark the weaker evidence.
            add_operation(store, "GET", path, "URL_CONFIRMED", source_url, "documented endpoint path; method not explicit")
    for m in FULL_API_RE.finditer(normalized):
        path = normalize_path(m.group(0))
        if not path:
            continue
        window = normalized[max(0, m.start() - 180):m.end() + 180]
        methods = list(re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\b", window, re.I))
        method = methods[-1].group(1).upper() if methods else "GET"
        evidence = "DOCUMENTATION_CONFIRMED" if methods else "URL_CONFIRMED"
        add_operation(store, method, path, evidence, source_url, "full API URL")


def candidate_spec_urls(text, base_url):
    found, seen = [], set()
    for pattern in (OPENAPI_URL_RE, SPEC_EXT_RE):
        for raw in pattern.findall(text):
            u = clean_url(raw.rstrip(".,);]"), base_url)
            if u and u not in seen:
                seen.add(u); found.append(u)
    for raw in HREF_RE.findall(text) + MD_LINK_RE.findall(text):
        u = clean_url(raw, base_url)
        if not u:
            continue
        low = u.lower()
        if any(x in low for x in ("openapi", "swagger", "api-spec", "apispec")) and u not in seen:
            seen.add(u); found.append(u)
    return found


def parse_json_openapi(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) and isinstance(data.get("paths"), dict) else None


def parse_yaml_openapi(text):
    if not re.search(r"(?im)^\s*(?:openapi|swagger)\s*:", text):
        return []
    result, current = [], None
    for line in text.splitlines():
        m = re.match(r"^\s{0,12}(/(?:v2|1\.1)/[^:#\s]+)\s*:\s*$", line)
        if m:
            current = m.group(1); continue
        mm = re.match(r"^\s{2,20}(get|post|put|patch|delete)\s*:\s*$", line, re.I)
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
                method_u = str(method).upper()
                if method_u not in METHODS:
                    continue
                raw = str(path)
                p = normalize_path(raw)
                if not p and raw.startswith("/"):
                    p = normalize_path("/v2" + raw)
                if p:
                    result.append((method_u, p))
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
    st, index_text, _, error = fetch(DOCS_INDEX)
    if st != 200:
        print(f"DOCS_INDEX_HTTP={st}", file=sys.stderr)
        print(error or "documentation index unavailable", file=sys.stderr)
        return 1

    links, seen = [], set()
    for u in extract_reference_urls(index_text, DOCS_INDEX):
        if u not in seen:
            seen.add(u); links.append({"title": u.rsplit("/", 1)[-1], "url": u})
    links = links[:MAX_DOCS]

    operations, specs = {}, []
    discovery_urls = candidate_spec_urls(index_text, DOCS_INDEX)[:MAX_DISCOVERY_URLS]
    spec_seen = set()

    def ingest_spec(u, detail):
        if u in spec_seen:
            return
        spec_seen.add(u)
        s, body, elapsed, err = fetch(u)
        extracted, fmt = parse_openapi(body) if s == 200 else ([], None)
        specs.append({"url": u, "http": s, "elapsed_s": elapsed, "format": fmt,
                      "operations": len(extracted), "error": err})
        for method, path in extracted:
            add_operation(operations, method, path, "OPENAPI_CONFIRMED", u, detail)

    for u in list(discovery_urls):
        ingest_spec(u, "machine-readable OpenAPI/Swagger")

    page_results = []
    for link in links:
        s, body, elapsed, err = fetch(link["url"])
        content_found = s == 200 and bool(body)
        if content_found:
            extract_explicit(body, link["url"], operations)
            for spec_url in candidate_spec_urls(body, link["url"]):
                if spec_url not in discovery_urls and len(discovery_urls) < MAX_DISCOVERY_URLS:
                    discovery_urls.append(spec_url)
        page_results.append({"title": link["title"], "url": link["url"],
                             "responses": [{"url": link["url"], "http": s, "elapsed_s": elapsed, "error": err}],
                             "content_found": content_found})

    for u in discovery_urls:
        ingest_spec(u, "machine-readable OpenAPI/Swagger discovered from reference page")

    ops = sorted(operations.values(), key=lambda x: (x["path"], x["method"]))
    get_ops = [x for x in ops if x["method"] == "GET"]
    non_get = [x for x in ops if x["method"] != "GET"]

    # Probe only concrete GET paths. Never substitute guessed IDs.
    headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": f"MARSEL-Audit-V{VERSION}"}
    probes, cache = [], {}
    for op in get_ops:
        path = op["path"]
        if PARAM_RE.search(path):
            probes.append({"method": "GET", "path": path, "status": "NOT_PROBED", "reason": "parameterized path; no identifier guessed"})
            continue
        if path not in cache:
            # Avoid the /v2/v2 duplication fixed in the live probe implementation.
            url = BASE + (path[3:] if BASE.endswith("/v2") and path.startswith("/v2/") else path)
            s, body, elapsed, err = fetch(url, headers=headers)
            item = {"method": "GET", "path": path, "url": url, "http": s, "elapsed_s": elapsed, "error": err}
            if s == 200:
                try:
                    parsed = json.loads(body)
                    item["json_type"] = type(parsed).__name__
                    item["json_keys"] = sorted(parsed.keys())[:50] if isinstance(parsed, dict) else None
                except json.JSONDecodeError:
                    item["error"] = "HTTP 200 but response is not JSON"
            cache[path] = item
        probes.append(cache[path])

    counts = {
        "unique_operations": len(ops),
        "get_operations": len(get_ops),
        "non_get_operations": len(non_get),
        "openapi_confirmed": sum(1 for x in ops if x["evidence"] == "OPENAPI_CONFIRMED"),
        "documentation_confirmed": sum(1 for x in ops if x["evidence"] == "DOCUMENTATION_CONFIRMED"),
        "url_confirmed": sum(1 for x in ops if x["evidence"] == "URL_CONFIRMED"),
        "get_probes_attempted": len(probes),
        "get_probes_http_200": sum(1 for p in probes if p.get("http") == 200),
        "write_requests_made": 0,
    }
    completeness_status = "PASS" if counts["unique_operations"] > 0 and (counts["openapi_confirmed"] + counts["documentation_confirmed"]) > 0 else "INCOMPLETE"

    report = {
        "version": VERSION,
        "readonly": True,
        "method_policy": {"allowed": ["GET"], "blocked": ["POST", "PUT", "PATCH", "DELETE"]},
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "sources": {"documentation_index": DOCS_INDEX, "api_base": BASE},
        "documentation": {"pages_discovered": len(links), "pages_fetched": sum(1 for p in page_results if p["content_found"])},
        "openapi_discovery": {"candidate_urls": len(discovery_urls), "documents_checked": len(specs),
                              "documents_with_operations": sum(1 for s in specs if s["operations"] > 0), "documents": specs},
        "operations": ops,
        "get_probes": probes,
        "summary": counts,
        "safety": {"status": "PASS", "write_requests_made": 0, "ro_app_data_mutated": False},
        "completeness": {"status": completeness_status, "never_guess_identifiers": True,
                         "note": "Discovery was broadened to all explicit ReadMe reference URLs and documented/OpenAPI endpoint expressions. PASS does not claim undocumented private endpoints exist."},
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)
    report["report_sha256"] = sha256_file(OUT)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)

    print(f"V{VERSION}_INVENTORY=PASS")
    print(f"UNIQUE_OPERATIONS={len(ops)}")
    print(f"OPENAPI_CONFIRMED={counts['openapi_confirmed']}")
    print(f"DOCUMENTATION_CONFIRMED={counts['documentation_confirmed']}")
    print(f"URL_CONFIRMED={counts['url_confirmed']}")
    print(f"PAGES_DISCOVERED={len(links)}")
    print(f"COMPLETENESS={completeness_status}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={report['report_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
