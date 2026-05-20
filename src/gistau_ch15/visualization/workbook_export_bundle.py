from __future__ import annotations

import json
from pathlib import Path


class WorkbookExportBundle:
    """Workbook-ready export bundle scaffold."""

    def export(self, output_dir: str | Path) -> list[Path]:
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)

        manifest = {
            "bundle": "workbook-ready",
            "status": "scaffold",
            "artifacts": [
                "backend comparison",
                "plotly traces",
                "publication exports",
            ],
        }

        manifest_path = root / "workbook_bundle_manifest.json"

        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        return [manifest_path]
