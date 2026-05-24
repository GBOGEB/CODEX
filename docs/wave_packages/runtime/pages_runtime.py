from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_FILES = [
    'docs/wave_packages/runtime/out/runtime_status.md',
    'docs/wave_packages/runtime/pages/index.html',
    'docs/wave_packages/runtime/pages/plotly_runtime_dashboard.html',
    'docs/wave_packages/runtime/out/topology_runtime.mmd',
]

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>Runtime Pages Bundle</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; }
li { margin-bottom: 0.5rem; }
</style>
</head>
<body>
<h1>Runtime Federation Pages Bundle</h1>
<p>Generated: {timestamp}</p>
<ul>
{items}
</ul>
</body>
</html>
"""


def build_index(runtime_files):
    items = []
    for item in runtime_files:
        name = Path(item).name
        items.append(f'<li><a href="../{item}">{name}</a></li>')
    return '\n'.join(items)


def main():
    parser = argparse.ArgumentParser(description='Generate runtime Pages bundle')
    parser.add_argument('--out', default='docs/wave_packages/runtime/pages/runtime_bundle_index.html')
    args = parser.parse_args()

    html = INDEX_TEMPLATE.format(
        timestamp=datetime.now(timezone.utc).isoformat(),
        items=build_index(RUNTIME_FILES),
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')

    manifest = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': 'pages-runtime-generated',
        'runtime_files': RUNTIME_FILES,
        'bundle_size': len(RUNTIME_FILES),
    }

    manifest_path = out.with_suffix('.json')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
