from __future__ import annotations

from pathlib import Path

from gistau_ch15.visualization.regenerate_overlay_json import regenerate
from gistau_ch15.visualization.trace_json_export import (
    PlotlyTraceJSONExporter,
)


class PagesArtifactRefresh:
    """Refresh GitHub Pages-visible visualization artifacts."""

    def refresh(
        self,
        *,
        overlay_seed_output: str | Path | None = None,
        trace_export_output: str | Path | None = None,
    ) -> list[Path]:
        outputs: list[Path] = []

        if overlay_seed_output is not None:
            outputs.append(regenerate(overlay_seed_output))
        else:
            outputs.append(regenerate())

        if trace_export_output is not None:
            outputs.append(PlotlyTraceJSONExporter().export(trace_export_output))
        else:
            outputs.append(PlotlyTraceJSONExporter().export())

        return outputs
