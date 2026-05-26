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
    assert 'governance thresholds' in result[0].reason


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

    # Should trigger: body split, layout adjustment, and semantic emphasis
    assert len(result) == 3
    
    # Check that body split decision is present
    body_decisions = [d for d in result if d.component == 'body']
    assert len(body_decisions) == 1
    assert 'split_card_or_reduce_density' in body_decisions[0].decision
    
    # Check that layout decision for figures+text is present
    layout_decisions = [d for d in result if d.component == 'layout']
    assert len(layout_decisions) == 1
    assert 'two_column' in layout_decisions[0].decision.lower()
    
    # Check that semantic emphasis is present
    semantic_decisions = [d for d in result if d.component == 'semantic-emphasis']
    assert len(semantic_decisions) == 1
    assert 'visual_priority' in semantic_decisions[0].decision
