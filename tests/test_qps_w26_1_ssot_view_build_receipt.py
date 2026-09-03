import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "qps_ssot_view_build_receipt.schema.json"
RECEIPT = ROOT / "receipts" / "qps_w26_1_ssot_view_build_receipt.json"


def test_qps_w26_1_receipt_conforms_to_schema_and_has_no_credit():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(receipt)
    assert receipt["row_count"] == 449
    assert receipt["formal_credit"] == 0
    assert all(receipt["semantic_guardrails"].values())
    assert set(receipt["visual_qa"].values()) == {"PASS"}
