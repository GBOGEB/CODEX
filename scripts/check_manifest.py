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

for path in required:
    if not Path(path).exists():
        raise SystemExit(f"required path missing: {path}")

print("manifest check passed")
