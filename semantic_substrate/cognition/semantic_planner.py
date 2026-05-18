from semantic_substrate.analytics.semantic_debt_runtime import calculate_semantic_debt
from semantic_substrate.analytics.drift_runtime_minimal import scan_active_branch_alignment
from semantic_substrate.runtime.recommendation_engine import SemanticRecommendationEngine


class SemanticPlanner:
    def __init__(self):
        self.recommender = SemanticRecommendationEngine()

    def generate_plan(self):
        debt = calculate_semantic_debt()
        drift = scan_active_branch_alignment()
        recommendations = self.recommender.recommend()

        priorities = []

        if debt.get('band') in {'warning', 'critical'}:
            priorities.append('reduce semantic debt')

        if drift:
            priorities.append('resolve semantic drift')

        priorities.extend(recommendations)

        return {
            'runtime_phase': 'autonomous-semantic-cognition',
            'priority_count': len(priorities),
            'priorities': priorities,
        }


if __name__ == '__main__':
    planner = SemanticPlanner()
    print(planner.generate_plan())
