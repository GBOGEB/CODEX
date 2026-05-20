from semantic_substrate.engines.semantic_planning_engine import build_semantic_plan


def test_build_semantic_plan_generates_drift_adjusted_priority():
    drift_report = {'drift_score': 3, 'debt_status': 'warning'}
    snapshot = {'unresolved_semantic_debt': ['tuple replay persistence not implemented']}
    proposals = {
        'proposals': [
            {
                'recommendation': 'Add manifest and semantic delta coverage for `x`.',
                'rule_id': 'DRIFT-002',
                'severity': 'warning',
            }
        ]
    }
    report = build_semantic_plan(drift_report, snapshot, proposals)

    assert report['priorities']
    assert report['priorities'][0]['drift_adjusted_priority'] >= drift_report['drift_score']
