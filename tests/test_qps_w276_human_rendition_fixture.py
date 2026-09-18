from pathlib import Path
import importlib.util, json
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/"federation/qps/w276/validate_human_rendition_fixture.py"
F=ROOT/"federation/qps/w276/QPS_W276_HUMAN_RENDITION_SANITIZED_FIXTURE_v1.json"
SPEC=importlib.util.spec_from_file_location("w276",V); M=importlib.util.module_from_spec(SPEC); assert SPEC.loader is not None; SPEC.loader.exec_module(M)

def test_sanitized_contract():
    data=json.loads(F.read_text(encoding="utf-8"))
    assert M.validate(data)==[]
    assert M.compact(data["atomic_refs"])=="RTM-456..464"
