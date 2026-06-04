from pathlib import Path

import yaml

from federation_runtime.engines.confluence_artifact_pipeline import fixture_artifacts, write_artifacts
from federation_runtime.engines.phase0_orchestration import generate
from federation_runtime.engines.qplant_contractual_ingestion import ingest


def test_confluence_artifact_generation_extracts_structure(tmp_path):
    page = fixture_artifacts("1023934467")
    output_dir = tmp_path / "confluence" / "page_1023934467"
    metadata = write_artifacts(page, output_dir)

    assert (output_dir / "raw_storage.html").exists()
    assert (output_dir / "content.md").exists()
    assert (output_dir / "metadata.yaml").exists()
    assert (output_dir / "links.json").exists()
    assert (output_dir / "attachments.json").exists()
    assert (output_dir / "hierarchy.json").exists()
    assert metadata["structure_counts"]["headings"] >= 2
    assert metadata["structure_counts"]["tables"] == 1
    assert metadata["structure_counts"]["macros"] >= 1


def test_qplant_ingestion_preserves_trace_markers(tmp_path):
    source = tmp_path / "locked_baseline.md"
    source.write_text("1. The Contractor shall preserve source references.\n2. Informational note only.\n", encoding="utf-8")

    manifest = ingest([source], tmp_path / "docs" / "baseline", tmp_path / "docs" / "rtm", tmp_path / "outputs")
    requirements = yaml.safe_load((tmp_path / "docs" / "baseline" / "contractual_baseline_manifest.yaml").read_text())
    rtm = (tmp_path / "docs" / "rtm" / "requirements_traceability_matrix.md").read_text()

    assert manifest["requirement_count"] == 1
    assert requirements["sources"][0]["requirement_count"] == 1
    assert "locked_baseline.md:1" in rtm
    assert "locked_source_not_reinterpreted" in rtm


def test_orchestration_signal_schema(tmp_path):
    task_path, signal_path = generate(tmp_path)
    task_links = yaml.safe_load(Path(task_path).read_text())
    signals = yaml.safe_load(Path(signal_path).read_text())

    assert task_links["task_links"][0]["source_content_id"] == "confluence:ACR:page:1023934467"
    for signal in signals["cross_repo_signals"]:
        assert {"source_content_id", "target_repository", "requested_action", "payload_status", "trace_reference"} <= signal.keys()
