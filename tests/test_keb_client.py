"""Tests for KebClient (P5-3 buildout)."""

from __future__ import annotations

import pytest
from pathlib import Path

from src.keb.keb_client import KebClient


@pytest.fixture
def client() -> KebClient:
    """Return a KebClient pointing at the real KEB/governance/ directory."""
    return KebClient()


class TestResolveTerms:
    def test_keb_term_returns_definition(self, client: KebClient):
        definition = client.resolve_term("KEB")
        assert definition is not None
        assert len(definition) > 5

    def test_unknown_term_returns_none(self, client: KebClient):
        assert client.resolve_term("NONEXISTENT_XYZ") is None

    def test_known_terms_include_drift_and_convergence(self, client: KebClient):
        terms = client.list_terms()
        assert "DRIFT" in terms
        assert "CONVERGENCE" in terms


class TestGovernanceRules:
    def test_returns_list(self, client: KebClient):
        rules = client.get_governance_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_each_rule_has_id_and_rule_keys(self, client: KebClient):
        for rule in client.get_governance_rules():
            assert "id" in rule
            assert "rule" in rule

    def test_dbg_rule_001_exists(self, client: KebClient):
        ids = [r["id"] for r in client.get_governance_rules()]
        assert "DBG-001" in ids

    def test_convergence_rules_present(self, client: KebClient):
        ids = [r["id"] for r in client.get_governance_rules()]
        # At least one CR-xxx rule should exist
        assert any(i.startswith("CR-") for i in ids)


class TestKpiCategories:
    def test_returns_list_of_strings(self, client: KebClient):
        cats = client.get_kpi_categories()
        assert isinstance(cats, list)
        assert all(isinstance(c, str) for c in cats)

    def test_governance_category_present(self, client: KebClient):
        assert "governance" in client.get_kpi_categories()


class TestConfidenceLevels:
    def test_returns_dict(self, client: KebClient):
        levels = client.get_confidence_levels()
        assert isinstance(levels, dict)
        assert len(levels) > 0

    def test_high_level_exists(self, client: KebClient):
        levels = client.get_confidence_levels()
        assert "high" in levels


class TestMissingDirectory:
    def test_raises_file_not_found_for_bad_dir(self):
        bad_client = KebClient(keb_dir="/tmp/nonexistent_keb_dir")
        with pytest.raises(FileNotFoundError):
            bad_client.resolve_term("KEB")
