from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / 'outputs' / 'semantic'
PLANNING_REPORT_JSON = OUTPUT_DIR / 'planning_report.json'
PLANNING_REPORT_MD = OUTPUT_DIR / 'planning_report.md'

SEVERITY_WEIGHT = {'error': 3, 'warning': 2, 'note': 1}


def _build_priorities(drift_report: dict, snapshot: dict, proposals: dict) -> list[dict]:
    priorities = []
    for proposal in proposals.get('proposals', []):
        priorities.append(
            {
                'title': proposal.get('recommendation'),
                'source': proposal.get('rule_id'),
                'priority_score': SEVERITY_WEIGHT.get(proposal.get('severity', 'note'), 1),
                'requires_human_approval': True,
            }
        )

    for debt_item in snapshot.get('unresolved_semantic_debt', []):
        priorities.append(
            {
                'title': f'Remediate semantic debt: {debt_item}',
                'source': 'snapshot.unresolved_semantic_debt',
                'priority_score': 1,
                'requires_human_approval': False,
            }
        )

    drift_score = drift_report.get('drift_score', 0)
    for item in priorities:
        item['drift_adjusted_priority'] = item['priority_score'] + drift_score
    priorities.sort(key=lambda item: item['drift_adjusted_priority'], reverse=True)
    return priorities


def _write_human_summary(priorities: list[dict]) -> None:
    lines = ['# Semantic Planning Report', '', '## Prioritized Actions']
    if not priorities:
        lines.append('- No active drift-adjusted priorities.')
    else:
        for item in priorities:
            lines.append(
                f"- ({item['drift_adjusted_priority']}) {item['title']} "
                f"[source: {item['source']}]"
            )
    PLANNING_REPORT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def build_semantic_plan(drift_report: dict, snapshot: dict, proposals: dict) -> dict:
    priorities = _build_priorities(drift_report, snapshot, proposals)
    report = {
        'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'drift_score': drift_report.get('drift_score', 0),
        'debt_status': drift_report.get('debt_status', 'healthy'),
        'priorities': priorities,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLANNING_REPORT_JSON.write_text(json.dumps(report, indent=2), encoding='utf-8')
    _write_human_summary(priorities)
    return report
