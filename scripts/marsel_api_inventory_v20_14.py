#!/usr/bin/env python3
"""MARSEL V20.14 — official RO App API inventory, READ ONLY."""
import hashlib
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

METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b", re.I)
METHOD_PATH_RE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\b\s*(?:[:\-]\s*)?"
    r"(https?://[^\s)\]}>\'\"`]+|/[A-Za-z0-9_./{}:-]+)",
    re.I,
)
PATH_TOKEN_RE = re.compile(r"(?:https?://[^\s)\]}>\'\"`]+|/[A-Za-z0-9_./{}:-]+)")
BULLET_RE = re.compile(r"^-\s*\[([^\]]+)\]\(([^)]+)\)")

TITLE_METHODS = {
    "get": "GET",
    "create": "POST",
    "add": "POST",
    "update": "PUT",
    "delete": "DELETE",
    "merge": "POST",
    "change": "PATCH",
}


def fetch(url, headers=None):
    req = Request(
        url,
        headers=headers
        or {
            "User-Agent": "MARSEL-Audit-V20.14",
            "Accept": "text/plain, text/markdown, application/json",
        },
        method="GET",
    )
    started = time.time()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            body = response.read()
            return response.status, body.decode("utf-8", errors="replace"), round(time.time() - started, 3), None
    except Exception as exc:
        return None, "", round(time.time() - started, 3), f"{type(exc).__name__}: {exc}"


def clean_url(url):
    return url.rstrip(".,;:")


def title_method(title):
    first = title.strip().split(None, 1)[0].casefold() if title.strip() else ""
    return TITLE_METHODS.get(first)


def normalize_documented_path(raw):
    raw = clean_url(raw)
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        if not parsed.netloc.endswith("roapp.io") or not parsed.path:
            return None
        return parsed.path
    if raw.startswith("/"):
        return raw
    return None


def extract_explicit_method_paths(text):
    """Extract only method/path pairs literally represented in the page."""
    found = []
    for match in METHOD_PATH_RE.finditer(text):
        path = normalize_documented_path(match.group(2))
        if path:
            found.append((match.group(1).upper(), path))

    lines = text.splitlines()
    for index, line in enumerate(lines):
        methods = METHOD_RE.findall(line)
        if not methods:
            continue
        same_line_paths = [
            normalize_documented_path(token)
            for token in PATH_TOKEN_RE.findall(line)
        ]
        same_line_paths = [path for path in same_line_paths if path]
        if same_line_paths:
            for method in methods:
                for path in same_line_paths:
                    found.append((method.upper(), path))
            continue
        if len(methods) != 1:
            continue
        for next_line in lines[index + 1 : index + 3]:
            stripped = re.sub(r"[`<>\"']", "", next_line).strip()
            candidate = normalize_documented_path(stripped)
            if candidate:
                found.append((methods[0].upper(), candidate))
                break

    return list(dict.fromkeys(found))


def extract_methods(text):
    return sorted({m.group(1).upper() for m in METHOD_RE.finditer(text)})


def canonical_path(path):
    path = re.sub(r"\s+", "", path)
    path = path.replace("/v2/v2/", "/v2/")
    if path.startswith("/v2/"):
        return path[len("/v2"):]
    return path


def has_placeholder(path):
    return bool(re.search(r"\{[^}]+\}|<[^>]+>|:[A-Za-z_][A-Za-z0-9_]*", path))


def sha256_json(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def main():
    if not KEY:
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2

    status, index_text, elapsed, error = fetch(DOCS_INDEX)
    if status != 200:
        print(f"DOCS_INDEX_HTTP={status}", file=sys.stderr)
        print(error or "documentation index unavailable", file=sys.stderr)
        return 1

    links = []
    seen_urls = set()
    for line in index_text.splitlines():
        match = BULLET_RE.match(line.strip())
        if not match:
            continue
        title, href = match.groups()
        href = clean_url(href)
        if "/reference/" not in href:
            continue
        url = urljoin(DOCS_INDEX, href)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        links.append({"title": title.strip(), "url": url})

    if len(links) > MAX_DOCS:
        links = links[:MAX_DOCS]

    operations = []
    for link in links:
        st, text, doc_elapsed, doc_error = fetch(link["url"])
        pairs = extract_explicit_method_paths(text) if st == 200 else []
        methods = sorted({method for method, _ in pairs})
        paths = sorted({canonical_path(path) for _, path in pairs if canonical_path(path)})

        if st == 200 and not methods:
            methods = extract_methods(text)

        inferred = title_method(link["title"])
        if not methods and inferred:
            methods = [inferred]
            method_source = "operation_title"
        elif methods:
            method_source = "document_body"
        else:
            method_source = "unresolved"

        operations.append(
            {
                "title": link["title"],
                "documentation_url": link["url"],
                "documentation_http": st,
                "documentation_elapsed_s": doc_elapsed,
                "documentation_error": doc_error,
                "methods": methods,
                "method_source": method_source,
                "paths": paths,
                "get_probe": None,
            }
        )

    probe_cache = {}
    headers = {
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "User-Agent": "MARSEL-Audit-V20.14",
    }
    for op in operations:
        if "GET" not in op["methods"]:
            continue
        concrete = [p for p in op["paths"] if not has_placeholder(p)]
        if not concrete:
            op["get_probe"] = {"status": "NOT_PROBED", "reason": "no concrete GET path extracted"}
            continue
        probes = []
        for path in concrete:
            if path in probe_cache:
                probe = probe_cache[path]
            else:
                probe_url = BASE + path if path.startswith("/") else BASE + "/" + path
                st, body, probe_elapsed, probe_error = fetch(probe_url, headers=headers)
                probe = {
                    "path": path,
                    "http": st,
                    "elapsed_s": probe_elapsed,
                    "json": None,
                    "error": probe_error,
                }
                if st == 200:
                    try:
                        parsed = json.loads(body)
                        probe["json"] = {
                            "type": type(parsed).__name__,
                            "keys": sorted(parsed.keys())[:50] if isinstance(parsed, dict) else None,
                        }
                    except json.JSONDecodeError:
                        probe["error"] = "HTTP 200 but response is not JSON"
                probe_cache[path] = probe
            probes.append(probe)
        op["get_probe"] = {"status": "PROBED", "results": probes}

    def probe_status(op):
        probe = op.get("get_probe")
        return probe.get("status") if isinstance(probe, dict) else None

    documented_get = sum("GET" in op["methods"] for op in operations)
    documented_non_get = sum(any(m != "GET" for m in op["methods"]) for op in operations)
    resolved_path_ops = sum(bool(op["paths"]) for op in operations)
    probed = sum(1 for op in operations if probe_status(op) == "PROBED")
    not_probed = sum(1 for op in operations if probe_status(op) == "NOT_PROBED")
    unresolved_probe_state = sum(1 for op in operations if probe_status(op) is None)
    probe_http = [
        probe["http"]
        for op in operations
        if probe_status(op) == "PROBED"
        for probe in op["get_probe"].get("results", [])
    ]

    report = {
        "version": "20.14",
        "readonly": True,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "method_policy": {"allowed": ["GET"], "forbidden": ["POST", "PUT", "PATCH", "DELETE"]},
        "documentation": {
            "index": DOCS_INDEX,
            "index_http": status,
            "index_elapsed_s": elapsed,
            "reference_links": len(links),
            "parse_errors": sum(1 for op in operations if op["documentation_http"] != 200),
        },
        "operations": operations,
        "summary": {
            "reference_links": len(links),
            "documented_operations": len(operations),
            "documented_get_operations": documented_get,
            "documented_non_get_operations": documented_non_get,
            "operations_with_extracted_paths": resolved_path_ops,
            "get_operations_probed": probed,
            "get_operations_not_probed": not_probed,
            "operations_with_unresolved_probe_state": unresolved_probe_state,
            "get_probe_http_counts": {str(k): probe_http.count(k) for k in sorted(set(probe_http), key=lambda x: (-1 if x is None else x))},
            "write_requests_made": 0,
            "ro_app_data_mutated": False,
        },
    }
    report["summary"]["inventory_sha256"] = sha256_json(report["operations"])

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("=== MARSEL V20.14 / OFFICIAL API INVENTORY / READ ONLY ===")
    print(f"DOCS_INDEX_HTTP={status}")
    print(f"REFERENCE_LINKS={len(links)}")
    print(f"DOCUMENTED_OPERATIONS={len(operations)}")
    print(f"DOCUMENTED_GET_OPERATIONS={documented_get}")
    print(f"OPERATIONS_WITH_EXTRACTED_PATHS={resolved_path_ops}")
    print(f"GET_OPERATIONS_PROBED={probed}")
    print(f"GET_OPERATIONS_NOT_PROBED={not_probed}")
    print(f"OPERATIONS_WITH_UNRESOLVED_PROBE_STATE={unresolved_probe_state}")
    print("WRITE_REQUESTS_MADE=0")
    print(f"INVENTORY_SHA256={report['summary']['inventory_sha256']}")
    print(f"REPORT={OUT}")
    print("RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
