from semantic_substrate.analytics.semantic_debt_runtime import calculate_semantic_debt
from semantic_substrate.runtime.recommendation_engine import SemanticRecommendationEngine


class RuntimeReasoningEngine:
    def __init__(self):
        self.recommender = SemanticRecommendationEngine()

    def reason(self):
        debt = calculate_semantic_debt()
        recommendations = self.recommender.recommend()

        reasoning = []

        if debt.get('score', 0) > 10:
            reasoning.append('runtime stability risk increasing')

        if recommendations:
            reasoning.append('recommendation pipeline active')

        if not reasoning:
            reasoning.append('runtime cognition stable')

        return {
            'reasoning': reasoning,
            'recommendations': recommendations,
        }


if __name__ == '__main__':
    engine = RuntimeReasoningEngine()
    print(engine.reason())
