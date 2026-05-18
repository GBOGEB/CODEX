from datetime import datetime


def classify_path(path: str):
    if path.endswith('.yaml'):
        return 'semantic-config'
    if path.endswith('.py'):
        return 'runtime'
    if path.endswith('.md'):
        return 'documentation'
    return 'unclassified'


def generate_delta_candidate(changed_files):
    return {
        'generated_at': datetime.utcnow().isoformat(),
        'summary': 'Auto-generated semantic delta candidate',
        'changed_files': [
            {
                'path': path,
                'classification': classify_path(path),
            }
            for path in changed_files
        ],
        'recommended_delta_type': 'runtime-evolution',
    }


if __name__ == '__main__':
    sample_files = [
        'semantic_substrate/PROGRESS.md',
        'semantic_substrate/engines/replay_engine.py',
    ]

    print(generate_delta_candidate(sample_files))
