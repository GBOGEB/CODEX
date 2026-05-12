import json
from fnmatch import fnmatch
from pathlib import Path

PLOT_HTML_PREFIX = "docs/plots/"

manifest = json.loads(Path("MANIFEST.json").read_text(encoding="utf-8"))
published = manifest.get("published_pages", [])
if not isinstance(published, list) or not published:
    raise SystemExit("published_pages must be a non-empty list")

deployed_html = sorted(
    str(path).replace("\\", "/")
    for path in Path("docs").rglob("*.html")
)

tracked_html = set()
missing = []
for pattern in published:
    pattern_matches = [path for path in deployed_html if fnmatch(path, pattern)]
    if not pattern_matches:
        missing.append(pattern)
    tracked_html.update(pattern_matches)

orphan_html = [path for path in deployed_html if path not in tracked_html]
stale_plot_html = [path for path in orphan_html if path.startswith(PLOT_HTML_PREFIX)]

duplicate_dashboards = [
    path
    for path in deployed_html
    if path != "docs/dashboard.html" and Path(path).name.startswith("dashboard")
]

errors = []
if missing:
    errors.append("Missing published pages from manifest:\n" + "\n".join(missing))
if orphan_html:
    errors.append("Untracked public entrypoints under docs/:\n" + "\n".join(orphan_html))
if stale_plot_html:
    errors.append("Stale plot HTML files under docs/plots/:\n" + "\n".join(stale_plot_html))
if duplicate_dashboards:
    errors.append(
        "Duplicate canonical dashboard files detected:\n" + "\n".join(duplicate_dashboards)
    )

if errors:
    raise SystemExit("\n\n".join(errors))

print("stale check passed")
