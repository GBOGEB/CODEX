from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'


class SemanticReplayEngine:
    def __init__(self):
        self.snapshot_data = self._load_yaml('state_snapshots.yaml')
        self.branch_data = self._load_yaml('branch_dag.yaml')
        self.tuple_data = self._load_yaml('tuple_registry.yaml')
        self.delta_data = self._load_yaml('semantic_delta_ledger.yaml')

    def _load_yaml(self, filename):
        with open(SEMANTIC / filename, 'r', encoding='utf-8') as handle:
            return yaml.safe_load(handle) or {}

    def latest_snapshot(self):
        snapshots = self.snapshot_data.get('snapshots', [])
        if not snapshots:
            return None
        return snapshots[-1]

    def reconstruct_state(self):
        snapshot = self.latest_snapshot()
        if not snapshot:
            return {'status': 'no_snapshot'}

        return {
            'snapshot_id': snapshot.get('snapshot_id'),
            'active_branches': snapshot.get('active_branches', []),
            'active_invariants': snapshot.get('active_invariants', []),
            'next_actions': snapshot.get('next_actions', []),
            'semantic_debt': snapshot.get('unresolved_semantic_debt', []),
            'tuple_count': len(self.tuple_data.get('tuples', [])),
            'delta_count': len(self.delta_data.get('deltas', [])),
        }

    def recommend_next_action(self):
        state = self.reconstruct_state()
        actions = state.get('next_actions', [])
        return actions[0] if actions else 'no_action_available'


if __name__ == '__main__':
    engine = SemanticReplayEngine()
    print(engine.reconstruct_state())
    print(engine.recommend_next_action())
