"""Tests for parse_chat_tuple.py script."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.parse_chat_tuple import (
    REQUIRED_KEYS,
    TUPLE_FILE_PATTERN,
    iter_tuple_files,
    load_tuple_documents,
    load_yaml_file,
)


def test_tuple_file_pattern():
    """Test the tuple filename pattern matching."""
    # Valid patterns
    assert TUPLE_FILE_PATTERN.match("26_W22_12_35__INCUBATOR__RUNTIME_GOVERNANCE__CHAT_TUPLE_INGRESS_MAPPING__W000.yml")
    assert TUPLE_FILE_PATTERN.match("26_W01_08_45__DELIVERY__BUILD__CI_PIPELINE__W001.yml")
    
    # Invalid patterns
    assert not TUPLE_FILE_PATTERN.match("session_tuple_schema.yml")
    assert not TUPLE_FILE_PATTERN.match("26_W22_12_35__INCUBATOR.yml")
    assert not TUPLE_FILE_PATTERN.match("README.md")


def test_iter_tuple_files():
    """Test iteration over tuple files."""
    incubator_dir = REPO_ROOT / "incubator"
    files = iter_tuple_files(incubator_dir)
    
    assert isinstance(files, list)
    assert len(files) >= 1  # At least the W000 seed file
    
    # All files should match pattern
    for file_path in files:
        assert TUPLE_FILE_PATTERN.match(file_path.name)
        assert file_path.suffix == ".yml"


def test_load_yaml_file():
    """Test YAML loading and validation."""
    incubator_dir = REPO_ROOT / "incubator"
    tuple_files = iter_tuple_files(incubator_dir)
    
    assert len(tuple_files) > 0, "No tuple files found"
    
    # Load first tuple file
    first_file = tuple_files[0]
    doc = load_yaml_file(first_file)
    
    assert isinstance(doc, dict)
    
    # Check all required keys present
    for key in REQUIRED_KEYS:
        assert key in doc, f"Required key '{key}' missing from {first_file.name}"


def test_load_tuple_documents():
    """Test loading all tuple documents."""
    docs = load_tuple_documents()
    
    assert isinstance(docs, list)
    assert len(docs) >= 1
    
    for doc in docs:
        # Check required fields
        for key in REQUIRED_KEYS:
            assert key in doc, f"Required key '{key}' missing"
        
        # Check _file added
        assert "_file" in doc
        assert doc["_file"].startswith("incubator/")


def test_tuple_id_format():
    """Test tuple ID format matches filename."""
    docs = load_tuple_documents()
    
    for doc in docs:
        # ID should match pattern
        id_val = doc["id"]
        filename = Path(doc["_file"]).stem  # Remove .yml extension
        
        # ID should match filename (without extension)
        assert id_val == filename, f"ID '{id_val}' doesn't match filename '{filename}'"


def test_tuple_wave_format():
    """Test wave field format."""
    docs = load_tuple_documents()
    
    for doc in docs:
        wave = doc["wave"]
        # Wave should be W### format
        assert wave.startswith("W"), f"Wave '{wave}' should start with 'W'"
        assert len(wave) == 4, f"Wave '{wave}' should be 4 characters (W###)"
        assert wave[1:].isdigit(), f"Wave '{wave}' should have 3 digits after 'W'"
