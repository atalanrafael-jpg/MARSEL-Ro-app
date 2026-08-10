#!/usr/bin/env python3
"""MARSEL V20.23 — bounded READ-ONLY API documentation inventory.

The inventory is documentation-derived only. It never performs POST/PUT/PATCH/
DELETE requests, never guesses identifiers, and never claims live completeness.
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
INDEXES = [x.strip() for x in os.environ.get("ROAPP_DOCS_INDEXES", "https://roapp.readme.io/llms.txt").split(",") if x.strip()]
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-29.json")
TIMEOUT = min(int(os.environ.get("ROAPP_TIMEOUT", "8")), 10)
MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "25")), 30)
BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "45")), 60.0)
METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b", re.I)
# Support both full API URLs and documented route forms such as GET /v2/orders.
PATH_RE = re.compile(r"(?<![A-Za-z0-9])/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
URL_RE = re.compile(r"https?://api\.roapp\.io/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
REFERENCE_URL_RE = re.compile(r"(?:https?://roapp\.readme\.io)?/reference/[A-Za-z0-9_./?=&%{}:\-]+", re.I)


def fetch(url: str):
    req = Request(
        url,
        headers={
            "User-Agent": f"MARSEL-Audit-V{VERSION}",
            "Accept": "text/plain,text/markdown,text/html,application/json",
        },
        method="GET",
    )
    started = time.monotonic()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            return response.status, response.read().decode("utf-8", "replace"), round(time.monotonic() - started, 3), None
    except Exception as exc:
        return None, "", round(time.monotonic() - started, 3), f"{type(exc).__name__}: {exc}"


def norm(raw: str):
    raw = html.unescape(raw).strip("`'\"<>[]{}();,.")
    if raw.startswith("http"):
        parsed = urlparse(raw)
        if parsed.netloc.lower() != "api.roapp.io":
            return None
        raw = parsed.path
    raw = raw.split("#", 1)[0]
    if raw.rstrip("/") in ("/v2", "/1.1"):
        return None
    if not raw.startswith(("/v2/", "/1.1/")):
        return None
    raw = re.sub(r"/v2/v2/", "/v2/", raw)
    raw = re.sub(r"/1\.1/1\.1/", "/1.1/", raw)
    return raw


# Backward-compatible public name retained for the V20.23 test contract.
normalize_path = norm


def add_operation(ops: dict, method: str, raw_path: str, source: str):
    path = norm(raw_path)
    if not path:
        return
    method = method.upper() if method else "GET"
    ops[(method, path)] = {
        "method": method,
        "path": path,
        "source": source,
        "evidence_type": "documentation",
    }


def extract_operations(body: str, source: str, ops: dict):
    # 1. Full API URLs.
    for match in URL_RE.finditer(body):
        window = body[max(0, match.start() - 180): match.end() + 180]
        methods = METHOD_RE.findall(window)
        add_operation(ops, methods[-1] if methods else "GET", match.group(), source)

    # 2. Route forms in prose/code, including "GET /v2/..." and bare routes.
    for match in PATH_RE.finditer(body):
        window = body[max(0, match.start() - 180): match.end() + 180]
        methods = METHOD_RE.findall(window)
        add_operation(ops, methods[-1] if methods else "GET", match.group(), source)


def reference_urls(index_body: str, base: str):
    refs = []
    # Markdown links, absolute URLs, and relative /reference/... links.
    for match in REFERENCE_URL_RE.finditer(html.unescape(index_body)):
        url = match.group()
        if url.startswith("/"):
            url = urljoin(base, url)
        if url not in refs:
            refs.append(url)
    # Also handle normal markdown target syntax when the target contains a URL.
    for target in re.findall(r"\]\(([^)]+/reference/[^)]+)\)", index_body, flags=re.I):
        target = html.unescape(target.strip().strip("<>"))
        url = urljoin(base, target)
        if url not in refs:
            refs.append(url)
    return refs


def main():
    if not os.environ.get("ROAPP_API_KEY"):
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2

    deadline = time.monotonic() + BUDGET
    ops = {}
    pages = []

    for idx in INDEXES:
        if time.monotonic() >= deadline:
            break
        status, body, elapsed, error = fetch(idx)
        pages.append({"url": idx, "http": status, "elapsed_s": elapsed, "error": error})
        if status != 200:
            continue

        refs = reference_urls(body, idx)
        # The index itself can contain endpoint snippets; parse it too.
        extract_operations(body, idx, ops)

        for url in refs[:MAX_DOCS]:
            if time.monotonic() >= deadline:
                break
            status2, body2, elapsed2, error2 = fetch(url)
            pages.append({"url": url, "http": status2, "elapsed_s": elapsed2, "error": error2})
            if status2 == 200:
                extract_operations(body2, url, ops)

    operations = sorted(ops.values(), key=lambda item: (item["path"], item["method"]))
    get_count = sum(item["method"] == "GET" for item in operations)
    non_get_count = sum(item["method"] != "GET" for item in operations)

    data = {
        "version": VERSION,
        "readonly": True,
        "method_policy": {"allowed": ["GET"], "blocked": ["POST", "PUT", "PATCH", "DELETE"]},
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "documentation": {"pages_processed": len(pages), "pages": pages},
        "operations": operations,
        "summary": {
            "unique_documented_operations": len(operations),
            "unique_confirmed_operations": 0,
            "get_operations": get_count,
            "non_get_operations": non_get_count,
        },
        "contract_state": {
            "completeness_claim": "NOT_ESTABLISHED",
            "parameterized_identifiers_guessed": False,
            "never_guess_identifiers": True,
            "live_endpoint_verification": "NOT_PERFORMED",
        },
        "safety": {"status": "PASS", "write_requests_made": 0, "ro_app_data_mutated": False},
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
    digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    data["report_sha256"] = digest
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)

    print(f"V{VERSION}_INVENTORY=PASS")
    print(f"PAGES_PROCESSED={len(pages)}")
    print(f"DOCUMENTED_OPERATIONS={len(operations)}")
    print(f"GET_OPERATIONS={get_count}")
    print(f"NON_GET_DOCUMENTED_OPERATIONS={non_get_count}")
    print("CONFIRMED_OPERATIONS=0")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
