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
        overlay_output: Path | None = None,
        trace_output: Path | None = None,
    ) -> list[Path]:
        """Refresh artifacts, optionally redirecting outputs.

        Args:
            overlay_output: Optional path for thermo_visual_overlay_seed.json
            trace_output: Optional path for plotly_trace_export.json
        """
        outputs: list[Path] = []

        if overlay_output is not None:
            outputs.append(regenerate(overlay_output))
        else:
            outputs.append(regenerate())

        if trace_output is not None:
            outputs.append(PlotlyTraceJSONExporter().export(trace_output))
        else:
            outputs.append(PlotlyTraceJSONExporter().export())

        return outputs
