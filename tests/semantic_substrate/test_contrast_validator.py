import pytest

from semantic_substrate.renderer.contrast_validator import ContrastValidator


def test_validate_theme_node_default_warning_dark_thresholds() -> None:
    validator = ContrastValidator()
    warning_dark = validator.target_invariants["warning"]["dark"]

    result = validator.validate_theme_node(warning_dark["background"], warning_dark["text"])

    assert result["contrast_ratio"] == pytest.approx(10.03, abs=0.01)
    assert result["passes_wcag_aa"] is True
    assert result["passes_wcag_aaa"] is True


def test_validate_theme_node_invalid_hex_input_raises() -> None:
    with pytest.raises(ValueError):
        ContrastValidator.validate_theme_node("#12345", "#FFFFFF")

    with pytest.raises(ValueError):
        ContrastValidator.validate_theme_node("#ZZ0000", "#FFFFFF")


def test_validate_theme_node_boundary_at_aa_threshold(monkeypatch) -> None:
    luminance_map = {"#bg": 0.40, "#tx": 0.05}
    monkeypatch.setattr(
        ContrastValidator,
        "_relative_luminance",
        classmethod(lambda cls, color: luminance_map[color]),
    )

    result = ContrastValidator.validate_theme_node("#bg", "#tx")

    assert result["contrast_ratio"] == 4.5
    assert result["passes_wcag_aa"] is True
    assert result["passes_wcag_aaa"] is False


def test_validate_theme_node_boundary_at_aaa_threshold(monkeypatch) -> None:
    luminance_map = {"#bg": 0.65, "#tx": 0.05}
    monkeypatch.setattr(
        ContrastValidator,
        "_relative_luminance",
        classmethod(lambda cls, color: luminance_map[color]),
    )

    result = ContrastValidator.validate_theme_node("#bg", "#tx")

    assert result["contrast_ratio"] == 7.0
    assert result["passes_wcag_aa"] is True
    assert result["passes_wcag_aaa"] is True
