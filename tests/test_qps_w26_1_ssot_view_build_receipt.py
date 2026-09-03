import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "qps_ssot_view_build_receipt.schema.json"
RECEIPT = ROOT / "receipts" / "qps_w26_1_ssot_view_build_receipt.json"


def test_qps_w26_1_receipt_conforms_to_schema_and_has_no_credit():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    validator.validate(receipt)
    assert receipt["source_sha256"] == "d012ac1313df9a2dff4cc838f2e05f70699052587b0979046a2a58528e97b7fb"
    assert receipt["outputs"] == [
        "QPS_LKT_NEGO_RFI_COMPLIANCE_SSOT_v1.0.xlsx",
        "QPS_LKT_NEGO_RFI_COMPLIANCE_SSOT_v1.0.html",
        "QPS_LKT_NEGO_RFI_COMPLIANCE_SSOT_v1.0_management.pptx",
        "QPS_LKT_NEGO_RFI_COMPLIANCE_SSOT_v1.0_management.pdf",
    ]
    assert receipt["style_contract"]["palette_source"] == "GBOGEB/ABACUS:ssot/ssot_style.json"
    assert receipt["row_count"] == 449
    assert receipt["formal_credit"] == 0
    assert all(receipt["semantic_guardrails"].values())
    assert set(receipt["visual_qa"].values()) == {"PASS"}
