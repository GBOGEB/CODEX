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
    overlay_seed = tmp_path / "thermo_visual_overlay_seed.json"
    trace_export = tmp_path / "plotly_trace_export.json"

    outputs = refresh_overlay_artifacts(
        manifest_path,
        overlay_seed_output=overlay_seed,
        trace_export_output=trace_export,
        root=tmp_path,
    )

    assert manifest_path in outputs
    assert manifest_path.exists()

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert payload["artifact_count"] == len(payload["artifacts"])
    assert len(payload["artifacts"]) >= 2
    
    # Verify all required paths are present
    artifact_paths = {item["path"] for item in payload["artifacts"]}
    assert "thermo_visual_overlay_seed.json" in artifact_paths
    assert "plotly_trace_export.json" in artifact_paths


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


def test_parse_payload_validates_artifact_types(tmp_path: Path):
    """Test that parse_payload wraps TypeError as ValueError for malformed artifacts."""
    manifest_path = tmp_path / "malformed_manifest.json"
    
    # Test with non-dict artifact
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "artifact_count": 1,
                "artifacts": ["not_a_dict"],
            }
        ),
        encoding="utf-8",
    )
    
    with pytest.raises(ValueError, match="must be a dict"):
        OverlayArtifactManifestBuilder().load_manifest(manifest_path)
    
    # Test with dict missing required fields
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "artifact_count": 1,
                "artifacts": [{"key": "test"}],  # missing path, sha256, size_bytes
            }
        ),
        encoding="utf-8",
    )
    
    with pytest.raises(ValueError, match="invalid fields"):
        OverlayArtifactManifestBuilder().load_manifest(manifest_path)
