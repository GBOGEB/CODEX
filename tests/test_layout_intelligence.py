from src.renderers.layout_intelligence import (
    AdaptiveLayoutEngine,
    CardLayoutInput,
)


def test_standard_layout_path() -> None:
    engine = AdaptiveLayoutEngine()

    result = engine.decide_card_layout(
        CardLayoutInput(
            title='Short title',
            body_line_count=4,
        )
    )

    assert any(
        layout_decision.decision == 'standard_card_layout'
        for layout_decision in result
    )


def test_dense_layout_detection() -> None:
    engine = AdaptiveLayoutEngine()

    result = engine.decide_card_layout(
        CardLayoutInput(
            title='Dense engineering review card',
            body_line_count=24,
            figure_count=2,
            semantic_weight='critical',
        )
    )

    decisions = [str(decision).lower() for decision in result]

    assert any('dense' in decision and 'text' in decision for decision in decisions)
    assert any('multiple' in decision and 'figure' in decision for decision in decisions)
    assert any('critical' in decision and 'semantic' in decision for decision in decisions)
