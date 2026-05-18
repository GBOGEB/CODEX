from semantic_substrate.analytics.semantic_debt_runtime import calculate_semantic_debt
from semantic_substrate.analytics.drift_runtime_minimal import scan_active_branch_alignment
from semantic_substrate.engines.replay_engine import SemanticReplayEngine


class SemanticOrchestrator:
    def __init__(self):
        self.replay_engine = SemanticReplayEngine()

    def run_cycle(self):
        state = self.replay_engine.reconstruct_state()
        drift = scan_active_branch_alignment()
        debt = calculate_semantic_debt()

        return {
            'state': state,
            'drift': drift,
            'debt': debt,
            'recommended_action': self.replay_engine.recommend_next_action(),
        }


if __name__ == '__main__':
    orchestrator = SemanticOrchestrator()
    print(orchestrator.run_cycle())
