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
    overlay_seed_output: str | Path | None = None,
    trace_export_output: str | Path | None = None,
    root: Path | None = None,
) -> list[Path]:
    """Refresh Pages artifacts and regenerate generated overlay manifest."""

    artifacts = PagesArtifactRefresh().refresh(
        overlay_seed_output=overlay_seed_output,
        trace_export_output=trace_export_output,
    )
    manifest_builder = OverlayArtifactManifestBuilder()
    manifest = manifest_builder.write_manifest(artifacts, manifest_output, root=root)
    manifest_builder.load_manifest(manifest)
    return [*artifacts, manifest]
