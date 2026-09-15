#!/usr/bin/env python3
import hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
TUPLE=ROOT/'triage/census/roundtrip/TRIAGE_W62_IMMUTABLE_TUPLE.json'
REC=ROOT/'triage/census/roundtrip/TRIAGE_W62_CHILD_REENTRY_RECEIPT.yaml'
if not TUPLE.exists() or not REC.exists():
    raise SystemExit('FAIL missing tuple or child receipt')
obj=json.loads(TUPLE.read_text(encoding='utf-8'))
canon=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
canonical_sha=hashlib.sha256(canon).hexdigest()
text=REC.read_text(encoding='utf-8')
fields=['original_tuple_sha256','keb_forward_sha256','dow_input_sha256','dow_output_tuple_sha256','keb_normalized_sha256']
vals={}
for f in fields:
    m=re.search(r'^'+re.escape(f)+r':\s*([0-9a-f]{64})\s*$',text,re.M)
    if not m:
        raise SystemExit('FAIL missing '+f)
    vals[f]=m.group(1)
if len(set(vals.values()))!=1:
    raise SystemExit('FAIL receipt digest parity')
if 'child_disposition: ACCEPT' not in text:
    raise SystemExit('FAIL child disposition not ACCEPT')
if 'engineering_credit_delta: 0' not in text:
    raise SystemExit('FAIL engineering credit boundary')
print('tuple_id='+obj.get('tuple_id',''))
print('canonical_sha256='+canonical_sha)
print('receipt_raw_sha256='+next(iter(vals.values())))
print('digest_parity=PASS')
print('child_disposition=ACCEPT')
print('engineering_credit_delta=0')
