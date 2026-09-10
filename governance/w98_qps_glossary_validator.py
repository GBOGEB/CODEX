"""W98 QPS glossary 3PC/3PR semantic/provenance validator.

Public KEB validator: consumes only a redacted child receipt and never requires
private bidder text, locators or digests.
"""
from __future__ import annotations

REQUIRED_CHALLENGES = {
    "QPS": "FLAG_CONFLICT",
    "PID": "FLAG_CONFLICT",
    "SUPPLIER": "ACCEPT_APPLICANT_LOCAL",
    "QPLANT": "ACCEPT_CANONICAL",
    "MTBF": "ACCEPT_CANONICAL",
}
FORBIDDEN_KEYS = {
    "private_source_locator", "private_source_digest", "commercial_information",
    "raw_offer_text", "cross_bidder_comparison",
}


def validate_receipt(receipt: dict) -> dict:
    errors: list[str] = []
    if receipt.get("scope_anchor") != "QPS":
        errors.append("scope_anchor_must_be_QPS")
    if receipt.get("subsystem_view") != "QPLANT":
        errors.append("QPLANT_must_be_subsystem_view")
    if receipt.get("precedence") != ["SCK_CEN_CONTRACTUAL", "APPLICANT_SPECIFIC", "GENERAL_RELATED"]:
        errors.append("authority_precedence_invalid")
    leaked = sorted(FORBIDDEN_KEYS.intersection(receipt))
    if leaked:
        errors.append("private_fields_present:" + ",".join(leaked))
    challenges = receipt.get("challenges", {})
    for token, expected in REQUIRED_CHALLENGES.items():
        actual = challenges.get(token, {}).get("disposition")
        if actual != expected:
            errors.append(f"challenge:{token}:expected:{expected}:got:{actual}")
    if receipt.get("engineering_credit_delta", 0) != 0:
        errors.append("engineering_credit_must_be_zero")
    if receipt.get("negotiation_credit_delta", 0) != 0:
        errors.append("negotiation_credit_must_be_zero")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "validated_challenges": len(REQUIRED_CHALLENGES) - sum(e.startswith("challenge:") for e in errors),
        "authority_preserved": not any("authority" in e for e in errors),
    }
