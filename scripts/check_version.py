import json
from pathlib import Path

version = json.loads(Path("VERSION.json").read_text(encoding="utf-8"))
required = ("version", "generated_at", "git")
missing = [key for key in required if not str(version.get(key, "")).strip()]

if missing:
    raise SystemExit("VERSION.json missing required values: " + ", ".join(missing))

for key in required:
    print(f"{key}={version[key]}")
