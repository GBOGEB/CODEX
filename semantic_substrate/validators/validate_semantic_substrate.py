import pathlib
import re
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'

REQUIRED_FILES = [
    'overlay_ssot.yaml',
    'invariants.yaml',
    'branch_dag.yaml',
    'STATE_RECONSTRUCTION.md',
    'semantic_delta_ledger.yaml',
    'roe_log.yaml',
    'tuple_registry.yaml',
    'state_snapshots.yaml',
    'evolution_roadmap.yaml',
]

REQUIRED_DIRS = [
    'engines',
    'validators',
    'analytics',
    'agents',
    'merge',
    'digital_twin',
]

PATTERNS = {
    'invariant': re.compile(r'^INV-[0-9]{3}$'),
    'tuple': re.compile(r'^(ROOT|TUP-[0-9]{4})$'),
    'delta': re.compile(r'^DELTA-[0-9]{4}$'),
    'state': re.compile(r'^STATE-[0-9]{4}$'),
    'roe': re.compile(r'^ROE-[0-9]{4}$'),
}


def load_yaml(relative_path):
    if yaml is None:
        raise RuntimeError('PyYAML is required for semantic validation')
    path = SEMANTIC / relative_path
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def validate_required_files():
    return [str(SEMANTIC / item) for item in REQUIRED_FILES if not (SEMANTIC / item).exists()]


def validate_required_dirs():
    return [str(SEMANTIC / item) for item in REQUIRED_DIRS if not (SEMANTIC / item).is_dir()]


def validate_unique_ids(items, id_field, pattern_name):
    failures = []
    seen = set()
    pattern = PATTERNS[pattern_name]
    for item in items:
        item_id = item.get(id_field)
        if not item_id:
            failures.append(f'missing {id_field}: {item}')
            continue
        if not pattern.match(item_id):
            failures.append(f'invalid {id_field}: {item_id}')
        if item_id in seen:
            failures.append(f'duplicate {id_field}: {item_id}')
        seen.add(item_id)
    return failures


def validate_invariants():
    data = load_yaml('invariants.yaml')
    invariants = data.get('invariants', [])
    failures = validate_unique_ids(invariants, 'id', 'invariant')
    required = {'INV-001', 'INV-002', 'INV-003'}
    actual = {item.get('id') for item in invariants}
    missing = sorted(required - actual)
    if missing:
        failures.append(f'missing core invariants: {missing}')
    return failures


def validate_tuple_lineage():
    data = load_yaml('tuple_registry.yaml')
    tuples = data.get('tuples', [])
    failures = validate_unique_ids(tuples, 'tuple_id', 'tuple')
    ids = {item.get('tuple_id') for item in tuples}
    for item in tuples:
        tuple_id = item.get('tuple_id')
        parent_id = item.get('parent_id')
        if tuple_id == 'ROOT':
            if parent_id is not None:
                failures.append('ROOT tuple must not have parent_id')
            continue
        if not parent_id:
            failures.append(f'{tuple_id} missing parent_id')
        elif parent_id not in ids:
            failures.append(f'{tuple_id} references missing parent_id {parent_id}')
    return failures


def validate_branch_dag():
    data = load_yaml('branch_dag.yaml')
    branches = data.get('branches', [])
    failures = []
    ids = {item.get('id') for item in branches}
    parent_map = {item.get('id'): item.get('parent') for item in branches}
    allowed_status = {'active', 'dormant', 'merged', 'abandoned', 'planned'}

    if 'ROOT' not in ids:
        failures.append('branch DAG missing ROOT node')

    for item in branches:
        node = item.get('id')
        status = item.get('status')
        if status not in allowed_status:
            failures.append(f'{node} has invalid status {status}')
        parent = item.get('parent')
        if node != 'ROOT' and parent not in ids:
            failures.append(f'{node} references missing parent branch {parent}')

    for node in ids:
        visited = set()
        current = node
        while current:
            if current in visited:
                failures.append(f'branch cycle detected at {node}')
                break
            visited.add(current)
            current = parent_map.get(current)
    return failures


def validate_deltas():
    data = load_yaml('semantic_delta_ledger.yaml')
    deltas = data.get('deltas', [])
    failures = validate_unique_ids(deltas, 'id', 'delta')
    for item in deltas:
        for field in ['date', 'from_state', 'to_state', 'summary', 'impact']:
            if field not in item:
                failures.append(f"{item.get('id')} missing {field}")
    return failures


def validate_snapshots():
    data = load_yaml('state_snapshots.yaml')
    snapshots = data.get('snapshots', [])
    failures = validate_unique_ids(snapshots, 'snapshot_id', 'state')
    for item in snapshots:
        if 'next_actions' not in item:
            failures.append(f"{item.get('snapshot_id')} missing next_actions")
    return failures


def validate_roe():
    data = load_yaml('roe_log.yaml')
    roe_items = data.get('roe', [])
    failures = validate_unique_ids(roe_items, 'id', 'roe')
    for item in roe_items:
        for field in ['date', 'trigger', 'cause', 'correction', 'prevention']:
            if field not in item:
                failures.append(f"{item.get('id')} missing {field}")
    return failures


def main():
    checks = {
        'required_files': validate_required_files,
        'required_dirs': validate_required_dirs,
        'invariants': validate_invariants,
        'tuple_lineage': validate_tuple_lineage,
        'branch_dag': validate_branch_dag,
        'deltas': validate_deltas,
        'snapshots': validate_snapshots,
        'roe': validate_roe,
    }

    failures_by_check = defaultdict(list)
    for name, check in checks.items():
        try:
            failures = check()
        except Exception as exc:  # pragma: no cover
            failures = [f'{type(exc).__name__}: {exc}']
        if failures:
            failures_by_check[name].extend(failures)

    if failures_by_check:
        print('SEMANTIC VALIDATION FAILED')
        for name, failures in failures_by_check.items():
            print(f'[{name}]')
            for failure in failures:
                print(f'- {failure}')
        sys.exit(1)

    print('SEMANTIC VALIDATION PASSED')
    sys.exit(0)


if __name__ == '__main__':
    main()
