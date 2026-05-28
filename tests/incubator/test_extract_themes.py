"""Tests for extract_themes.py script."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.extract_themes import extract_theme_counts


def test_extract_theme_counts():
    """Test theme extraction."""
    counts = extract_theme_counts()
    
    assert isinstance(counts, dict)
    assert len(counts) >= 1  # At least one theme from W000
    
    # All keys should be strings (theme names)
    for theme, count in counts.items():
        assert isinstance(theme, str)
        assert isinstance(count, int)
        assert count > 0


def test_runtime_governance_theme_present():
    """Test that RUNTIME_GOVERNANCE theme from W000 is present."""
    counts = extract_theme_counts()
    
    # W000 seed file has RUNTIME_GOVERNANCE theme
    assert "RUNTIME_GOVERNANCE" in counts
    assert counts["RUNTIME_GOVERNANCE"] >= 1


def test_counts_sorted():
    """Test that theme counts are sorted alphabetically."""
    counts = extract_theme_counts()
    themes = list(counts.keys())
    
    assert themes == sorted(themes), "Themes should be alphabetically sorted"
