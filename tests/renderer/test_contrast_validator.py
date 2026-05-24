#!/usr/bin/env python3

from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_target_invariant_warning_card_contrast():
    validator = ContrastValidator()
    dark_warning = validator.target_invariants["warning"]["dark"]

    bg = dark_warning["background"]
    text = dark_warning["text"]

    metrics = validator.validate_theme_node(bg, text)

    assert metrics["contrast_ratio"] >= 4.5
    assert metrics["wcag_aa_compliant"] is True


def test_failing_contrast_combination():
    validator = ContrastValidator()
    metrics = validator.validate_theme_node("#FFFFFF", "#D3D3D3")
    assert metrics["wcag_aa_compliant"] is False
