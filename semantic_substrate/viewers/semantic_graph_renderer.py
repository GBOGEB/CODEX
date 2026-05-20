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


def render_html_graph(branches):
    edges = []
    for branch in branches.get('branches', []):
        parent = branch.get('parent') or '∅'
        node = branch.get('id')
        title = branch.get('title', '')
        edges.append(f'<li><strong>{parent}</strong> → <strong>{node}</strong> <em>{title}</em></li>')
    body = '\n'.join(edges)
    return (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>CODEX Semantic Graph</title></head>\n'
        '<body>\n'
        '<h1>CODEX Semantic Graph</h1>\n'
        '<ul>\n'
        f'{body}\n'
        '</ul>\n'
        '</body>\n'
        '</html>\n'
    )


def write_html_graph(output_path: Path):
    data = load_branches()
    rendered = render_html_graph(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding='utf-8')
    return output_path


if __name__ == '__main__':
    data = load_branches()
    print(render_ascii_graph(data))
