from pathlib import Path
import json
import sys


def main():
    """Generate runtime dashboard summary from topology JSON."""
    ROOT = Path(__file__).resolve().parents[1]
    DOCS = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge'
    TOPOLOGY = DOCS / 'runtime_topology.json'
    OUTPUT = DOCS / 'runtime_summary.md'

    summary = ['# Runtime Summary', '']

    if not TOPOLOGY.exists():
        print(f"Warning: Topology file not found at {TOPOLOGY}", file=sys.stderr)
        OUTPUT.write_text('\n'.join(summary), encoding='utf-8')
        return

    try:
        data = json.loads(TOPOLOGY.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {TOPOLOGY}: {e}", file=sys.stderr)
        sys.exit(1)
    except (IOError, OSError) as e:
        print(f"Error reading {TOPOLOGY}: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate schema
    if 'root' not in data:
        print(f"Error: Missing 'root' key in {TOPOLOGY}", file=sys.stderr)
        sys.exit(1)
    if 'nodes' not in data:
        print(f"Error: Missing 'nodes' key in {TOPOLOGY}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data['nodes'], list):
        print(f"Error: 'nodes' must be a list in {TOPOLOGY}", file=sys.stderr)
        sys.exit(1)

    summary.append(f"Root Node: {data['root']}")
    summary.append('')
    summary.append('## Nodes')

    for node in data['nodes']:
        if not isinstance(node, dict):
            print(f"Warning: Skipping invalid node (not a dict): {node}", file=sys.stderr)
            continue
        if 'id' not in node or 'status' not in node:
            print(f"Warning: Skipping node missing 'id' or 'status': {node}", file=sys.stderr)
            continue
        summary.append(f"- {node['id']} :: {node['status']}")

    OUTPUT.write_text('\n'.join(summary), encoding='utf-8')
    print('Runtime dashboard summary generated.')


if __name__ == '__main__':
    main()
