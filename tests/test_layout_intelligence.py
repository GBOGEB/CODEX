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

    assert result
    assert len(result) == 1
    assert result[0].component == 'layout'
    assert result[0].decision == 'standard_card_layout'


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

    assert len(result) >= 2
    # Verify expected decisions are present
    components = [d.component for d in result]
    assert 'body' in components
    assert 'semantic-emphasis' in components
    # Verify specific decision content
    body_decision = next(d for d in result if d.component == 'body')
    assert body_decision.decision == 'split_card_or_reduce_density'
    semantic_decision = next(d for d in result if d.component == 'semantic-emphasis')
    assert semantic_decision.decision == 'reserve_visual_priority'
