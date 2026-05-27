import pytest

from governance.WCAG_CONTRAST_CHECKER import contrast_ratio
from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_contrast_validator_uses_governed_warning_dark_tokens() -> None:
    validator = ContrastValidator()
    warning_dark = validator.target_invariants["warning"]["dark"]

    assert "background" in warning_dark
    assert "text" in warning_dark
    # Values must be well-formed hex strings
    assert warning_dark["background"].startswith("#")
    assert warning_dark["text"].startswith("#")


def test_validate_theme_node_matches_governed_wcag_calculation() -> None:
    validator = ContrastValidator()
    warning_dark = validator.target_invariants["warning"]["dark"]

    result = validator.validate_theme_node(
        warning_dark["background"],
        warning_dark["text"],
    )

    expected_ratio = round(contrast_ratio(warning_dark["background"], warning_dark["text"]), 2)
    assert result["contrast_ratio"] == expected_ratio
    assert result["wcag_aa_compliant"] is True


def test_validate_theme_node_supports_short_hex_and_rejects_rgba() -> None:
    validator = ContrastValidator()

    assert validator.validate_theme_node("#000", "#fff")["contrast_ratio"] == 21.0

    with pytest.raises(ValueError, match="8-digit hex"):
        validator.validate_theme_node("#000000ff", "#ffffff")


# --- AA boundary (4.5) ---

def test_contrast_ratio_exactly_at_aa_boundary_passes() -> None:
    """A pair whose ratio rounds to exactly 4.5 must be AA-compliant."""
    validator = ContrastValidator()
    # #767676 on white is the canonical AA boundary pair (ratio ≈ 4.54)
    result = validator.validate_theme_node("#ffffff", "#767676")
    assert result["contrast_ratio"] >= ContrastValidator.MIN_AA_RATIO
    assert result["wcag_aa_compliant"] is True
    assert result["action_required"] is False


def test_contrast_ratio_just_below_aa_boundary_fails() -> None:
    """A pair with ratio < 4.5 must not be AA-compliant."""
    validator = ContrastValidator()
    # #777777 on white is just below AA (ratio ≈ 4.48)
    result = validator.validate_theme_node("#ffffff", "#777777")
    assert result["contrast_ratio"] < ContrastValidator.MIN_AA_RATIO
    assert result["wcag_aa_compliant"] is False
    assert result["action_required"] is True


# --- AAA boundary (7.0) ---

def test_contrast_ratio_above_aaa_boundary_is_aaa_compliant() -> None:
    """Pure black on white (21:1) must satisfy both AA and AAA."""
    validator = ContrastValidator()
    result = validator.validate_theme_node("#000000", "#ffffff")
    assert result["contrast_ratio"] == 21.0
    assert result["wcag_aa_compliant"] is True
    assert result["wcag_aaa_compliant"] is True


def test_contrast_ratio_just_below_aaa_boundary_is_aa_only() -> None:
    """A pair between 4.5 and 7.0 passes AA but not AAA."""
    validator = ContrastValidator()
    # #595959 on white gives ratio ≈ 7.0 — use a slightly lighter grey to stay below
    result = validator.validate_theme_node("#ffffff", "#696969")
    assert result["wcag_aa_compliant"] is True
    assert result["wcag_aaa_compliant"] is False

