import json
from pathlib import Path

manifest = json.loads(Path('MANIFEST.json').read_text(encoding='utf-8'))
published = manifest.get('published_pages', [])

seen = set()
duplicates = []
for page in published:
    if page in seen and page not in duplicates:
        duplicates.append(page)
    seen.add(page)
if duplicates:
    raise SystemExit('Duplicate published pages in manifest:\n' + '\n'.join(duplicates))

missing = [p for p in published if not Path(p).exists()]
if missing:
    raise SystemExit('Missing published pages from manifest:\n' + '\n'.join(missing))

published_html = {Path(p).as_posix() for p in published}
deployed_html = sorted(path.as_posix() for path in Path('docs').rglob('*.html'))
orphaned = [path for path in deployed_html if path not in published_html]
if orphaned:
    raise SystemExit('Untracked deployed HTML pages under docs/:\n' + '\n'.join(orphaned))

print('stale check passed')
