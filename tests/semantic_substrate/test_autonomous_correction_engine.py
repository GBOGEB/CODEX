from semantic_substrate.engines.autonomous_correction_engine import generate_correction_proposals


def test_generate_correction_proposals_marks_human_approval():
    drift_report = {
        'debt_status': 'warning',
        'findings': [
            {
                'rule_id': 'DRIFT-002',
                'severity': 'warning',
                'path': 'semantic_substrate/new_file.yaml',
                'message': 'Unclassified change may indicate undocumented structure drift.',
            }
        ],
    }
    proposals = generate_correction_proposals(drift_report)

    assert proposals['proposal_count'] == 1
    assert proposals['adaptive_invariant_recommendation'] is True
    assert proposals['proposals'][0]['requires_human_approval'] is True
