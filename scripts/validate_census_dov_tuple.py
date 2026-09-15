#!/usr/bin/env python3
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
TUPLE=ROOT/'triage/census/roundtrip/TRIAGE_W62_IMMUTABLE_TUPLE.json'
REG=ROOT/'triage/census/CENSUS_DOV_PROOF_OPERATION.yaml'
if not TUPLE.exists():
    raise SystemExit('FAIL missing tuple')
if not REG.exists():
    raise SystemExit('FAIL missing operation registry')
obj=json.loads(TUPLE.read_text(encoding='utf-8'))
if obj.get('operation')!='CENSUS_DOV_PROOF':
    raise SystemExit('FAIL operation mismatch')
canon=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
print('tuple_id='+str(obj.get('tuple_id')))
print('canonical_sha256='+hashlib.sha256(canon).hexdigest())
print('semantic_disposition=VALID_FOR_DOW_ROUTE')
