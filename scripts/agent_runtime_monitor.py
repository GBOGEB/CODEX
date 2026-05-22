from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / 'agent_runtime' / 'agent_metrics.json'
OUTPUT = ROOT / 'agent_runtime' / 'agent_runtime_report.md'

report = ['# Agent Runtime Report', '']

if METRICS.exists():
    data = json.loads(METRICS.read_text(encoding='utf-8'))

    report.append(f"Wave: {data['wave']}")
    report.append(f"Completion: {data['completion_percent']}%")
    report.append('')
    report.append('## Agent Metrics')

    for name, score in data['agents'].items():
        report.append(f"- {name}: {score}")

OUTPUT.write_text('\n'.join(report), encoding='utf-8')

print('Agent runtime monitoring scaffold complete.')
