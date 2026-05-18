from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'


def load_branch_dag():
    with open(SEMANTIC / 'branch_dag.yaml', 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def render_mermaid():
    dag = load_branch_dag()

    lines = ['graph TD']

    for branch in dag.get('branches', []):
        parent = branch.get('parent')
        node = branch.get('id')

        if parent:
            lines.append(f'    {parent} --> {node}')
        else:
            lines.append(f'    {node}')

    return '\n'.join(lines)


if __name__ == '__main__':
    print(render_mermaid())
