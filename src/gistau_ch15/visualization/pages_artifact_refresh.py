from __future__ import annotations

from pathlib import Path

from gistau_ch15.visualization.regenerate_overlay_json import regenerate
from gistau_ch15.visualization.trace_json_export import (
    PlotlyTraceJSONExporter,
)


class PagesArtifactRefresh:
    """Refresh GitHub Pages-visible visualization artifacts."""

    def refresh(self) -> list[Path]:
        outputs: list[Path] = []

        outputs.append(regenerate())
        outputs.append(PlotlyTraceJSONExporter().export())

        return outputs
