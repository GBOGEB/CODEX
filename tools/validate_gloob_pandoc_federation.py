#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "federation/global_mesh/GLOOB_PANDOC_FEDERATION_CONTRACT_v1.json"

REQUIRED_REPOS = {
    "GBOGEB/ABACUS": "DOW_DERIVED_ANALYSIS_CONSUMPTION",
    "GBOGEB/cryoplant-project": "CHILD_ENGINEERING_AUTHORITY",
    "GBOGEB/DOCX_RTM_Automation": "SOURCE_EXTRACTION_RTM_WORKER",
}
REQUIRED_FIDELITY = {
    "SEMANTIC_EXACT",
    "SEMANTIC_NEAR",
    "SEMANTIC_CHANGED",
    "FROZEN_RENDER",
    "RECONSTRUCTED_FROM_PDF",
    "OCR_REQUIRED",
}

def validate():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["producer"]["repo"] == "GBOGEB/CODEX"
    assert len(data["producer"]["head_sha"]) == 40
    consumers = {x["repo"]: x for x in data["consumers"]}
    assert set(consumers) == set(REQUIRED_REPOS)
    for repo, role in REQUIRED_REPOS.items():
        assert consumers[repo]["role"] == role
        assert len(consumers[repo]["head_sha"]) == 40
    assert data["authority"]["authority_transfer"] is False
    assert set(data["fidelity_classes"]) == REQUIRED_FIDELITY
    assert "adapter_parity_PASS" in data["retirement_gate"]["required"]
    assert data["retirement_gate"]["default"] == "KEEP"
    assert data["formal_credit_delta"] == 0
    return data

if __name__ == "__main__":
    validate()
    print("PASS: GLOOB/Pandoc federation contract invariants hold")
