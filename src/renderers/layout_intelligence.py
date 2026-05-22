from __future__ import annotations

from dataclasses import dataclass

from src.renderers.lint.thresholds import MAX_CARD_BODY_LINES, MAX_TITLE_LENGTH


@dataclass
class LayoutDecision:
    component: str
    decision: str
    reason: str


@dataclass
class CardLayoutInput:
    title: str
    body_line_count: int
    figure_count: int = 0
    semantic_weight: str = 'normal'


class AdaptiveLayoutEngine:
    """Adaptive layout decision engine scaffold.

    The renderer should not blindly dump content into fixed cards.
    It should make deterministic, explainable layout decisions for:
    - title scaling
    - card sizing
    - content splitting
    - whitespace balancing
    - figure/text proportion
    """

    def decide_card_layout(self, card: CardLayoutInput) -> list[LayoutDecision]:
        decisions: list[LayoutDecision] = []

        if len(card.title) > MAX_TITLE_LENGTH:
            decisions.append(
                LayoutDecision(
                    component='title',
                    decision='scale_down_or_wrap',
                    reason='title exceeds recommended length',
                )
            )

        if card.body_line_count > MAX_CARD_BODY_LINES:
            decisions.append(
                LayoutDecision(
                    component='body',
                    decision='split_card_or_reduce_density',
                    reason='body exceeds preferred card line count',
                )
            )

        if card.figure_count > 1 and card.body_line_count > 10:
            decisions.append(
                LayoutDecision(
                    component='layout',
                    decision='use_two_column_or_figure_priority_layout',
                    reason='mixed dense text and multiple figures',
                )
            )

        if card.semantic_weight == 'critical':
            decisions.append(
                LayoutDecision(
                    component='semantic-emphasis',
                    decision='reserve_visual_priority',
                    reason='critical card requires higher visual hierarchy',
                )
            )

        if not decisions:
            decisions.append(
                LayoutDecision(
                    component='layout',
                    decision='standard_card_layout',
                    reason='content within governance thresholds',
                )
            )

        return decisions


if __name__ == '__main__':
    engine = AdaptiveLayoutEngine()
    sample = CardLayoutInput(
        title='Example renderer governance card',
        body_line_count=8,
    )
    for decision in engine.decide_card_layout(sample):
        print(f'{decision.component}: {decision.decision} ({decision.reason})')
