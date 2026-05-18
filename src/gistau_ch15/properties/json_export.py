from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonExportWriter:
    """Utility writer for backend comparison artifacts."""

    def __init__(self, output_directory: str = "outputs") -> None:
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def write_json(self, file_name: str, payload: Any) -> Path:
        path = self.output_directory / file_name
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
        return path

    def write_backend_reports(
        self,
        comparison_rows: list[dict[str, Any]],
        summary: dict[str, Any],
        heatmap_matrix: dict[str, Any],
    ) -> list[Path]:
        return [
            self.write_json("backend_comparison_report.json", comparison_rows),
            self.write_json("backend_delta_summary.json", summary),
            self.write_json("backend_heatmap_matrix.json", heatmap_matrix),
        ]
