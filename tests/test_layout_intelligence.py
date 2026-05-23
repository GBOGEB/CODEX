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

    assert len(result) == 3
    
    # Verify body split decision
    body_decisions = [d for d in result if d.component == 'body']
    assert len(body_decisions) == 1
    assert body_decisions[0].decision == 'split_card_or_reduce_density'
    
    # Verify layout decision for mixed content
    layout_decisions = [d for d in result if d.component == 'layout']
    assert len(layout_decisions) == 1
    assert layout_decisions[0].decision == 'use_two_column_or_figure_priority_layout'
    
    # Verify semantic emphasis for critical weight
    semantic_decisions = [d for d in result if d.component == 'semantic-emphasis']
    assert len(semantic_decisions) == 1
    assert semantic_decisions[0].decision == 'reserve_visual_priority'
