from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'


def load_yaml(relative_path):
    with open(SEMANTIC / relative_path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def scan_active_branch_alignment():
    branch_dag = load_yaml('branch_dag.yaml')
    snapshots = load_yaml('state_snapshots.yaml')

    active_snapshot = snapshots.get('snapshots', [])[-1]
    snapshot_branches = set(active_snapshot.get('active_branches', []))

    drift = []

    for branch in branch_dag.get('branches', []):
        branch_id = branch.get('id')
        branch_status = branch.get('status')

        if branch_status == 'active' and branch_id not in snapshot_branches:
            drift.append({
                'branch': branch_id,
                'reason': 'active branch missing from latest snapshot',
            })

    return drift


if __name__ == '__main__':
    report = scan_active_branch_alignment()
    print({'drift_items': report, 'count': len(report)})
