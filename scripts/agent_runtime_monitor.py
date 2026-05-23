from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / 'agent_runtime' / 'agent_metrics.json'
OUTPUT = ROOT / 'outputs' / 'agent_runtime_report.md'

report = ['# Agent Runtime Report', '']

if not METRICS.exists():
    sys.exit(f"Error: Metrics file not found at {METRICS}")

try:
    data = json.loads(METRICS.read_text(encoding='utf-8'))
except json.JSONDecodeError as e:
    sys.exit(f"Error: Invalid JSON in {METRICS}: {e}")

# Validate required fields
required_fields = ['wave', 'completion_percent', 'agents']
missing_fields = [field for field in required_fields if field not in data]
if missing_fields:
    sys.exit(f"Error: Missing required fields in {METRICS}: {', '.join(missing_fields)}")

# Validate agents is a dict
if not isinstance(data.get('agents'), dict):
    sys.exit(f"Error: 'agents' field must be a dictionary in {METRICS}")

report.append(f"Wave: {data['wave']}")
report.append(f"Completion: {data['completion_percent']}%")
report.append('')
report.append('## Agent Metrics')

for name, score in data['agents'].items():
    report.append(f"- {name}: {score}")

# Ensure output directory exists
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(report), encoding='utf-8')

print('Agent runtime monitoring scaffold complete.')
