"""Tests for build_incubator_index.py script."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_incubator_index import build_markdown


def test_build_markdown():
    """Test Markdown index generation."""
    markdown = build_markdown()
    
    assert isinstance(markdown, str)
    assert len(markdown) > 0
    
    # Check for required sections
    assert "# Incubator Index" in markdown
    assert "Machine-readable tuple ingress index" in markdown
    assert "| ID | Date | Time | Category | Theme | Title | Wave | Status | Source |" in markdown
    
    # Check for required notes
    assert "## Notes" in markdown
    assert "YY_Www_HH_MM__CATEGORY__THEME__TITLE__STATUS" in markdown
    assert "python scripts/build_incubator_index.py" in markdown


def test_markdown_has_seed_tuple():
    """Test that seed tuple W000 appears in index."""
    markdown = build_markdown()
    
    # W000 seed file should be present
    assert "W000" in markdown
    assert "INCUBATOR" in markdown
    assert "RUNTIME_GOVERNANCE" in markdown
    assert "CHAT_TUPLE_INGRESS_MAPPING" in markdown


def test_markdown_table_structure():
    """Test Markdown table has proper structure."""
    markdown = build_markdown()
    lines = markdown.split("\n")
    
    # Find table header
    header_idx = None
    for i, line in enumerate(lines):
        if "| ID | Date | Time |" in line:
            header_idx = i
            break
    
    assert header_idx is not None, "Table header not found"
    
    # Next line should be separator
    separator_line = lines[header_idx + 1]
    assert "|" in separator_line
    assert "---" in separator_line
