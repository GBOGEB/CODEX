import pytest

from renderers.lint.contrast_lint import _contrast_ratio, _hex_to_rgb


def test_hex_to_rgb_parses_hex_triplet() -> None:
    assert _hex_to_rgb('#804020') == pytest.approx((128 / 255, 64 / 255, 32 / 255))


def test_contrast_ratio_black_white_known_value() -> None:
    assert _contrast_ratio('#000000', '#FFFFFF') == 21.0


def test_contrast_ratio_identical_colors_is_one() -> None:
    assert _contrast_ratio('#3B2A00', '#3B2A00') == 1.0
