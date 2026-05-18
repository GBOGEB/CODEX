from semantic_substrate.analytics.semantic_debt_runtime import calculate_semantic_debt
from semantic_substrate.analytics.drift_runtime_minimal import scan_active_branch_alignment
from semantic_substrate.engines.replay_engine import SemanticReplayEngine


class SemanticTelemetryDashboard:
    def __init__(self):
        self.replay = SemanticReplayEngine()

    def summary(self):
        state = self.replay.reconstruct_state()
        debt = calculate_semantic_debt()
        drift = scan_active_branch_alignment()

        return {
            'snapshot_id': state.get('snapshot_id'),
            'active_branch_count': len(state.get('active_branches', [])),
            'tuple_count': state.get('tuple_count'),
            'delta_count': state.get('delta_count'),
            'debt_score': debt.get('score'),
            'debt_band': debt.get('band'),
            'drift_count': len(drift),
            'recommended_action': state.get('next_actions', ['none'])[0],
        }


if __name__ == '__main__':
    dashboard = SemanticTelemetryDashboard()
    print(dashboard.summary())
