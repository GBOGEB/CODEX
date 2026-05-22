from src.renderers.theme_runtime import SemanticThemeRuntime


def test_warning_dark_theme() -> None:
    runtime = SemanticThemeRuntime()
    theme = runtime.resolve('warning', 'dark')

    assert theme.background == '#3B2A00'
    assert theme.text == '#FFE9A3'


def test_ssot_light_theme() -> None:
    runtime = SemanticThemeRuntime()
    theme = runtime.resolve('ssot', 'light')

    assert theme.background == '#E3D5FF'
