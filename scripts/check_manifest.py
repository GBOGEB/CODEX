import json
from pathlib import Path

required = [
    "docs/index.html",
    "docs/dashboard.html",
    "docs/plots/index.html",
]
MAX_ERROR_ENTRIES = 50

manifest = Path("MANIFEST.json")
if not manifest.exists():
    raise SystemExit("MANIFEST.json missing")

obj = json.loads(manifest.read_text(encoding="utf-8"))
if obj.get("canonical_entrypoint") != "docs/index.html":
    raise SystemExit("canonical_entrypoint must be docs/index.html")

published_pages = obj.get("published_pages")
if not isinstance(published_pages, list) or not published_pages:
    raise SystemExit("published_pages must be a non-empty list")

bad_entries = [
    page
    for page in published_pages
    if not isinstance(page, str) or not page.strip() or not page.startswith("docs/")
]
if bad_entries:
    raise SystemExit(
        "published_pages contains invalid entries:\n"
        + "\n".join(p for p in bad_entries[:MAX_ERROR_ENTRIES])
    )

missing_required = [path for path in required if path not in published_pages]
if missing_required:
    raise SystemExit(
        "published_pages missing required entrypoints:\n"
        + "\n".join(missing_required)
    )

seen = set()
duplicate_set = set()
duplicates = []
for page in published_pages:
    if page in seen and page not in duplicate_set:
        duplicates.append(page)
        duplicate_set.add(page)
    seen.add(page)
if duplicates:
    raise SystemExit("published_pages contains duplicates:\n" + "\n".join(duplicates))

for path in required:
    if not Path(path).exists():
        raise SystemExit(f"required path missing: {path}")

print("manifest check passed")
