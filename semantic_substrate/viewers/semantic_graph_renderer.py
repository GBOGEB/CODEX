from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
BRANCH_DAG = ROOT / 'semantic_substrate' / 'branch_dag.yaml'


def load_branches():
    with open(BRANCH_DAG, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def render_ascii_graph(branches):
    lines = ['CODEX Semantic Graph']

    for branch in branches.get('branches', []):
        parent = branch.get('parent')
        node = branch.get('id')
        lines.append(f'- {parent} -> {node}')

    return '\n'.join(lines)


if __name__ == '__main__':
    data = load_branches()
    print(render_ascii_graph(data))
