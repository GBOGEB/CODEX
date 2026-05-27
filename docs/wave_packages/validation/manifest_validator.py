"""Manifest validation runtime for A66/A67 continuity.

This validator is intentionally lightweight so it can run in local development,
GitHub Actions, or CODEX bridge execution without external dependencies.
"""

from __future__ import annotations

import json
from pathlib import Path


class ManifestValidationError(RuntimeError):
    """Raised when manifest validation fails."""


REQUIRED_KEYS = [
    "canonical_entrypoint",
    "published_pages",
    "controls",
    "promotion_rules",
]


def validate_manifest(manifest_path: str | Path = "MANIFEST.json") -> dict:
    path = Path(manifest_path)
    if not path.exists():
        raise ManifestValidationError(f"Manifest file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    missing_keys = [key for key in REQUIRED_KEYS if key not in data]
    if missing_keys:
        raise ManifestValidationError(
            f"Manifest missing required keys: {', '.join(missing_keys)}"
        )

    missing_paths = []
    for entry in data.get("published_pages", []):
        if "*" in entry or "<" in entry:
            continue
        if not Path(entry).exists():
            missing_paths.append(entry)

    result = {
        "status": "ok" if not missing_paths else "warning",
        "missing_paths": missing_paths,
        "published_page_count": len(data.get("published_pages", [])),
    }

    return result


if __name__ == "__main__":
    report = validate_manifest()
    print(json.dumps(report, indent=2))
