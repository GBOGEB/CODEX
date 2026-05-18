def suggest_healing_actions(drift_items, debt_band):
    actions = []

    if drift_items:
        actions.append('update snapshots to align active branches')

    if debt_band == 'critical':
        actions.append('resolve unresolved semantic debt before merge')

    if not actions:
        actions.append('no healing action required')

    return actions


if __name__ == '__main__':
    print(suggest_healing_actions([], 'healthy'))
