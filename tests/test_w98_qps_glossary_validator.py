from governance.w98_qps_glossary_validator import validate_receipt


def good_receipt():
    return {
        "scope_anchor": "QPS",
        "subsystem_view": "QPLANT",
        "precedence": ["SCK_CEN_CONTRACTUAL", "APPLICANT_SPECIFIC", "GENERAL_RELATED"],
        "challenges": {
            "QPS": {"disposition": "FLAG_CONFLICT"},
            "PID": {"disposition": "FLAG_CONFLICT"},
            "SUPPLIER": {"disposition": "ACCEPT_APPLICANT_LOCAL"},
            "QPLANT": {"disposition": "ACCEPT_CANONICAL"},
            "MTBF": {"disposition": "ACCEPT_CANONICAL"},
        },
        "engineering_credit_delta": 0,
        "negotiation_credit_delta": 0,
    }


def test_good_receipt_passes():
    result = validate_receipt(good_receipt())
    assert result["status"] == "PASS"
    assert result["validated_challenges"] == 5


def test_silent_qps_normalisation_fails():
    receipt = good_receipt()
    receipt["challenges"]["QPS"]["disposition"] = "ACCEPT_CANONICAL"
    assert validate_receipt(receipt)["status"] == "FAIL"


def test_private_locator_leak_fails():
    receipt = good_receipt()
    receipt["private_source_locator"] = "forbidden"
    assert validate_receipt(receipt)["status"] == "FAIL"
