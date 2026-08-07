#!/usr/bin/env python3
"""MARSEL V20.14 — official RO App API inventory, READ ONLY."""
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
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-14.json")
TIMEOUT = int(os.environ.get("ROAPP_TIMEOUT", "30"))
MAX_DOCS = int(os.environ.get("MARSEL_MAX_DOCS", "300"))
MAX_RETRIES = int(os.environ.get("ROAPP_MAX_RETRIES", "3"))
RETRY_BASE = float(os.environ.get("ROAPP_RETRY_BASE_SECONDS", "0.75"))
MIN_INTERVAL = float(os.environ.get("ROAPP_MIN_REQUEST_INTERVAL", "0.25"))

METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b", re.I)
METHOD_PATH_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?(https?://[^\s)\]}>\'\"`]+|/[A-Za-z0-9_./{}:-]+)", re.I)
FULL_API_URL_RE = re.compile(r"https?://api\.roapp\.io/v2(?:/[A-Za-z0-9_./{}:-]+)?", re.I)
PATH_TOKEN_RE = re.compile(r"(?:https?://[^\s)\]}>\'\"`]+|/[A-Za-z0-9_./{}:-]+)")
TITLE_METHODS = {"get": "GET", "create": "POST", "add": "POST", "update": "PUT", "delete": "DELETE", "merge": "POST", "change": "PATCH"}

_last_request_at = 0.0


def fetch(url, headers=None):
    global _last_request_at
    req_headers = headers or {"User-Agent": "MARSEL-Audit-V20.14", "Accept": "text/plain, text/markdown, text/html, application/json"}
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


def clean_url(url): return url.rstrip(".,;:")


def title_method(title):
    first = title.strip().split(None, 1)[0].casefold() if title.strip() else ""
    return TITLE_METHODS.get(first)


def normalize_documented_path(raw):
    raw = clean_url(html.unescape(raw).strip().replace("\\/", "/"))
    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        if parsed.netloc.lower() != "api.roapp.io" or not parsed.path.startswith("/v2"):
            return None
        return parsed.path
    if raw.startswith("/v2/"): return raw
    if raw.startswith("/"): return raw
    return None


def extract_explicit_method_paths(text):
    normalized = html.unescape(text).replace("\\/", "/")
    found = []
    for match in METHOD_PATH_RE.finditer(normalized):
        path = normalize_documented_path(match.group(2))
        if path: found.append((match.group(1).upper(), path))
    for url_match in FULL_API_URL_RE.finditer(normalized):
        path = normalize_documented_path(url_match.group(0))
        if not path: continue
        window_start = max(0, url_match.start() - 1500)
        window_end = min(len(normalized), url_match.end() + 300)
        window = normalized[window_start:window_end]
        nearest = min(((abs((window_start + m.start()) - url_match.start()), m.group(1).upper()) for m in METHOD_RE.finditer(window)), default=None)
        if nearest: found.append((nearest[1], path))
    lines = normalized.splitlines()
    for index, line in enumerate(lines):
        methods = METHOD_RE.findall(line)
        if not methods: continue
        same_line_paths = [normalize_documented_path(token) for token in PATH_TOKEN_RE.findall(line)]
        same_line_paths = [path for path in same_line_paths if path]
        if same_line_paths:
            for method in methods:
                for path in same_line_paths: found.append((method.upper(), path))
            continue
        if len(methods) != 1: continue
        for next_line in lines[index + 1:index + 11]:
            candidate = normalize_documented_path(re.sub(r"[`<>\"']", "", next_line).strip())
            if candidate:
                found.append((methods[0].upper(), candidate))
                break
    return list(dict.fromkeys(found))


def extract_methods(text): return sorted({m.group(1).upper() for m in METHOD_RE.finditer(text)})


def canonical_path(path):
    path = re.sub(r"\s+", "", path).replace("/v2/v2/", "/v2/")
    return path[len("/v2"):] if path.startswith("/v2/") else path


def has_placeholder(path): return bool(re.search(r"\{[^}]+\}|<[^>]+>|:[A-Za-z_][A-Za-z0-9_]*", path))


def sha256_json(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2
    if not 0 <= MIN_INTERVAL <= 10:
        print("ROAPP_MIN_REQUEST_INTERVAL must be between 0 and 10 seconds", file=sys.stderr)
        return 2
    status, index_text, elapsed, error = fetch(DOCS_INDEX)
    if status != 200:
        print(f"DOCS_INDEX_HTTP={status}", file=sys.stderr); print(error or "documentation index unavailable", file=sys.stderr); return 1

    links, seen_urls = [], set()
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+/reference/[^)]+)\)", index_text):
        title, href = match.groups(); url = urljoin(DOCS_INDEX, clean_url(href))
        if url not in seen_urls:
            seen_urls.add(url); links.append({"title": html.unescape(title).strip(), "url": url})
    links = links[:MAX_DOCS]

    operations = []
    for link in links:
        st, text, doc_elapsed, doc_error = fetch(link["url"])
        pairs = extract_explicit_method_paths(text) if st == 200 else []
        methods = sorted({method for method, _ in pairs})
        paths = sorted({canonical_path(path) for _, path in pairs if canonical_path(path)})
        if st == 200 and not methods: methods = extract_methods(text)
        inferred = title_method(link["title"])
        method_source = "document_body"
        if not methods and inferred:
            methods = [inferred]; method_source = "operation_title"
        elif not methods:
            method_source = "unresolved"
        operations.append({"title": link["title"], "documentation_url": link["url"], "documentation_http": st, "documentation_elapsed_s": doc_elapsed, "documentation_error": doc_error, "methods": methods, "method_source": method_source, "paths": paths, "get_probe": None})

    probe_cache, headers = {}, {"Authorization": f"Bearer {KEY}", "Accept": "application/json", "User-Agent": "MARSEL-Audit-V20.14"}
    for op in operations:
        if "GET" not in op["methods"]: continue
        concrete = [p for p in op["paths"] if not has_placeholder(p)]
        if not concrete:
            op["get_probe"] = {"status": "NOT_PROBED", "reason": "no concrete GET path extracted"}; continue
        probes = []
        for path in concrete:
            if path not in probe_cache:
                probe_url = BASE + path if path.startswith("/") else BASE + "/" + path
                st, body, probe_elapsed, probe_error = fetch(probe_url, headers=headers)
                probe = {"path": path, "http": st, "elapsed_s": probe_elapsed, "json": None, "error": probe_error}
                if st == 200:
                    try:
                        parsed = json.loads(body); probe["json"] = {"type": type(parsed).__name__, "keys": sorted(parsed.keys())[:50] if isinstance(parsed, dict) else None}
                    except json.JSONDecodeError: probe["error"] = "HTTP 200 but response is not JSON"
                probe_cache[path] = probe
            probes.append(probe)
        op["get_probe"] = {"status": "PROBED", "results": probes}

    def probe_status(op):
        probe = op.get("get_probe")
        return probe.get("status") if isinstance(probe, dict) else None

    documented_get = sum("GET" in op["methods"] for op in operations)
    documented_non_get = sum(any(m != "GET" for m in op["methods"]) for op in operations)
    resolved_path_ops = sum(bool(op["paths"]) for op in operations)
    get_probed = sum(1 for op in operations if "GET" in op["methods"] and probe_status(op) == "PROBED")
    get_not_probed = sum(1 for op in operations if "GET" in op["methods"] and probe_status(op) == "NOT_PROBED")
    get_unresolved = sum(1 for op in operations if "GET" in op["methods"] and probe_status(op) is None)
    operations_without_paths = sum(1 for op in operations if not op["paths"])
    non_get_operations = sum(1 for op in operations if "GET" not in op["methods"])
    probe_http = [probe["http"] for op in operations if probe_status(op) == "PROBED" for probe in op["get_probe"].get("results", [])]

    report = {
        "version": "20.14", "readonly": True, "write_requests_made": 0, "ro_app_data_mutated": False,
        "request_policy": {"allowed_method": "GET", "min_interval_seconds": MIN_INTERVAL, "max_retries": MAX_RETRIES, "retry_base_seconds": RETRY_BASE},
        "method_policy": {"allowed": ["GET"], "forbidden": ["POST", "PUT", "PATCH", "DELETE"]},
        "documentation": {"index": DOCS_INDEX, "index_http": status, "index_elapsed_s": elapsed, "reference_links": len(links), "parse_errors": sum(1 for op in operations if op["documentation_http"] != 200)},
        "operations": operations,
        "summary": {
            "reference_links": len(links), "documented_operations": len(operations), "documented_get_operations": documented_get,
            "documented_non_get_operations": documented_non_get, "non_get_operations": non_get_operations,
            "operations_with_extracted_paths": resolved_path_ops, "operations_without_extracted_paths": operations_without_paths,
            "get_operations_probed": get_probed, "get_operations_not_probed": get_not_probed,
            "get_operations_with_unresolved_probe_state": get_unresolved,
            "get_probe_http_counts": {str(k): probe_http.count(k) for k in sorted(set(probe_http), key=lambda x: (-1 if x is None else x))},
            "write_requests_made": 0, "ro_app_data_mutated": False,
        },
    }
    report["summary"]["inventory_sha256"] = sha256_json(report["operations"])
    with open(OUT, "w", encoding="utf-8") as handle: json.dump(report, handle, ensure_ascii=False, indent=2)

    print("=== MARSEL V20.14 / OFFICIAL API INVENTORY / READ ONLY ===")
    print(f"DOCS_INDEX_HTTP={status}"); print(f"REFERENCE_LINKS={len(links)}"); print(f"DOCUMENTED_OPERATIONS={len(operations)}")
    print(f"DOCUMENTED_GET_OPERATIONS={documented_get}"); print(f"OPERATIONS_WITH_EXTRACTED_PATHS={resolved_path_ops}")
    print(f"OPERATIONS_WITHOUT_EXTRACTED_PATHS={operations_without_paths}"); print(f"GET_OPERATIONS_PROBED={get_probed}")
    print(f"GET_OPERATIONS_NOT_PROBED={get_not_probed}"); print(f"GET_OPERATIONS_WITH_UNRESOLVED_PROBE_STATE={get_unresolved}")
    print(f"NON_GET_OPERATIONS={non_get_operations}"); print(f"MIN_REQUEST_INTERVAL={MIN_INTERVAL}"); print(f"MAX_RETRIES={MAX_RETRIES}")
    print("WRITE_REQUESTS_MADE=0"); print(f"INVENTORY_SHA256={report['summary']['inventory_sha256']}"); print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0


if __name__ == "__main__": raise SystemExit(main())
