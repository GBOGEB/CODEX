"""Unit tests for ContrastValidator (WCAG contrast math)."""
import pytest

from semantic_substrate.renderer.contrast_validator import ContrastValidator


class TestHexToRgb:
    def setup_method(self):
        self.validator = ContrastValidator()

    def test_black_hex(self):
        r, g, b = self.validator._hex_to_rgb("#000000")
        assert r == 0.0 and g == 0.0 and b == 0.0

    def test_white_hex(self):
        r, g, b = self.validator._hex_to_rgb("#FFFFFF")
        assert abs(r - 1.0) < 1e-9 and abs(g - 1.0) < 1e-9 and abs(b - 1.0) < 1e-9

    def test_invalid_hex_raises_value_error(self):
        with pytest.raises(ValueError):
            self.validator._hex_to_rgb("#FFF")

    def test_invalid_hex_no_hash_raises_value_error(self):
        with pytest.raises(ValueError):
            self.validator._hex_to_rgb("GGGGGG")


class TestLinearize:
    def setup_method(self):
        self.validator = ContrastValidator()

    def test_below_threshold_uses_linear_formula(self):
        # channel <= 0.03928 → channel / 12.92
        result = self.validator._linearize(0.0)
        assert result == 0.0

    def test_at_threshold_boundary(self):
        # 0.03928 is on the boundary — uses linear formula
        result = self.validator._linearize(0.03928)
        assert abs(result - 0.03928 / 12.92) < 1e-9

    def test_above_threshold_uses_gamma_formula(self):
        result = self.validator._linearize(1.0)
        expected = ((1.0 + 0.055) / 1.055) ** 2.4
        assert abs(result - expected) < 1e-9


class TestRelativeLuminance:
    def setup_method(self):
        self.validator = ContrastValidator()

    def test_black_luminance_is_zero(self):
        assert self.validator._relative_luminance("#000000") == 0.0

    def test_white_luminance_is_one(self):
        lum = self.validator._relative_luminance("#FFFFFF")
        assert abs(lum - 1.0) < 1e-9


class TestValidateThemeNode:
    def setup_method(self):
        self.validator = ContrastValidator()

    def test_black_on_white_passes_wcag_aa(self):
        result = self.validator.validate_theme_node("#FFFFFF", "#000000")
        assert result["contrast_ratio"] == pytest.approx(21.0, abs=0.1)
        assert result["passes_wcag_aa"] is True

    def test_white_on_white_fails_wcag_aa(self):
        result = self.validator.validate_theme_node("#FFFFFF", "#FFFFFF")
        assert result["contrast_ratio"] == pytest.approx(1.0, abs=0.01)
        assert result["passes_wcag_aa"] is False

    def test_warning_dark_pair_passes_wcag_aa(self):
        # Validated G7 audit pair: background=#4A3110, text=#FFE9A3
        result = self.validator.validate_theme_node("#4A3110", "#FFE9A3")
        assert result["contrast_ratio"] == pytest.approx(10.03, abs=0.05)
        assert result["passes_wcag_aa"] is True

    def test_contrast_ratio_just_below_threshold_fails(self):
        # #777777 on #FFFFFF gives ~4.48:1, just below the 4.5:1 AA threshold
        result = self.validator.validate_theme_node("#FFFFFF", "#777777")
        assert result["contrast_ratio"] < 4.5
        assert result["passes_wcag_aa"] is False

    def test_ratio_at_aa_threshold_passes(self):
        # #767676 on #FFFFFF gives ~4.54:1, just above the 4.5:1 AA threshold
        result = self.validator.validate_theme_node("#FFFFFF", "#767676")
        assert result["contrast_ratio"] >= 4.5
        assert result["passes_wcag_aa"] is True

    def test_invalid_hex_raises(self):
        with pytest.raises(ValueError):
            self.validator.validate_theme_node("#ZZZ", "#000000")

    def test_symmetry_of_background_and_text(self):
        # Contrast ratio should be the same regardless of which is background
        r1 = self.validator.validate_theme_node("#4A3110", "#FFE9A3")
        r2 = self.validator.validate_theme_node("#FFE9A3", "#4A3110")
        assert r1["contrast_ratio"] == r2["contrast_ratio"]
