from __future__ import annotations

from pathlib import Path

from gistau_ch15.visualization.overlay_artifact_manifest import (
    OverlayArtifactManifestBuilder,
)
from gistau_ch15.visualization.pages_artifact_refresh import (
    PagesArtifactRefresh,
)

MANIFEST_OUTPUT = Path("docs/gistau-ch15/data/generated_overlay_manifest.json")


def refresh_overlay_artifacts(
    manifest_output: str | Path = MANIFEST_OUTPUT,
    *,
    root: Path | None = None,
    overlay_output: Path | None = None,
    trace_output: Path | None = None,
) -> list[Path]:
    """Refresh Pages artifacts and regenerate generated overlay manifest.
    
    Args:
        manifest_output: Path where the manifest JSON will be written.
        root: Base directory for computing relative paths in the manifest.
              Defaults to the repository root (parent of docs/).
        overlay_output: Optional path for thermo_visual_overlay_seed.json
        trace_output: Optional path for plotly_trace_export.json
    """
    if root is None:
        # Default to repo root (parent of docs/) for stable relative paths
        root = Path(__file__).resolve().parent.parent.parent.parent

    artifacts = PagesArtifactRefresh().refresh(
        overlay_output=overlay_output,
        trace_output=trace_output,
    )
    manifest = OverlayArtifactManifestBuilder().write_manifest(
        artifacts,
        manifest_output,
        root=root,
    )
    return [*artifacts, manifest]
