from __future__ import annotations

import pytest

from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_default_theme_path_is_module_relative(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    validator = ContrastValidator()

    assert validator.target_invariants["warning"]["dark"]["background"] == "#4A3110"


def test_black_white_ratio_matches_wcag_reference() -> None:
    validator = ContrastValidator()
    result = validator.validate_theme_node("#000000", "#ffffff")

    assert result["contrast_ratio"] == 21.0
    assert result["passes_wcag_aa"] is True


def test_same_color_has_ratio_one() -> None:
    validator = ContrastValidator()
    result = validator.validate_theme_node("#123456", "#123456")

    assert result["contrast_ratio"] == 1.0
    assert result["passes_wcag_aa"] is False


def test_wcag_aa_boundary_behavior() -> None:
    validator = ContrastValidator()
    passing = validator.validate_theme_node("#767676", "#FFFFFF")
    failing = validator.validate_theme_node("#777777", "#FFFFFF")

    assert passing["passes_wcag_aa"] is True
    assert passing["contrast_ratio"] >= 4.5
    assert failing["passes_wcag_aa"] is False
    assert failing["contrast_ratio"] < 4.5


@pytest.mark.parametrize("invalid_hex", ["123456", "#12", "#GGGGGG", "#00000000"])
def test_invalid_hex_rejected(invalid_hex: str) -> None:
    validator = ContrastValidator()

    with pytest.raises(ValueError, match="expected format '#RRGGBB' or '#RGB'|8-digit hex"):
        validator.validate_theme_node(invalid_hex, "#FFFFFF")
