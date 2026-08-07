#!/usr/bin/env python3
"""MARSEL V20.18 — strict READ-ONLY RO App endpoint diagnostics.

Goals:
- probe every concrete GET path from the inventory;
- retain parameterized GET templates instead of silently dropping them;
- resolve placeholders only from an explicit JSON environment mapping;
- never guess identifiers and never use write HTTP methods;
- normalize API base paths so /v2 is not accidentally tested as /v2/v2.
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

BASE = os.environ.get("ROAPP_API_BASE", "https://api.roapp.io/v2").rstrip("/")
KEY = os.environ.get("ROAPP_API_KEY", "")
TIMEOUT = float(os.environ.get("ROAPP_TIMEOUT", "30"))
INVENTORY = Path(os.environ.get("MARSEL_API_INVENTORY_INPUT", "marsel-api-inventory-v20-14.json"))
OUT = Path(os.environ.get("MARSEL_ENDPOINT_DIAGNOSTICS_OUTPUT", "marsel-endpoint-diagnostics-v20-18.json"))
PARAMS_RAW = os.environ.get("ROAPP_PATH_PARAMS_JSON", "{}")

PLACEHOLDER_RE = re.compile(r"\{([^{}]+)\}|:([A-Za-z_][A-Za-z0-9_]*)|<([^<>]+)>")


def fail(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load_params():
    try:
        value = json.loads(PARAMS_RAW)
    except json.JSONDecodeError as exc:
        fail(f"ROAPP_PATH_PARAMS_JSON invalid JSON: {exc}")
    if not isinstance(value, dict):
        fail("ROAPP_PATH_PARAMS_JSON must be a JSON object")
    return {str(k): str(v) for k, v in value.items() if v is not None and str(v) != ""}


def normalize_path(raw):
    raw = str(raw).strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        from urllib.parse import urlparse
        parsed = urlparse(raw)
        if parsed.netloc.lower() != "api.roapp.io":
            return None
        raw = parsed.path
    if raw.startswith("/v2/"):
        raw = raw[3:]
    if not raw.startswith("/"):
        raw = "/" + raw
    return re.sub(r"/{2,}", "/", raw)


def resolve_path(path, params):
    missing = []

    def repl(match):
        name = next(x for x in match.groups() if x is not None)
        if name in params:
            return params[name]
        missing.append(name)
        return match.group(0)

    resolved = PLACEHOLDER_RE.sub(repl, path)
    return resolved, sorted(set(missing))


def classify(status):
    if status == 200:
        return "OK"
    if status in (401, 403):
        return "AUTH_OR_PERMISSION"
    if status == 404:
        return "NOT_FOUND"
    if status == 405:
        return "METHOD_NOT_ALLOWED"
    if status == 408:
        return "TIMEOUT"
    if status == 409:
        return "CONFLICT"
    if status == 429:
        return "RATE_LIMIT"
    if status is not None and 500 <= status <= 599:
        return "SERVER_ERROR"
    if status is not None and 400 <= status <= 499:
        return "CLIENT_ERROR"
    return "UNKNOWN"


def main():
    if not KEY:
        fail("ROAPP_API_KEY is required")
    if not INVENTORY.exists():
        fail(f"Inventory not found: {INVENTORY}")

    params = load_params()
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    operations = data.get("operations", [])
    templates = set()
    concrete = set()
    for op in operations:
        if "GET" not in op.get("methods", []):
            continue
        for raw in op.get("paths", []):
            path = normalize_path(raw)
            if not path:
                continue
            if PLACEHOLDER_RE.search(path):
                templates.add(path)
            else:
                concrete.add(path)

    results = []
    headers = {
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "User-Agent": "MARSEL-V20.18-Readonly",
    }

    with httpx.Client(timeout=TIMEOUT, follow_redirects=False) as client:
        for path in sorted(concrete):
            started = time.time()
            try:
                response = client.get(BASE + path, headers=headers)
                item = {
                    "path": path,
                    "resolved_path": path,
                    "http": response.status_code,
                    "classification": classify(response.status_code),
                    "elapsed_s": round(time.time() - started, 3),
                    "content_type": response.headers.get("content-type", ""),
                }
                if response.status_code != 200:
                    item["response_preview"] = response.text[:300].replace("\n", " ")
                results.append(item)
            except httpx.TimeoutException:
                results.append({"path": path, "resolved_path": path, "http": None, "classification": "TIMEOUT"})
            except Exception as exc:
                results.append({"path": path, "resolved_path": path, "http": None, "classification": "CLIENT_EXCEPTION", "error": type(exc).__name__})
            time.sleep(0.2)

        for template in sorted(templates):
            resolved, missing = resolve_path(template, params)
            if missing:
                results.append({
                    "path": template,
                    "resolved_path": None,
                    "http": None,
                    "classification": "PARAMETER_REQUIRED",
                    "missing_parameters": missing,
                })
                continue
            started = time.time()
            try:
                response = client.get(BASE + resolved, headers=headers)
                item = {
                    "path": template,
                    "resolved_path": resolved,
                    "http": response.status_code,
                    "classification": classify(response.status_code),
                    "elapsed_s": round(time.time() - started, 3),
                    "content_type": response.headers.get("content-type", ""),
                }
                if response.status_code != 200:
                    item["response_preview"] = response.text[:300].replace("\n", " ")
                results.append(item)
            except httpx.TimeoutException:
                results.append({"path": template, "resolved_path": resolved, "http": None, "classification": "TIMEOUT"})
            except Exception as exc:
                results.append({"path": template, "resolved_path": resolved, "http": None, "classification": "CLIENT_EXCEPTION", "error": type(exc).__name__})
            time.sleep(0.2)

    counts = {}
    for item in results:
        cls = item["classification"]
        counts[cls] = counts.get(cls, 0) + 1

    summary = {
        "inventory_documented_operations": len(operations),
        "unique_concrete_get_paths": len(concrete),
        "unique_parameterized_get_templates": len(templates),
        "paths_attempted": sum(x["classification"] != "PARAMETER_REQUIRED" for x in results),
        "paths_not_attempted_missing_parameters": sum(x["classification"] == "PARAMETER_REQUIRED" for x in results),
        "classifications": counts,
        "non_200": sum(x.get("http") != 200 for x in results),
        "network_errors": sum(x.get("http") is None and x["classification"] != "PARAMETER_REQUIRED" for x in results),
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    report = {
        "version": "20.18",
        "readonly": True,
        "api_base": BASE,
        "parameter_resolution": {
            "source": "ROAPP_PATH_PARAMS_JSON",
            "provided_parameter_names": sorted(params),
            "never_guess_identifiers": True,
        },
        "endpoints": results,
        "summary": summary,
        "write_requests_made": 0,
        "ro_app_data_mutated": False,
    }
    report["report_sha256"] = hashlib.sha256(
        json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== MARSEL V20.18 / STRICT ENDPOINT DIAGNOSTICS / READ ONLY ===")
    print(f"API_BASE={BASE}")
    print(f"CONCRETE_GET_PATHS={len(concrete)}")
    print(f"PARAMETERIZED_GET_TEMPLATES={len(templates)}")
    print(f"PATHS_ATTEMPTED={summary['paths_attempted']}")
    print(f"PATHS_NOT_ATTEMPTED_MISSING_PARAMETERS={summary['paths_not_attempted_missing_parameters']}")
    print("CLASSIFICATIONS=" + json.dumps(counts, sort_keys=True))
    print("WRITE_REQUESTS=0")
    print("RO_APP_DATA_MUTATED=False")
    print(f"REPORT={OUT}")
    print(f"REPORT_SHA256={report['report_sha256']}")
    if summary["network_errors"] or summary["non_200"]:
        print("RESULT=REVIEW_REQUIRED")
    else:
        print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
