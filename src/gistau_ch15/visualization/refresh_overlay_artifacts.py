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
) -> list[Path]:
    """Refresh Pages artifacts and regenerate generated overlay manifest."""

    artifacts = PagesArtifactRefresh().refresh()
    manifest = OverlayArtifactManifestBuilder().write_manifest(
        artifacts,
        manifest_output,
    )
    return [*artifacts, manifest]
