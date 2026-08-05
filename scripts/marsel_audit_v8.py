#!/usr/bin/env python3
import json, os, sys
from datetime import datetime, timezone, date
import httpx

BASE = os.environ.get('ROAPP_API_BASE', 'https://api.roapp.io/v2').rstrip('/')
KEY = os.environ.get('ROAPP_API_KEY')
OUT = 'marsel-audit-v8-report.json'
PAGE_SIZE = int(os.environ.get('MARSEL_AUDIT_PAGE_SIZE', '100'))

if not KEY:
    print('ERROR: ROAPP_API_KEY is not configured')
    sys.exit(2)

H = {'Authorization': f'Bearer {KEY}', 'Accept': 'application/json'}

def get(path, params):
    r = httpx.get(BASE + path, params=params, headers=H, timeout=30)
    if r.status_code != 200:
        print(f'ERROR HTTP {r.status_code} GET {path}')
        sys.exit(3)
    return r.json()

def rows(p):
    if isinstance(p, list): return p
    if isinstance(p, dict):
        for k in ('orders', 'data', 'items'):
            if isinstance(p.get(k), list): return p[k]
    return []

def pages(p):
    x = p.get('paging', {}) if isinstance(p, dict) else {}
    for k in ('total_pages', 'totalPages', 'pages'):
        if isinstance(x.get(k), int): return x[k]
    return None

def d(v):
    if not isinstance(v, str): return None
    try: return datetime.fromisoformat(v.replace('Z', '+00:00')).date()
    except Exception:
        try: return date.fromisoformat(v[:10])
        except Exception: return None

def compact(x, reason):
    s = x.get('status') if isinstance(x.get('status'), dict) else {}
    t = x.get('order_type') if isinstance(x.get('order_type'), dict) else {}
    return {
        'id': x.get('id'), 'number': x.get('number'),
        'status_id': s.get('id'), 'status_name': s.get('name'),
        'order_type_id': t.get('id'), 'order_type_name': t.get('name'),
        'branch_id': x.get('branch_id'), 'assignee_id': x.get('assignee_id'),
        'manager_id': x.get('manager_id'), 'created_at': x.get('created_at'),
        'modified_at': x.get('modified_at'), 'due_date': x.get('due_date'),
        'closed_at': x.get('closed_at'), 'done_at': x.get('done_at'),
        'overdue': x.get('overdue'), 'status_overdue': x.get('status_overdue'),
        'diagnostic_reason': reason
    }

print('=== MARSEL AUDIT V8 / RO APP API / READ ONLY ===')
print(f'BASE={BASE}')
p = get('/orders', {'page': 1, 'pageSize': PAGE_SIZE})
total = pages(p)
data = rows(p)
if total is None:
    print('ERROR: API did not report total pages')
    sys.exit(4)
for n in range(2, total + 1):
    data += rows(get('/orders', {'page': n, 'pageSize': PAGE_SIZE}))

today = datetime.now(timezone.utc).date()
missing = [compact(x, 'missing_assignee_id') for x in data if x.get('assignee_id') is None]
future = []
for x in data:
    due = d(x.get('due_date'))
    if x.get('overdue') is True and due is not None and due >= today and x.get('closed_at') is None and x.get('done_at') is None:
        item = compact(x, 'overdue_flag_with_due_date_today_or_future')
        item['due_date_relation'] = 'today_or_future'
        future.append(item)

report = {
    'audit': 'MARSEL_AUDIT_V8', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    'readonly': True,
    'orders': {'http_status': 200, 'page_size': PAGE_SIZE, 'total_pages_reported': total,
               'pages_scanned': total, 'rows_scanned': len(data), 'pagination_complete': True},
    'targets': {'missing_assignee_count': len(missing), 'future_due_overdue_count': len(future)},
    'missing_assignee_orders': missing,
    'future_due_overdue_orders': future,
    'safety': {'writes_performed': False, 'updates_performed': False, 'deletes_performed': False,
               'client_names_phones_emails_excluded': True}
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f'HTTP /orders=200')
print(f'TOTAL_PAGES_REPORTED={total}')
print(f'PAGES_SCANNED={total}')
print(f'ROWS_SCANNED={len(data)}')
print('PAGINATION_COMPLETE=True')
print(f'MISSING_ASSIGNEE_ID={len(missing)}')
print(f'FUTURE_DUE_OVERDUE_FLAG={len(future)}')
print('--- MISSING_ASSIGNEE_DETAILS ---')
for x in missing:
    print(json.dumps(x, ensure_ascii=False, separators=(',', ':')))
print('--- FUTURE_DUE_OVERDUE_DETAILS ---')
for x in future:
    print(json.dumps(x, ensure_ascii=False, separators=(',', ':')))
print(f'REPORT={OUT}')
print('RESULT=READ_ONLY; NO RO APP DATA CREATED, UPDATED OR DELETED')
