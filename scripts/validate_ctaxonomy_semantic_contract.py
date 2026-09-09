#!/usr/bin/env python3
"""Validate the KEB-side CTaxonomy support contract without owning child definitions."""
from pathlib import Path
import sys
import yaml

PATH = Path("governance/ctaxonomy/CTAXONOMY_SEMANTIC_SUPPORT_CONTRACT_v1.yaml")


def main() -> int:
    data = yaml.safe_load(PATH.read_text(encoding="utf-8"))
    errors = []
    required = set(data.get("required_active_ids", []))
    expected = {"PLOC", "BFLOW", "GEO", "GEO-A", "GEO-B", "THERM", "THERM-A", "THERM-B"}
    if required != expected:
        errors.append("required_active_ids mismatch")
    validation = data.get("validation", {})
    for key in (
        "canonical_term_unique_per_taxonomy_id",
        "alias_resolves_to_exactly_one_taxonomy_id",
        "abbreviation_has_exactly_one_expansion",
        "alias_is_not_taxonomy_identity",
        "glossary_change_cannot_change_engineering_disposition",
        "parent_cannot_create_child_taxonomy_id",
    ):
        if validation.get(key) != "REQUIRED":
            errors.append(f"missing fail-closed rule: {key}")
    receipt = data.get("receipt", {})
    if receipt.get("engineering_credit_delta") != 0 or receipt.get("child_disposition_authority") is not False:
        errors.append("authority guard violated")
    if errors:
        print("KEB_CTAXONOMY_CONTRACT=FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("KEB_CTAXONOMY_CONTRACT=PASS")
    print("canonical_ids=8")
    print("engineering_credit_delta=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
