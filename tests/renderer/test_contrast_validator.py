from pathlib import Path

import pytest
import yaml

from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_target_invariant_warning_card_contrast():
    validator = ContrastValidator()
    theme_path = Path(__file__).resolve().parent.parent.parent / "themes" / "semantic_cards.yaml"
    with theme_path.open("r", encoding="utf-8") as handle:
        warning_dark_theme = yaml.safe_load(handle)["semantic_cards"]["warning"]["dark"]
    dark_warning = validator.target_invariants["warning"]["dark"]

    assert dark_warning["background"] == warning_dark_theme["background"]
    assert dark_warning["text"] == warning_dark_theme["text"]

    metrics = validator.validate_theme_node(
        warning_dark_theme["background"], warning_dark_theme["text"]
    )
    assert metrics["wcag_aa_compliant"] is True
    assert metrics["contrast_ratio"] >= validator.MIN_AA_RATIO


def test_failing_contrast_combination():
    validator = ContrastValidator()
    metrics = validator.validate_theme_node("#FFFFFF", "#D3D3D3")

    assert metrics["wcag_aa_compliant"] is False
    assert metrics["action_required"] is True


def test_hex_normalization_and_rejections():
    validator = ContrastValidator()

    assert validator.calculate_relative_luminance("#abc") == pytest.approx(
        validator.calculate_relative_luminance("#aabbcc")
    )

    expected = {
        "##FFFFFF": "Unsupported hex color",
        "FFFFFF": "Unsupported hex color",
        "#FFFFFFFF": r"8-digit hex \(RGBA\) not supported",
        "#xyz": "Unsupported hex color",
    }
    for invalid_hex, message in expected.items():
        with pytest.raises(ValueError, match=message):
            validator.calculate_relative_luminance(invalid_hex)
