from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs' / 'hbhs-ep-v8.3-tuplebridge'
RUNTIME = DOCS / 'runtime'

RUNTIME.mkdir(parents=True, exist_ok=True)
(RUNTIME / 'manifests').mkdir(exist_ok=True)
(RUNTIME / 'exports').mkdir(exist_ok=True)
(RUNTIME / 'html').mkdir(exist_ok=True)

index_html = DOCS / 'index.html'

html = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>HBHS-EP TupleBridge Runtime</title>
</head>
<body>
  <h1>HBHS-EP TupleBridge Runtime</h1>
  <p>Wave-1 runtime scaffold operational.</p>
  <ul>
    <li>Runtime folders initialized</li>
    <li>Metrics scaffold initialized</li>
    <li>Pages deployment target initialized</li>
  </ul>
</body>
</html>
'''

index_html.write_text(html, encoding='utf-8')

metrics_path = DOCS / 'runtime-metrics.json'

if metrics_path.exists():
    data = json.loads(metrics_path.read_text(encoding='utf-8'))
    print(json.dumps(data, indent=2))

print('TupleBridge runtime scaffold complete.')
