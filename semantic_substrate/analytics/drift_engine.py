from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
DRIFT_RULES = ROOT / 'semantic_substrate' / 'analytics' / 'drift_rules.yaml'
DEBT_MODEL = ROOT / 'semantic_substrate' / 'analytics' / 'semantic_debt_score.yaml'
BRANCH_DAG = ROOT / 'semantic_substrate' / 'branch_dag.yaml'


def _load_yaml(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def evaluate_semantic_drift(delta: dict, branch_dag_path: Path = BRANCH_DAG) -> dict:
    rules = _load_yaml(DRIFT_RULES)
    debt_model = _load_yaml(DEBT_MODEL)
    branches = _load_yaml(branch_dag_path).get('branches', [])

    findings = []
    for file_record in delta.get('files', []):
        if file_record.get('classification') == 'unknown':
            findings.append(
                {
                    'rule_id': 'DRIFT-002',
                    'severity': 'warning',
                    'path': file_record.get('path'),
                    'message': 'Unclassified change may indicate undocumented structure drift.',
                }
            )

    stale_candidates = [
        item.get('id')
        for item in branches
        if item.get('status') == 'active' and item.get('id') != 'ROOT'
    ]
    if stale_candidates and not delta.get('files'):
        findings.append(
            {
                'rule_id': 'DRIFT-003',
                'severity': 'warning',
                'path': 'semantic_substrate/branch_dag.yaml',
                'message': 'Active branches found with no semantic delta file activity.',
            }
        )

    severity_weights = {'error': 2, 'warning': 1, 'note': 0}
    drift_score = sum(severity_weights.get(item.get('severity', 'note'), 0) for item in findings)
    debt_thresholds = debt_model.get('semantic_debt', {}).get('thresholds', {})
    status = 'healthy'
    if drift_score >= debt_thresholds.get('critical', {}).get('min_score', 26):
        status = 'critical'
    elif drift_score >= debt_thresholds.get('warning', {}).get('min_score', 11):
        status = 'warning'

    return {
        'rules_version': rules.get('version', '0.1.0'),
        'finding_count': len(findings),
        'findings': findings,
        'drift_score': drift_score,
        'debt_status': status,
    }
