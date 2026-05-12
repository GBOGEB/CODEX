import json
from pathlib import Path

manifest = json.loads(Path('MANIFEST.json').read_text(encoding='utf-8'))
published = set(manifest.get('published_pages', []))
missing = [p for p in published if not Path(p).exists()]
if missing:
    raise SystemExit('Missing published pages from manifest:\n' + '\n'.join(missing))

print('stale check passed')
