import pytest

from src.renderers.theme_runtime import SemanticThemeRuntime


def test_warning_dark_theme() -> None:
    runtime = SemanticThemeRuntime()
    theme = runtime.resolve('warning', 'dark')

    assert theme.background == '#3B2A00'
    assert theme.text == '#FFE9A3'
    assert theme.border == '#C89B00'


def test_ssot_light_theme() -> None:
    runtime = SemanticThemeRuntime()
    theme = runtime.resolve('ssot', 'light')

    assert theme.background == '#E3D5FF'
    assert theme.text == '#4B0082'
    assert theme.border == '#6A0DAD'


def test_decision_light_theme() -> None:
    runtime = SemanticThemeRuntime()
    theme = runtime.resolve('decision', 'light')

    assert theme.background == '#DDF4E4'
    assert theme.text == '#173524'
    assert theme.border == '#2D6A4F'


def test_decision_dark_theme() -> None:
    runtime = SemanticThemeRuntime()
    theme = runtime.resolve('decision', 'dark')

    assert theme.background == '#214F36'
    assert theme.text == '#DDFBE8'
    assert theme.border == '#49A078'


def test_invalid_semantic_type() -> None:
    runtime = SemanticThemeRuntime()

    with pytest.raises(ValueError, match="Unknown semantic_type 'invalid'"):
        runtime.resolve('invalid', 'light')


def test_invalid_mode() -> None:
    runtime = SemanticThemeRuntime()

    with pytest.raises(ValueError, match="Unknown mode 'invalid' for semantic_type 'warning'"):
        runtime.resolve('warning', 'invalid')
