from pathlib import Path

from gistau_ch15.visualization.refresh_overlay_artifacts import (
    refresh_overlay_artifacts,
)


def test_refresh_overlay_artifacts_writes_manifest(tmp_path: Path):
    manifest_path = tmp_path / "generated_overlay_manifest.json"

    outputs = refresh_overlay_artifacts(manifest_path)

    assert manifest_path in outputs
    assert manifest_path.exists()

    payload = manifest_path.read_text(encoding="utf-8")
    assert '"schema_version": "1.0"' in payload
    assert '"artifact_count": 2' in payload
