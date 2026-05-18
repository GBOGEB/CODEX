from semantic_substrate.analytics.semantic_debt_runtime import calculate_semantic_debt


class GovernanceRecommendationRuntime:
    def recommend(self):
        debt = calculate_semantic_debt()
        score = debt.get('score', 0)
        band = debt.get('band', 'unknown')

        recommendations = []

        if band in {'warning', 'critical'}:
            recommendations.append('review semantic debt policy thresholds')

        if score == 0:
            recommendations.append('governance baseline stable')

        if not recommendations:
            recommendations.append('continue monitoring governance signals')

        return {
            'debt_score': score,
            'debt_band': band,
            'recommendations': recommendations,
        }


if __name__ == '__main__':
    runtime = GovernanceRecommendationRuntime()
    print(runtime.recommend())
