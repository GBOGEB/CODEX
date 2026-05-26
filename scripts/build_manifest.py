#!/usr/bin/env python3
"""Build minimal bootstrap manifest."""
from pathlib import Path
import json

OUT = Path("reports/bootstrap_manifest.json")


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "wave": "W000",
        "governance": "governance/runtime_governance.yml",
        "docs": ["docs/runtime_map.md", "docs/federation_map.md", "docs/governance_states.md"],
    }
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
