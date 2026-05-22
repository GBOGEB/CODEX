from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge'
TOPOLOGY = DOCS / 'runtime_topology.json'
OUTPUT = DOCS / 'runtime_summary.md'

summary = ['# Runtime Summary', '']

if TOPOLOGY.exists():
    data = json.loads(TOPOLOGY.read_text(encoding='utf-8'))

    summary.append(f"Root Node: {data['root']}")
    summary.append('')
    summary.append('## Nodes')

    for node in data['nodes']:
        summary.append(f"- {node['id']} :: {node['status']}")

OUTPUT.write_text('\n'.join(summary), encoding='utf-8')

print('Runtime dashboard summary generated.')
