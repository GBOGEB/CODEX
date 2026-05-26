import pytest

from governance.WCAG_CONTRAST_CHECKER import contrast_ratio
from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_contrast_validator_uses_governed_warning_dark_tokens() -> None:
    validator = ContrastValidator()

    assert validator.target_invariants["warning"]["dark"] == {
        "background": "#3A2F00",
        "text": "#FFE28A",
    }


def test_validate_theme_node_matches_governed_wcag_calculation() -> None:
    validator = ContrastValidator()
    warning_dark = validator.target_invariants["warning"]["dark"]

    result = validator.validate_theme_node(
        warning_dark["background"],
        warning_dark["text"],
    )

    assert result["contrast_ratio"] == round(contrast_ratio("#3A2F00", "#FFE28A"), 2)
    assert result["wcag_aa_compliant"] is True


def test_validate_theme_node_supports_short_hex_and_rejects_rgba() -> None:
    validator = ContrastValidator()

    assert validator.validate_theme_node("#000", "#fff")["contrast_ratio"] == 21.0

    with pytest.raises(ValueError, match="8-digit hex"):
        validator.validate_theme_node("#000000ff", "#ffffff")
