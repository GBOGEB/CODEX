from __future__ import annotations

from pathlib import Path

from gistau_ch15.visualization.overlay_artifact_manifest import (
    MANIFEST_SCHEMA_VERSION,
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
    manifest_builder = OverlayArtifactManifestBuilder()
    manifest = manifest_builder.write_manifest(artifacts, manifest_output)
    loaded = manifest_builder.load_manifest(manifest)
    if loaded.schema_version != MANIFEST_SCHEMA_VERSION:
        raise ValueError("Unexpected manifest schema version after refresh")
    return [*artifacts, manifest]
