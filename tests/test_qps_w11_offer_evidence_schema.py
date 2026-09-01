from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest


SCHEMA_PATH = Path("schemas/qps_w11_offer_evidence.schema.json")


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_register() -> dict:
    return {
        "version": "0.1",
        "source_atoms": [
            {
                "atom_id": "ATOM-001",
                "source_id": "SRC-CUR-ALAT-OFFER",
                "source_sha256": "a" * 64,
                "source_format": "pdf",
                "source_locator": "page=210;table=1;row=4",
                "bidder": "ALAT",
                "evidence_class": "SOURCE_SUPPORTED",
                "extracted_text": "Sanitized bidder response placeholder.",
                "extraction_method": "pdf_table_text",
                "extraction_confidence": 0.98,
                "bidder_position": "COMPLIANT_WITH_REFERENCE",
            }
        ],
        "relations": [
            {
                "relation_id": "REL-001",
                "atom_id": "ATOM-001",
                "target_type": "RTM",
                "target_id": "RTM-514",
                "relation_type": "DIRECT_RTM",
                "lexical_score": 1.0,
                "reviewer_state": "UNREVIEWED",
            }
        ],
        "controls": {
            "no_cross_bidder_substitution": True,
            "no_inference_compliance_credit": True,
            "no_pca_bt_compliance_credit": True,
            "child_owned_final_disposition": True,
        },
    }


def test_valid_register_passes() -> None:
    jsonschema.Draft202012Validator(_schema()).validate(_valid_register())


@pytest.mark.parametrize("field", ["source_sha256", "source_locator"])
def test_source_identity_is_mandatory(field: str) -> None:
    candidate = _valid_register()
    candidate["source_atoms"][0].pop(field)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_schema()).validate(candidate)


def test_matching_scores_cannot_enter_evidence_truth_contract() -> None:
    candidate = copy.deepcopy(_valid_register())
    candidate["relations"][0]["semantic_score"] = 0.99
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_schema()).validate(candidate)


def test_control_flags_fail_closed() -> None:
    candidate = copy.deepcopy(_valid_register())
    candidate["controls"]["no_pca_bt_compliance_credit"] = False
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_schema()).validate(candidate)


def test_target_id_must_be_governed_rtm_or_offer_id() -> None:
    candidate = copy.deepcopy(_valid_register())
    candidate["relations"][0]["target_id"] = "REQ-514"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_schema()).validate(candidate)
