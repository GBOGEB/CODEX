from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>Runtime Federation Dashboard</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; }
.tile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
.tile { border: 1px solid #ccc; border-radius: 8px; padding: 1rem; }
.score { font-size: 2rem; font-weight: bold; }
pre { white-space: pre-wrap; }
</style>
</head>
<body>
<h1>Runtime Federation Dashboard</h1>
<p>Generated starter-pack dashboard for rapid execution continuity.</p>
<div class=\"tile-grid\">{tiles}</div>
<h2>Rendered Markdown</h2>
<pre>{markdown}</pre>
</body>
</html>
"""


def extract_tiles(markdown: str):
    tiles = []
    for line in markdown.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) == 3 and parts[0] != "Domain":
                tiles.append(parts)
    return tiles


def render_html(markdown: str) -> str:
    tile_html = []
    for domain, status, score in extract_tiles(markdown):
        tile_html.append(
            f"<div class='tile'><h3>{escape(domain)}</h3><p>{escape(status)}</p><div class='score'>{escape(score)}</div></div>"
        )

    return HTML_TEMPLATE.format(
        tiles="".join(tile_html),
        markdown=escape(markdown),
    )


def main():
    parser = argparse.ArgumentParser(description="Render HTML runtime dashboard")
    parser.add_argument("--input", default="docs/wave_packages/runtime/out/runtime_status.md")
    parser.add_argument("--out", default="docs/wave_packages/runtime/pages/index.html")
    args = parser.parse_args()

    markdown = Path(args.input).read_text(encoding="utf-8")
    html = render_html(markdown)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print(f"Rendered HTML dashboard -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
