import pytest

from renderers.lint.contrast_lint import _contrast_ratio, _hex_to_rgb


def test_hex_to_rgb_parses_hex_triplet() -> None:
    expected = (int('FF', 16) / 255, int('80', 16) / 255, int('40', 16) / 255)
    assert _hex_to_rgb('#FF8040') == pytest.approx(expected)


def test_contrast_ratio_black_white_known_value() -> None:
    assert _contrast_ratio('#000000', '#FFFFFF') == 21.0


def test_contrast_ratio_identical_colors_is_one() -> None:
    assert _contrast_ratio('#3B2A00', '#3B2A00') == 1.0
