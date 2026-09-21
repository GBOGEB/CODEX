#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "federation/global_mesh/GLOOB_PANDOC_FEDERATION_CONTRACT_v1.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

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
REQUIRED_GLOOB_OWNS = {
    "semantic_depth",
    "lens",
    "boundary",
    "BOOK_FLOW_GRAPH_projection_identity",
}
REQUIRED_PANDOC_OWNS = {
    "semantic_conversion",
    "normalized_AST_fingerprint",
    "semantic_roundtrip_receipt",
}
REQUIRED_MUST_NOT = {
    "transfer_QPS_engineering_authority",
    "replace_original_source_with_derived_extraction",
    "treat_PDF_to_editable_as_lossless",
    "retire_unique_renderer_capability_before_parity",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(data: dict | None = None) -> dict:
    if data is None:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    producer = data.get("producer") or {}
    require(producer.get("repo") == "GBOGEB/CODEX", "producer repo mismatch")
    require(bool(HEX40.fullmatch(str(producer.get("head_sha", "")))), "producer head is not lowercase 40-hex")

    consumers_list = data.get("consumers")
    require(isinstance(consumers_list, list), "consumers must be a list")
    require(all(isinstance(x, dict) for x in consumers_list), "consumer entries must be mappings")
    consumers = {x.get("repo"): x for x in consumers_list}
    require(set(consumers) == set(REQUIRED_REPOS), "consumer repo set mismatch")
    for repo, role in REQUIRED_REPOS.items():
        require(consumers[repo].get("role") == role, f"consumer role mismatch: {repo}")
        require(bool(HEX40.fullmatch(str(consumers[repo].get("head_sha", "")))), f"consumer head is not lowercase 40-hex: {repo}")

    authority = data.get("authority") or {}
    require(authority.get("authority_transfer") is False, "authority transfer must remain false")
    require(set(authority.get("gloob_owns") or []) == REQUIRED_GLOOB_OWNS, "gloob ownership set mismatch")
    require(set(authority.get("pandoc_owns") or []) == REQUIRED_PANDOC_OWNS, "pandoc ownership set mismatch")
    require(set(authority.get("must_not") or []) == REQUIRED_MUST_NOT, "authority prohibition set mismatch")

    require(set(data.get("fidelity_classes") or []) == REQUIRED_FIDELITY, "fidelity class set mismatch")
    retirement = data.get("retirement_gate") or {}
    require("adapter_parity_PASS" in (retirement.get("required") or []), "adapter parity retirement gate missing")
    require(retirement.get("default") == "KEEP", "retirement default must remain KEEP")
    require(data.get("formal_credit_delta") == 0, "formal credit delta must remain zero")
    return data


if __name__ == "__main__":
    validate()
    print("PASS: GLOOB/Pandoc federation contract invariants hold")
