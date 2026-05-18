def compress_runtime_state(state):
    return {
        'snapshot_id': state.get('snapshot_id'),
        'active_branch_count': len(state.get('active_branches', [])),
        'next_action': state.get('next_actions', ['none'])[0],
        'semantic_debt_count': len(state.get('semantic_debt', [])),
    }


if __name__ == '__main__':
    sample = {
        'snapshot_id': 'STATE-0001',
        'active_branches': ['semantic_substrate'],
        'next_actions': ['continue runtime stabilization'],
        'semantic_debt': ['drift analytics incomplete'],
    }

    print(compress_runtime_state(sample))
