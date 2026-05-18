def evaluate_merge(invariant_failures, lineage_breaks, reconstruction_failures):
    issues = []

    if invariant_failures:
        issues.append('invariant violations detected')

    if lineage_breaks:
        issues.append('tuple lineage continuity broken')

    if reconstruction_failures:
        issues.append('cold-start reconstruction failure detected')

    if issues:
        return {
            'merge_allowed': False,
            'issues': issues,
        }

    return {
        'merge_allowed': True,
        'issues': [],
    }


if __name__ == '__main__':
    print(evaluate_merge([], [], []))
