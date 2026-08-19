from __future__ import annotations

from pathlib import Path
from typing import Optional

from gistau_ch15.visualization.regenerate_overlay_json import regenerate
from gistau_ch15.visualization.trace_json_export import PlotlyTraceJSONExporter


class PagesArtifactRefresh:
    """Refresh GitHub Pages-visible visualization artifacts."""

    def refresh(
        self,
        *,
        overlay_output: Optional[Path] = None,
        trace_output: Optional[Path] = None,
    ) -> list[Path]:
        """Refresh artifacts, optionally redirecting outputs.

        Args:
            overlay_output: Optional path for thermo_visual_overlay_seed.json.
            trace_output: Optional path for plotly_trace_export.json.
        """
        outputs: list[Path] = []

        if overlay_output is not None:
            outputs.append(regenerate(overlay_output))
        else:
            outputs.append(regenerate())

        exporter = PlotlyTraceJSONExporter()
        if trace_output is not None:
            outputs.append(exporter.export(trace_output))
        else:
            outputs.append(exporter.export())

        return outputs
