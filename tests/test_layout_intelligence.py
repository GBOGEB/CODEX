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

    # Assert on structured fields instead of string representation
    components = [d.component for d in result]
    decisions = [d.decision for d in result]
    reasons = [d.reason for d in result]

    # Check for body density decision
    assert 'body' in components
    body_decision = next((d for d in result if d.component == 'body'), None)
    assert body_decision is not None
    assert 'split_card_or_reduce_density' == body_decision.decision

    # Check for layout decision (multiple figures + dense text)
    assert 'layout' in components
    layout_decision = next((d for d in result if d.component == 'layout'), None)
    assert layout_decision is not None
    assert 'use_two_column_or_figure_priority_layout' == layout_decision.decision

    # Check for semantic emphasis decision
    assert 'semantic-emphasis' in components
    semantic_decision = next((d for d in result if d.component == 'semantic-emphasis'), None)
    assert semantic_decision is not None
    assert 'reserve_visual_priority' == semantic_decision.decision
