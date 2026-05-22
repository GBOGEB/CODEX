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


def test_unknown_semantic_type_raises_actionable_error() -> None:
    runtime = SemanticThemeRuntime()

    try:
        runtime.resolve('unknown', 'dark')
    except KeyError as exc:
        message = str(exc)
        assert 'Unknown semantic type' in message
        assert 'warning' in message
        assert 'ssot' in message
    else:
        assert False, 'Expected KeyError for unknown semantic type'


def test_unknown_mode_raises_actionable_error() -> None:
    runtime = SemanticThemeRuntime()

    try:
        runtime.resolve('warning', 'nocturne')
    except KeyError as exc:
        message = str(exc)
        assert "Unknown mode 'nocturne'" in message
        assert 'dark' in message
        assert 'light' in message
    else:
        assert False, 'Expected KeyError for unknown mode'
