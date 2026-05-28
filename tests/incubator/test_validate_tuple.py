"""Tests for validate_tuple.py script."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_tuple import (
    TupleValidationError,
    validate_tuple_filename,
    validate_tuple_id,
    validate_tuple_fields,
    validate_tuple_status,
    validate_tuple_source_type,
    validate_tuple,
    validate_all_tuples,
)


def test_validate_tuple_filename_valid():
    """Test valid tuple filename."""
    validate_tuple_filename("26_W22_12_35__INCUBATOR__RUNTIME_GOVERNANCE__CHAT_TUPLE_INGRESS_MAPPING__W000.yml")


def test_validate_tuple_filename_invalid():
    """Test invalid tuple filename."""
    with pytest.raises(TupleValidationError, match="doesn't match naming convention"):
        validate_tuple_filename("bad_filename.yml")


def test_validate_tuple_id_valid():
    """Test valid tuple ID."""
    validate_tuple_id("26_W22_12_35__INCUBATOR__RUNTIME_GOVERNANCE__CHAT_TUPLE_INGRESS_MAPPING__W000")


def test_validate_tuple_id_invalid():
    """Test invalid tuple ID."""
    with pytest.raises(TupleValidationError, match="doesn't match naming convention"):
        validate_tuple_id("bad_id")


def test_validate_tuple_fields_valid():
    """Test tuple with all required fields."""
    tuple_data = {
        "id": "test",
        "date": "2026-05-26",
        "time_local": "12:35",
        "iso_week": "2026-W22",
        "category": "INCUBATOR",
        "theme": "RUNTIME_GOVERNANCE",
        "title": "TEST",
        "wave": "W000",
        "status": "active",
        "repo": "GBOGEB/CODEX",
        "branch": "test",
        "source_type": "chat_tuple",
    }
    validate_tuple_fields(tuple_data)


def test_validate_tuple_fields_missing():
    """Test tuple missing required fields."""
    tuple_data = {"id": "test"}
    with pytest.raises(TupleValidationError, match="missing required fields"):
        validate_tuple_fields(tuple_data)


def test_validate_tuple_status_valid():
    """Test valid tuple status."""
    for status in ["active", "archived", "draft"]:
        validate_tuple_status(status)


def test_validate_tuple_status_invalid():
    """Test invalid tuple status."""
    with pytest.raises(TupleValidationError, match="not in allowed values"):
        validate_tuple_status("invalid")


def test_validate_tuple_source_type_valid():
    """Test valid tuple source_type."""
    for source_type in ["chat_tuple", "session_tuple"]:
        validate_tuple_source_type(source_type)


def test_validate_tuple_source_type_invalid():
    """Test invalid tuple source_type."""
    with pytest.raises(TupleValidationError, match="not in allowed values"):
        validate_tuple_source_type("invalid")


def test_validate_all_tuples():
    """Test validating all tuples in incubator directory."""
    tuples = validate_all_tuples()
    # Should have at least the W000 seed tuple
    assert isinstance(tuples, list)
    assert all(isinstance(t, dict) for t in tuples)
