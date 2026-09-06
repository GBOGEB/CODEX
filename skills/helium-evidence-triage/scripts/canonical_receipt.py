#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
SCHEMA="helium-evidence-receipt/v1"
def canonical(obj:Any)->str:return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def sha256(obj:Any)->str:return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()
def build(payload:dict[str,Any])->dict[str,Any]:
    body=dict(payload);body.setdefault("schema",SCHEMA);request=body.pop("request",{})
    body["request_sha256"]=sha256(request)
    body["calculation_id"]=sha256({"schema":body["schema"],"request_sha256":body["request_sha256"],"provider":body.get("provider"),"provider_version":body.get("provider_version")})
    body["ssot_sha256"]=sha256(body);return body
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("input");p.add_argument("output");a=p.parse_args();payload=json.loads(Path(a.input).read_text(encoding="utf-8"));receipt=build(payload);Path(a.output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(receipt["ssot_sha256"]);return 0
if __name__=="__main__":raise SystemExit(main())
