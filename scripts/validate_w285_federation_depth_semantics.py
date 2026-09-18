#!/usr/bin/env python3
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "federation/w285/CODEX_W285_FEDERATION_DEPTH_SEMANTIC_REVIEW_v0.1.json"

def validate():
    d=json.loads(P.read_text(encoding="utf-8"))
    assert d["disposition"]=="ACCEPT_BOUNDED_CURRENT_USE_ATOM_MODEL"
    assert d["source"]["head"]=="23abb271c2747b63fa2a2c4c71a484ccdc339700"
    assert d["source"]["depth_blob"]=="691680cdf11289142b402a0ae02c95d46a246473"
    assert d["source"]["topology_blob"]=="df0ee845697578cd644691b81eafb2465249d772"
    assert d["semantic_findings"]["categories_mixed"] is False
    assert d["semantic_findings"]["bounded_sample_depth_reused"] is False
    assert d["semantic_findings"]["uncovered_function_zero_imputation"] is False
    assert d["measurement"]=={"B":1/3,"D":0.6,"PEN":0.2}
    assert d["formal_credit_delta"]==0
    assert d["authority_transfer"] is False
    return True

if __name__=="__main__":
    validate()
    print("PASS")
