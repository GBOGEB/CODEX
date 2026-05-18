import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'

REQUIRED_FILES = [
    'overlay_ssot.yaml',
    'invariants.yaml',
    'branch_dag.yaml',
    'STATE_RECONSTRUCTION.md',
    'semantic_delta_ledger.yaml',
    'roe_log.yaml',
]


def validate_required_files():
    missing = []
    for item in REQUIRED_FILES:
        path = SEMANTIC / item
        if not path.exists():
            missing.append(str(path))
    return missing


def validate_basic_ids():
    content = (SEMANTIC / 'invariants.yaml').read_text(encoding='utf-8')
    required = ['INV-001', 'INV-002', 'INV-003']
    missing = [rid for rid in required if rid not in content]
    return missing


def main():
    failures = []

    missing_files = validate_required_files()
    if missing_files:
        failures.append(f'Missing files: {missing_files}')

    missing_ids = validate_basic_ids()
    if missing_ids:
        failures.append(f'Missing invariant IDs: {missing_ids}')

    if failures:
        print('SEMANTIC VALIDATION FAILED')
        for failure in failures:
            print(f'- {failure}')
        sys.exit(1)

    print('SEMANTIC VALIDATION PASSED')
    sys.exit(0)


if __name__ == '__main__':
    main()
