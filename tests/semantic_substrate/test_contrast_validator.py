from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_validate_theme_node_returns_raw_and_rounded_ratio():
    result = ContrastValidator.validate_theme_node("#4A3110", "#FFE9A3")

    assert "contrast_ratio_raw" in result
    assert isinstance(result["contrast_ratio_raw"], float)
    assert result["contrast_ratio"] == round(result["contrast_ratio_raw"], 2)


def test_validate_theme_node_black_white_ratio_and_thresholds():
    result = ContrastValidator.validate_theme_node("#000000", "#FFFFFF")

    assert result["contrast_ratio"] == 21.0
    assert result["passes_wcag_aa"] is True
    assert result["passes_wcag_aaa"] is True


def test_validate_theme_node_identical_colors_fail_wcag():
    result = ContrastValidator.validate_theme_node("#777777", "#777777")

    assert result["contrast_ratio"] == 1.0
    assert result["passes_wcag_aa"] is False
    assert result["passes_wcag_aaa"] is False


def test_validate_theme_node_invalid_hex_raises():
    try:
        ContrastValidator.validate_theme_node("#12345", "#ffffff")
    except ValueError as exc:
        assert "Invalid hex color" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid hex color")
