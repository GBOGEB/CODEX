from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / 'agent_runtime' / 'agent_metrics.json'
OUTPUT = ROOT / 'outputs' / 'agent_runtime_report.md'

def write_error_report(error_message):
    """Write an error report when metrics cannot be loaded."""
    error_report = [
        '# Agent Runtime Report',
        '',
        '## Error',
        '',
        f'⚠️ Unable to generate report: {error_message}',
        '',
        f'**Metrics file:** `{METRICS}`',
        '',
        '### Required fields',
        '',
        '- `wave` (string)',
        '- `completion_percent` (number)',
        '- `agents` (object with agent completion percentages)',
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(error_report), encoding='utf-8')

report = ['# Agent Runtime Report', '']

if not METRICS.exists():
    error_msg = f"Metrics file not found at {METRICS}"
    write_error_report(error_msg)
    sys.exit(f"Error: {error_msg}")

try:
    data = json.loads(METRICS.read_text(encoding='utf-8'))
except json.JSONDecodeError as e:
    error_msg = f"Invalid JSON in {METRICS}: {e}"
    write_error_report(error_msg)
    sys.exit(f"Error: {error_msg}")

# Validate required fields
required_fields = ['wave', 'completion_percent', 'agents']
missing_fields = [field for field in required_fields if field not in data]
if missing_fields:
    error_msg = f"Missing required fields: {', '.join(missing_fields)}"
    write_error_report(error_msg)
    sys.exit(f"Error: {error_msg}")

# Validate agents is a dict
if not isinstance(data.get('agents'), dict):
    error_msg = "'agents' field must be a dictionary"
    write_error_report(error_msg)
    sys.exit(f"Error: {error_msg}")

report.append(f"Wave: {data['wave']}")
report.append(f"Completion: {data['completion_percent']}%")
report.append('')
report.append('## Agent Metrics')

for name, score in data['agents'].items():
    report.append(f"- {name}: {score}%")

# Ensure output directory exists
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(report), encoding='utf-8')

print('Agent runtime monitoring scaffold complete.')
