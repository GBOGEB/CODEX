from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / 'codex_abac_federation' / 'federation_topology.json'
OUTPUT = ROOT / 'codex_abac_federation' / 'federation_sync_report.md'

report = ['# Federation Synchronization Report', '']

if FEDERATION.exists():
    data = json.loads(FEDERATION.read_text(encoding='utf-8'))

    report.append(f"Federation: {data['federation']}")
    report.append('')
    report.append('## Repository Roles')

    for repo in data['repositories']:
        report.append(f"- {repo['id']} :: {repo['role']}")

OUTPUT.write_text('\n'.join(report), encoding='utf-8')

print('Federation synchronization scaffold complete.')
