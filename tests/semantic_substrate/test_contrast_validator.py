from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_validate_theme_node_returns_raw_and_rounded_ratio():
    result = ContrastValidator.validate_theme_node("#4A3110", "#FFE9A3")

    assert "contrast_ratio_raw" in result
    assert isinstance(result["contrast_ratio_raw"], float)
    assert result["contrast_ratio"] == round(result["contrast_ratio_raw"], 2)
