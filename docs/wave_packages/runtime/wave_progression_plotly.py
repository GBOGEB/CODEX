from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs' / 'wave_packages' / 'runtime' / 'out'

WAVES = {
    'A66': 72,
    'A67': 88,
    'A68': 91,
    'A69': 93,
    'A70': 95,
    'A71': 94,
    'A72': 96,
    'A73': 92,
    'A74': 95,
    'A75': 94,
    'A76': 90,
    'A77': 91,
    'A78': 94,
    'A79': 96,
    'A80': 97,
    'A81': 97,
    'A82': 98,
    'A83': 98,
    'A84': 99,
    'A85': 99,
}

HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Wave Progression Animation</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
</head>
<body>
<div id="wave_progression" style="width:100%;height:700px;"></div>
<script>
const waves = %WAVES%;
const x = Object.keys(waves);
const y = Object.values(waves);
const frames = x.map((wave, idx) => ({
  name: wave,
  data: [{
    x: x.slice(0, idx + 1),
    y: y.slice(0, idx + 1),
    type: 'scatter',
    mode: 'lines+markers'
  }]
}));
Plotly.newPlot('wave_progression', [{x:[x[0]], y:[y[0]], type:'scatter', mode:'lines+markers'}], {
  title:'Federation Wave Progression',
  xaxis:{title:'Wave'},
  yaxis:{title:'Completion %', range:[60,100]},
  updatemenus:[{type:'buttons', buttons:[{label:'Play', method:'animate', args:[null]}]}]
}).then(() => Plotly.addFrames('wave_progression', frames));
</script>
</body>
</html>
'''


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    html = HTML.replace('%WAVES%', json.dumps(WAVES))
    (OUT / 'wave_progression_animation.html').write_text(html, encoding='utf-8')
    (OUT / 'wave_progression_stats.json').write_text(json.dumps(WAVES, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'wave_count': len(WAVES)}, indent=2))
