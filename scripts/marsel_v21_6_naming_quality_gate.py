#!/usr/bin/env python3
"""MARSEL V21.6 naming/manufacturer static Quality Gate.
Read-only: validates naming governance rules and seed taxonomy only.
"""
from pathlib import Path
import csv, sys, re
DOC=Path('docs/MARSEL_V21_6_NAMING_MANUFACTURER_DIRECTORY.md')
SEED=Path('data/marsel_v21_6_reference_seed.csv')
REQUIRED=['производител','бренд','модел','Reference','серийный номер','синоним','каноничес','орфограф','пунктуац']
def main():
    errors=[]; warnings=[]
    if not DOC.exists(): errors.append('missing_naming_directory')
    if not SEED.exists(): errors.append('missing_reference_seed')
    if DOC.exists():
        text=DOC.read_text(encoding='utf-8').lower()
        for x in REQUIRED:
            if x.lower() not in text: errors.append(f'missing_rule:{x}')
        if 'автоматическ' in text and 'объедин' in text and 'запрещ' not in text: warnings.append('auto_merge_rule_should_be_explicit')
    if SEED.exists():
        with SEED.open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        if not rows: errors.append('empty_reference_seed')
        else:
            required_cols={'type','canonical_name','status'}
            if not required_cols.issubset(rows[0]): errors.append('seed_schema_missing_columns')
            seen=set()
            for i,r in enumerate(rows,2):
                key=(r.get('type','').strip().lower(),r.get('canonical_name','').strip().lower())
                if key in seen: errors.append(f'duplicate_seed_row:{i}')
                seen.add(key)
                if not r.get('canonical_name','').strip(): errors.append(f'empty_canonical_name:{i}')
    print('MARSEL_V21_6_NAMING_QUALITY_GATE')
    print(f'ERRORS={len(errors)}'); [print('ERROR='+e) for e in errors]
    print(f'WARNINGS={len(warnings)}'); [print('WARNING='+w) for w in warnings]
    print('RO_APP_DATA_MUTATED=False')
    print('WRITE_REQUESTS_MADE=0')
    return 1 if errors else 0
if __name__=='__main__': sys.exit(main())
