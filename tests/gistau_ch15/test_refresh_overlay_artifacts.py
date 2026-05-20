import json
from pathlib import Path

import pytest

from gistau_ch15.visualization.overlay_artifact_manifest import (
    MANIFEST_SCHEMA_VERSION,
    OverlayArtifactManifestBuilder,
)
from gistau_ch15.visualization.refresh_overlay_artifacts import (
    refresh_overlay_artifacts,
)


def test_refresh_overlay_artifacts_writes_manifest(tmp_path: Path):
    manifest_path = tmp_path / "generated_overlay_manifest.json"

    outputs = refresh_overlay_artifacts(manifest_path)

    assert manifest_path in outputs
    assert manifest_path.exists()

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert payload["artifact_count"] == 2
    assert len(payload["artifacts"]) == 2


def test_overlay_manifest_loader_validates_count(tmp_path: Path):
    manifest_path = tmp_path / "broken_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "artifact_count": 99,
                "artifacts": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="artifact_count"):
        OverlayArtifactManifestBuilder().load_manifest(manifest_path)
