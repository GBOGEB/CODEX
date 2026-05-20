import json
from pathlib import Path

from gistau_ch15.visualization.refresh_overlay_artifacts import (
    refresh_overlay_artifacts,
)


def test_refresh_overlay_artifacts_writes_manifest(tmp_path: Path):
    # Redirect all outputs to tmp_path
    overlay_output = tmp_path / "thermo_visual_overlay_seed.json"
    trace_output = tmp_path / "plotly_trace_export.json"
    manifest_path = tmp_path / "generated_overlay_manifest.json"

    outputs = refresh_overlay_artifacts(
        manifest_path,
        root=tmp_path,
        overlay_output=overlay_output,
        trace_output=trace_output,
    )

    # Verify manifest is in outputs and exists
    assert manifest_path in outputs
    assert manifest_path.exists()

    # Parse and validate manifest structure
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1.0"

    # Derive expected count from refreshed artifacts (manifest excluded)
    expected_artifact_count = len([p for p in outputs if p != manifest_path])
    assert manifest["artifact_count"] == expected_artifact_count

    # Verify artifacts list structure
    assert "artifacts" in manifest
    assert len(manifest["artifacts"]) == expected_artifact_count

    # Verify each artifact has required fields
    for artifact in manifest["artifacts"]:
        assert "key" in artifact
        assert "path" in artifact
        assert "sha256" in artifact
        assert "size_bytes" in artifact


def test_refresh_overlay_artifacts_default_paths_are_root_relative(tmp_path: Path):
    outputs = refresh_overlay_artifacts(root=tmp_path)

    overlay_output = tmp_path / "docs/gistau-ch15/data/thermo_visual_overlay_seed.json"
    trace_output = tmp_path / "docs/gistau-ch15/data/plotly_trace_export.json"
    manifest_path = tmp_path / "docs/gistau-ch15/data/generated_overlay_manifest.json"
    assert outputs == [overlay_output, trace_output, manifest_path]
    assert all(path.exists() for path in outputs)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_count"] == 2
    assert {item["path"] for item in manifest["artifacts"]} == {
        "docs/gistau-ch15/data/thermo_visual_overlay_seed.json",
        "docs/gistau-ch15/data/plotly_trace_export.json",
    }
