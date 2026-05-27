from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.federation.schema_validation import validate_repository_ssot


if __name__ == "__main__":
    errors = validate_repository_ssot(ROOT)
    if errors:
        raise SystemExit("SSOT schema validation failed:\n" + "\n".join(errors))
    print("SSOT schema validation passed")
