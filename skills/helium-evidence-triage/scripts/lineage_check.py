#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
def classify(a:dict,b:dict)->dict:
    shared=sorted(set(a.get("lineage_keys",[]))&set(b.get("lineage_keys",[])));wrapper=a.get("wraps")==b.get("name") or b.get("wraps")==a.get("name")
    cls="NOT_INDEPENDENT_WRAPPER" if wrapper else "CORRELATED_LINEAGE" if shared else "POTENTIALLY_INDEPENDENT_REVIEW_REQUIRED"
    return {"classification":cls,"shared_lineage_keys":shared,"wrapper_relation":wrapper}
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("source_a");p.add_argument("source_b");a=p.parse_args();sa=json.loads(Path(a.source_a).read_text());sb=json.loads(Path(a.source_b).read_text());print(json.dumps(classify(sa,sb),indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
