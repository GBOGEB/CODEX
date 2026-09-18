import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/"federation/qps/w286/validate_visual_golden_contract.py"
F=ROOT/"federation/qps/w286/QPS_W286_VISUAL_GOLDEN_SANITIZED_CONTRACT_v1.json"
S=importlib.util.spec_from_file_location("w286",V); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)
def load(): return json.loads(F.read_text(encoding="utf-8"))
def test_contract_passes(): assert M.validate(load())==[]
def test_authority_inversion_rejected():
    d=load(); d["semantic_authority"]="CODEX_AUTHORITY"; assert "authority_inversion" in M.validate(d)
def test_visual_divergence_required():
    d=load(); d["visual_binary_hashes_pairwise_distinct"]=False; assert "binary_divergence" in M.validate(d)
