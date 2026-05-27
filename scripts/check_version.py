import json
from pathlib import Path

version_path = Path("VERSION.json")

try:
    version = json.loads(version_path.read_text(encoding="utf-8"))
except FileNotFoundError as exc:
    raise SystemExit("VERSION.json missing") from exc
except json.JSONDecodeError as exc:
    raise SystemExit(f"VERSION.json is not valid JSON: {exc}") from exc

required = ("version", "generated_at", "git")
missing = [key for key in required if key not in version]
non_string = [key for key in required if key in version and not isinstance(version[key], str)]
blank = [key for key in required if key in version and isinstance(version[key], str) and not version[key].strip()]

if missing:
    raise SystemExit("VERSION.json missing required values: " + ", ".join(missing))
if non_string:
    raise SystemExit("VERSION.json fields must be strings: " + ", ".join(non_string))
if blank:
    raise SystemExit("VERSION.json fields must be non-empty: " + ", ".join(blank))

for key in required:
    print(f"{key}={version[key]}")
