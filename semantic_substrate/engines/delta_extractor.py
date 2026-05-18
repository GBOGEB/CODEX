from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def classify_change(path: str):
    if path.endswith('.yaml'):
        return 'semantic-config'
    if path.endswith('.md'):
        return 'documentation'
    if path.endswith('.py'):
        return 'runtime'
    return 'unknown'


def generate_delta_stub(changed_files):
    return {
        'summary': 'Auto-generated semantic delta candidate',
        'files': [
            {
                'path': item,
                'classification': classify_change(item),
            }
            for item in changed_files
        ],
    }


if __name__ == '__main__':
    sample = [
        'semantic_substrate/invariants.yaml',
        'semantic_substrate/validators/validate_semantic_substrate.py',
    ]

    print(generate_delta_stub(sample))
