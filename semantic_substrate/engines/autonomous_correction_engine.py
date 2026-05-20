from __future__ import annotations


def _proposal_for_finding(finding: dict, index: int) -> dict:
    path = finding.get('path') or 'unknown'
    rule_id = finding.get('rule_id') or 'DRIFT-UNK'
    severity = finding.get('severity', 'note')
    message = finding.get('message', '')
    recommendation = 'Review semantic drift and apply targeted invariant updates.'

    if rule_id == 'DRIFT-002':
        recommendation = f'Add manifest and semantic delta coverage for `{path}`.'
    elif rule_id == 'DRIFT-003':
        recommendation = 'Update branch activity status or capture missing semantic delta entry.'

    return {
        'proposal_id': f'CP-{index:04d}',
        'rule_id': rule_id,
        'severity': severity,
        'target_path': path,
        'recommendation': recommendation,
        'evidence': message,
        'requires_human_approval': True,
    }


def generate_correction_proposals(drift_report: dict) -> dict:
    findings = list(drift_report.get('findings', []))
    proposals = [_proposal_for_finding(item, index + 1) for index, item in enumerate(findings)]
    if not proposals and drift_report.get('debt_status') in {'warning', 'critical'}:
        proposals.append(
            {
                'proposal_id': 'CP-0001',
                'rule_id': 'DRIFT-GENERAL',
                'severity': 'warning',
                'target_path': 'semantic_substrate/invariants.yaml',
                'recommendation': 'Add adaptive invariant guardrails for repeated runtime drift.',
                'evidence': 'Elevated drift debt status detected without classified findings.',
                'requires_human_approval': True,
            }
        )

    return {
        'proposal_count': len(proposals),
        'proposals': proposals,
        'adaptive_invariant_recommendation': bool(proposals),
    }
