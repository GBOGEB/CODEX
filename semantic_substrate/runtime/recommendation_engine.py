from semantic_substrate.analytics.semantic_debt_runtime import calculate_semantic_debt
from semantic_substrate.analytics.drift_runtime_minimal import scan_active_branch_alignment


class SemanticRecommendationEngine:
    def recommend(self):
        debt = calculate_semantic_debt()
        drift = scan_active_branch_alignment()

        recommendations = []

        if debt.get('band') == 'critical':
            recommendations.append('prioritize semantic debt reduction')

        if drift:
            recommendations.append('resolve active branch drift')

        if not recommendations:
            recommendations.append('continue runtime stabilization')

        return recommendations


if __name__ == '__main__':
    engine = SemanticRecommendationEngine()
    print(engine.recommend())
