#!/usr/bin/env python3
"""MARSEL V20.22 — RO App API inventory, strictly READ ONLY.

This parser keeps documentation pages and machine-readable OpenAPI operations
separate. It never invents endpoint paths: paths are accepted only when they
are extracted from the documentation page or an OpenAPI document discovered
from the documentation index.
"""
import hashlib
import html
import json
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

DOCS_INDEX = os.environ.get("ROAPP_DOCS_INDEX", "https://roapp.readme.io/llms.txt")
BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-22.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
MAX_DOCS = int(os.environ.get("MARSEL_MAX_DOCS", "300"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.34"))
MAX_RETRIES = int(os.environ.get("ROAPP_MAX_RETRIES", "3"))
RETRY_BASE = float(os.environ.get("ROAPP_RETRY_BASE_SECONDS", "0.75"))

METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b", re.I)
METHOD_PATH_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://api\.roapp\.io(?:/[A-Za-z0-9_./{}:\-?=&\[\]]*)?|/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]]*)?)", re.I)
FULL_API_URL_RE = re.compile(r"https?://api\.roapp\.io(?:/[A-Za-z0-9_./{}:\-?=&\[\]]*)?", re.I)
PATH_RE = re.compile(r"/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]]*)?", re.I)
HREF_RE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.I)
OPENAPI_URL_RE = re.compile(r"https?://[^\s<>\"']+\.(?:json|ya?ml)(?:\?[^\s<>\"']*)?", re.I)
BASE_ONLY = {"/v2", "/1.1", "/v2/", "/1.1/"}
_last_request_at = 0.0


def fetch(url, headers=None):
    global _last_request_at
    req_headers = headers or {
        "User-Agent": "MARSEL-Audit-V20.22",
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
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else RETRY_BASE * (2 ** attempt)
                except ValueError:
                    delay = RETRY_BASE * (2 ** attempt)
                time.sleep(min(max(delay, 0.0), 30.0))
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt >= MAX_RETRIES:
                return None, "", round(time.time() - started, 3), last_error
            time.sleep(min(RETRY_BASE * (2 ** attempt), 30.0))
    return None, "", 0, last_error or "request failed"


def normalize_path(raw):
    raw = html.unescape(str(raw)).strip().replace("\\/", "/").rstrip(".,;:")
    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        if parsed.netloc.lower() != "api.roapp.io":
            return None
        raw = parsed.path
    if raw.startswith(("/v2/", "/1.1/")) and raw not in BASE_ONLY:
        return raw.replace("/v2/v2/", "/v2/").replace("/1.1/1.1/", "/1.1/")
    return None


def extract_explicit_method_paths(text):
    normalized = html.unescape(text).replace("\\/", "/")
    found = []
    for m in METHOD_PATH_RE.finditer(normalized):
        p = normalize_path(m.group(2))
        if p:
            found.append((m.group(1).upper(), p, "documentation_body"))
    for m in FULL_API_URL_RE.finditer(normalized):
        p = normalize_path(m.group(0))
        if not p:
            continue
        window = normalized[max(0, m.start() - 1200):m.end() + 300]
        methods = list(METHOD_RE.finditer(window))
        found.append(((methods[-1].group(1).upper() if methods else "GET"), p, "documentation_body"))
    for m in HREF_RE.finditer(normalized):
        p = normalize_path(m.group(1))
        if not p:
            continue
        window = normalized[max(0, m.start() - 1200):m.end() + 300]
        methods = list(METHOD_RE.finditer(window))
        found.append(((methods[-1].group(1).upper() if methods else "GET"), p, "documentation_body"))
    for m in PATH_RE.finditer(normalized):
        p = normalize_path(m.group(0))
        if not p:
            continue
        window = normalized[max(0, m.start() - 1000):m.end() + 250]
        methods = list(METHOD_RE.finditer(window))
        found.append(((methods[-1].group(1).upper() if methods else "GET"), p, "documentation_body"))
    return list(dict.fromkeys(found))


def extract_openapi_candidates(text):
    candidates = []
    for raw in OPENAPI_URL_RE.findall(text):
        url = html.unescape(raw).rstrip(".,);\]")
        if url not in candidates:
            candidates.append(url)
    return candidates


def parse_openapi(text):
    try:
        spec = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(spec, dict) or not isinstance(spec.get("paths"), dict):
        return []
    result = []
    for path, methods in spec["paths"].items():
        if not isinstance(methods, dict):
            continue
        normalized = normalize_path(path)
        if not normalized:
            if str(path).startswith("/"):
                normalized = str(path)
                if not normalized.startswith(("/v2/", "/1.1/")):
                    normalized = "/v2" + normalized
            else:
                continue
        for method in methods:
            m = str(method).upper()
            if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                result.append((m, normalized, "openapi"))
    return list(dict.fromkeys(result))


def sha256_json(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def page_variants(url):
    return list(dict.fromkeys([url] + ([url[:-3]] if url.endswith(".md") else [])))


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2
    if not 0 <= MIN_INTERVAL <= 10:
        print("ROAPP_MIN_REQUEST_INTERVAL must be between 0 and 10 seconds", file=sys.stderr)
        return 2

    status, index_text, _, error = fetch(DOCS_INDEX)
    if status != 200:
        print(f"DOCS_INDEX_HTTP={status}", file=sys.stderr)
        print(error or "documentation index unavailable", file=sys.stderr)
        return 1

    links, seen = [], set()
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+/reference/[^)]+)\)", index_text):
        title, href = m.groups()
        url = urljoin(DOCS_INDEX, href.rstrip(".,;"))
        if url not in seen:
            seen.add(url)
            links.append({"title": html.unescape(title).strip(), "url": url})
    links = links[:MAX_DOCS]

    operations = []
    openapi_candidates = extract_openapi_candidates(index_text)
    openapi_documents = []
    for spec_url in openapi_candidates:
        st, body, elapsed, err = fetch(spec_url)
        extracted = parse_openapi(body) if st == 200 else []
        openapi_documents.append({"url": spec_url, "http": st, "elapsed_s": elapsed, "error": err, "operations": len(extracted)})
        for method, path, source in extracted:
            operations.append({"title": f"OpenAPI {method} {path}", "documentation_url": spec_url, "methods": [method], "method_source": source, "paths": [path], "get_probe": None})

    for link in links:
        bodies, sources = [], []
        doc_status = None
        doc_error = None
        for variant in page_variants(link["url"]):
            st, text, elapsed, err = fetch(variant)
            sources.append({"url": variant, "http": st, "elapsed_s": elapsed, "error": err})
            if st == 200:
                bodies.append(text)
                doc_status = 200
            elif doc_status is None:
                doc_status, doc_error = st, err
        combined = "\n".join(bodies)
        pairs = extract_explicit_method_paths(combined) if bodies else []
        methods = sorted({m for m, _, _ in pairs})
        paths = sorted({p for _, p, _ in pairs})
        operations.append({
            "title": link["title"],
            "documentation_url": link["url"],
            "documentation_variants": sources,
            "documentation_http": doc_status,
            "documentation_error": doc_error,
            "methods": methods,
            "method_source": "document_body" if methods else "unresolved",
            "paths": paths,
            "get_probe": None,
        })

    dedup = {}
    for op in operations:
        key = (op.get("documentation_url"), tuple(op.get("methods", [])), tuple(op.get("paths", [])))
        dedup[key] = op
    operations = list(dedup.values())

    probe_cache = {}
    headers = {"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-Audit-V20.22"}
    for op in operations:
        if "GET" not in op.get("methods", []):
            continue
        concrete = [p for p in op.get("paths", []) if not re.search(r"\{[^}]+\}|:[A-Za-z_][A-Za-z0-9_]*|<[^>]+>", p)]
        if not concrete:
            op["get_probe"] = {"status": "NOT_PROBED", "reason": "no concrete GET path extracted"}
            continue
        probes = []
        for path in concrete:
            if path not in probe_cache:
                url = BASE + path if path.startswith("/") else BASE + "/" + path
                st, body, elapsed, err = fetch(url, headers=headers)
                item = {"path": path, "url": url, "http": st, "elapsed_s": elapsed, "error": err, "json": None}
                if st == 200:
                    try:
                        parsed = json.loads(body)
                        item["json"] = {"type": type(parsed).__name__, "keys": sorted(parsed.keys())[:50] if isinstance(parsed, dict) else None}
                    except json.JSONDecodeError:
                        item["error"] = "HTTP 200 but response is not JSON"
                probe_cache[path] = item
            probes.append(probe_cache[path])
        op["get_probe"] = {"status": "PROBED", "results": probes}

    get_ops = [o for o in operations if "GET" in o.get("methods", [])]
    non_get_ops = [o for o in operations if any(m != "GET" for m in o.get("methods", []))]
    extracted_paths = sum(bool(o.get("paths")) for o in operations)
    probed = sum(1 for o in get_ops if (o.get("get_probe") or {}).get("status") == "PROBED")
    not_probed = sum(1 for o in get_ops if (o.get("get_probe") or {}).get("status") == "NOT_PROBED")
    unresolved = sum(1 for o in get_ops if not o.get("get_probe"))

    report = {
        "version": "20.22",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "method_policy": {"allowed": ["GET"], "forbidden": ["POST", "PUT", "PATCH", "DELETE"]},
        "documentation": {"index": DOCS_INDEX, "index_http": status, "reference_links": len(links)},
        "openapi": {"candidates": len(openapi_candidates), "documents": openapi_documents, "operations_extracted": sum(x["operations"] for x in openapi_documents)},
        "operations": operations,
        "summary": {
            "reference_links": len(links),
            "documented_operations": len(operations),
            "documented_get_operations": len(get_ops),
            "documented_non_get_operations": len(non_get_ops),
            "operations_with_extracted_paths": extracted_paths,
            "operations_without_extracted_paths": len(operations) - extracted_paths,
            "get_operations_probed": probed,
            "get_operations_not_probed": not_probed,
            "get_operations_with_unresolved_probe_state": unresolved,
            "write_requests_made": 0,
            "ro_app_data_mutated": False,
        },
    }
    report["summary"]["inventory_sha256"] = sha256_json(report["operations"])
    report["completeness"] = {
        "status": "COMPLETE" if report["summary"]["operations_without_extracted_paths"] == 0 else "INCOMPLETE",
        "reason": "Some reference pages did not expose machine-readable endpoint paths and no OpenAPI document was available for them." if report["summary"]["operations_without_extracted_paths"] else None,
        "never_guess_identifiers": True,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("=== MARSEL V20.22 / OFFICIAL API INVENTORY / READ ONLY ===")
    for k, v in [("DOCS_INDEX_HTTP", status), ("REFERENCE_LINKS", len(links)), ("DOCUMENTED_OPERATIONS", len(operations)), ("DOCUMENTED_GET_OPERATIONS", len(get_ops)), ("OPERATIONS_WITH_EXTRACTED_PATHS", extracted_paths), ("OPERATIONS_WITHOUT_EXTRACTED_PATHS", len(operations) - extracted_paths), ("GET_OPERATIONS_PROBED", probed), ("GET_OPERATIONS_NOT_PROBED", not_probed), ("GET_OPERATIONS_WITH_UNRESOLVED_PROBE_STATE", unresolved)]:
        print(f"{k}={v}")
    print(f"OPENAPI_CANDIDATES={len(openapi_candidates)}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"INVENTORY_SHA256={report['summary']['inventory_sha256']}")
    print(f"COMPLETENESS={report['completeness']['status']}")
    print(f"REPORT={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
