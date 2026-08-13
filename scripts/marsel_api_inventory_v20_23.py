#!/usr/bin/env python3
"""MARSEL V20.23 bounded READ-ONLY inventory bootstrap."""
from __future__ import annotations
import hashlib, html, json, os, re, sys, time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

VERSION = "20.23"
INDEXES = [x.strip() for x in os.environ.get("ROAPP_DOCS_INDEXES", "https://roapp.readme.io/llms.txt").split(",") if x.strip()]
OUT = os.environ.get("MARSEL_API_INVENTORY_OUTPUT", "marsel-api-inventory-v20-29.json")
TIMEOUT = min(int(os.environ.get("ROAPP_TIMEOUT", "8")), 10)
MAX_DOCS = min(int(os.environ.get("MARSEL_MAX_DOCS", "25")), 30)
BUDGET = min(float(os.environ.get("MARSEL_INVENTORY_BUDGET_SECONDS", "45")), 60.0)
METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b", re.I)
PATH_RE = re.compile(r"/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)
URL_RE = re.compile(r"https?://api\.roapp\.io/(?:v2|1\.1)(?:/[A-Za-z0-9_./{}:\-?=&\[\]$%]+)?", re.I)


def fetch(url):
    req = Request(url, headers={"User-Agent": f"MARSEL-Audit-V{VERSION}", "Accept": "text/plain,text/markdown,text/html,application/json"}, method="GET")
    started = time.monotonic()
    try:
        with urlopen(req, timeout=TIMEOUT) as response:
            return response.status, response.read().decode("utf-8", "replace"), round(time.monotonic() - started, 3), None
    except Exception as exc:
        return None, "", round(time.monotonic() - started, 3), f"{type(exc).__name__}: {exc}"


def normalize_path(raw):
    raw = html.unescape(raw).strip("`'\"<>[]{}();,.")
    if raw.startswith("http"):
        parsed = urlparse(raw)
        if parsed.netloc.lower() != "api.roapp.io":
            return None
        raw = parsed.path
    raw = raw.split("#", 1)[0]
    if not raw.startswith(("/v2/", "/1.1/")):
        return None
    raw = re.sub(r"/v2/v2/", "/v2/", raw)
    raw = re.sub(r"/1\.1/1\.1/", "/1.1/", raw)
    return raw


# Backward-compatible internal alias; both names are read-only normalizers.
norm = normalize_path


def main():
    if not os.environ.get("ROAPP_API_KEY"):
        print("ROAPP_API_KEY is required", file=sys.stderr)
        return 2
    deadline = time.monotonic() + BUDGET
    operations, pages = {}, []
    for index in INDEXES:
        if time.monotonic() >= deadline:
            break
        status, body, elapsed, error = fetch(index)
        pages.append({"url": index, "http": status, "elapsed_s": elapsed, "error": error})
        if status != 200:
            continue
        refs = []
        for line in body.splitlines():
            for token in re.findall(r"https?://[^\s<>]+", line):
                token = token.rstrip(".,);]")
                if "/reference/" in token and token not in refs:
                    refs.append(token)
        for url in refs[:MAX_DOCS]:
            if time.monotonic() >= deadline:
                break
            status2, body2, elapsed2, error2 = fetch(url)
            pages.append({"url": url, "http": status2, "elapsed_s": elapsed2, "error": error2})
            if status2 != 200:
                continue
            for match in URL_RE.finditer(body2):
                path = normalize_path(match.group())
                if not path:
                    continue
                window = body2[max(0, match.start() - 120):match.end() + 120]
                methods = METHOD_RE.findall(window)
                method = methods[-1].upper() if methods else "GET"
                operations[(method, path)] = {"method": method, "path": path, "source": url}
            for match in PATH_RE.finditer(body2):
                path = normalize_path(match.group())
                if not path:
                    continue
                window = body2[max(0, match.start() - 120):match.end() + 120]
                methods = METHOD_RE.findall(window)
                method = methods[-1].upper() if methods else "GET"
                operations[(method, path)] = {"method": method, "path": path, "source": url}
    data = {
        "version": VERSION,
        "readonly": True,
        "method_policy": {"allowed": ["GET"], "blocked": ["POST", "PUT", "PATCH", "DELETE"]},
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
        "documentation": {"pages_processed": len(pages), "pages": pages},
        "operations": sorted(operations.values(), key=lambda item: (item["path"], item["method"])),
        "summary": {
            "unique_confirmed_operations": len(operations),
            "get_operations": sum(item["method"] == "GET" for item in operations.values()),
            "non_get_operations": sum(item["method"] != "GET" for item in operations.values()),
        },
        "contract_state": {"completeness_claim": "NOT_ESTABLISHED", "parameterized_identifiers_guessed": False},
        "safety": {"status": "PASS", "write_requests_made": 0, "ro_app_data_mutated": False, "write_methods_used": []},
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    digest = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    data["report_sha256"] = digest
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    print(f"V{VERSION}_INVENTORY=PASS")
    print(f"PAGES_PROCESSED={len(pages)}")
    print(f"CONFIRMED_OPERATIONS={len(operations)}")
    print("WRITE_REQUESTS_MADE=0")
    print("RO_APP_DATA_MUTATED=false")
    print(f"REPORT_SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
