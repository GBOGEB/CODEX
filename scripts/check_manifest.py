import json
from pathlib import Path

required = [
    "docs/index.html",
    "docs/dashboard.html",
    "docs/plots/index.html",
]

manifest = Path("MANIFEST.json")
if not manifest.exists():
    raise SystemExit("MANIFEST.json missing")

obj = json.loads(manifest.read_text(encoding="utf-8"))
if obj.get("canonical_entrypoint") != "docs/index.html":
    raise SystemExit("canonical_entrypoint must be docs/index.html")

published_pages = obj.get("published_pages")
if not isinstance(published_pages, list) or not published_pages:
    raise SystemExit("published_pages must be a non-empty list")

non_string_pages = [page for page in published_pages if not isinstance(page, str)]
if non_string_pages:
    raise SystemExit("published_pages must contain only string paths")

missing_required_pages = [path for path in required if path not in published_pages]
if missing_required_pages:
    raise SystemExit(
        "published_pages missing required entrypoints: "
        + ", ".join(missing_required_pages)
    )

for path in required:
    if not Path(path).exists():
        raise SystemExit(f"required path missing: {path}")

print("manifest check passed")
