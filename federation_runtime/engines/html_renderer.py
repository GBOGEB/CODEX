#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
(r/'dist').mkdir(exist_ok=True)
(r/'dist'/'index.html').write_text('<!doctype html><html><body><h1>Governed Semantic Federation Runtime</h1></body></html>', encoding='utf-8')
print('html rendered')
