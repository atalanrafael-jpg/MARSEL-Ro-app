#!/usr/bin/env python3
import os
import httpx
base=os.getenv('ROAPP_API_BASE','https://api.roapp.io/v2').rstrip('/')
key=os.getenv('ROAPP_API_KEY')
assert key
r=httpx.get(f'{base}/orders',headers={'Authorization':f'Bearer {key}','Accept':'application/json'},timeout=30)
print(f'HTTP={r.status_code}')
print(f'CONTENT_TYPE={r.headers.get("content-type","")}')
assert r.status_code == 200
print('WRITE_REQUESTS=0')
print('RO_APP_DATA_MUTATED=False')
