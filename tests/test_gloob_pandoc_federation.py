import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "federation" / "global_mesh" / "GLOOB_PANDOC_FEDERATION_CONTRACT_v1.json"

def test_gloob_pandoc_federation_contract():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["producer"]["repo"] == "GBOGEB/CODEX"
    assert len(data["producer"]["head_sha"]) == 40
    assert {c["repo"] for c in data["consumers"]} == {
        "GBOGEB/ABACUS",
        "GBOGEB/cryoplant-project",
        "GBOGEB/DOCX_RTM_Automation",
    }
    assert data["authority"]["authority_transfer"] is False
    assert data["retirement_gate"]["default"] == "KEEP"
    assert "adapter_parity_PASS" in data["retirement_gate"]["required"]
    assert data["formal_credit_delta"] == 0
