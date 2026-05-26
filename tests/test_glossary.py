#!/usr/bin/env python3
import pytest
import yaml


@pytest.fixture
def plane_data():
    with open("GLOSSARY.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_equation_object_contract_integrity(plane_data):
    equations = plane_data["glossary"]["equations"]
    required_keys = [
        "abbreviation",
        "caption",
        "latex_inline",
        "governance_meaning",
        "linked_dashboards",
        "linked_runtime",
        "thresholds",
    ]
    for eq_key, eq_data in equations.items():
        for key in required_keys:
            assert key in eq_data, f"Structure failure: Equation '{eq_key}' lacks '{key}' declaration token."


def test_caption_prefix_conventions(plane_data):
    equations = plane_data["glossary"]["equations"]
    valid_prefixes = ["FIG", "TAB", "PLT", "EQ"]
    for eq_key, eq_data in equations.items():
        caption_string = eq_data["caption"]
        assert any(caption_string.startswith(p) for p in valid_prefixes), (
            f"Nomenclature drift: '{eq_key}' caption fails prefix constraint rules."
        )
