from __future__ import annotations

import json
from pathlib import Path

from gistau_ch15.visualization.backend_agreement import (
    BackendAgreementBuilder,
)
from gistau_ch15.visualization.plotly_trace_builder import (
    PlotlyTraceBuilder,
)
from gistau_ch15.visualization.saturation_sampling import (
    FallbackSaturationSampler,
)


OUTPUT = Path("docs/gistau-ch15/data/plotly_trace_export.json")


class PlotlyTraceJSONExporter:
    """Export Plotly-compatible trace JSON for GitHub Pages dashboards."""

    def export(self, output_path: str | Path = OUTPUT) -> Path:
        saturation = FallbackSaturationSampler().sample()
        agreement = BackendAgreementBuilder().build()

        builder = PlotlyTraceBuilder()

        payload = {
            "saturation": builder.saturation_traces(saturation.__dict__),
            "agreement": builder.agreement_trace(
                agreement.backends,
                agreement.tuples,
                agreement.values,
            ),
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

        return path
