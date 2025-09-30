from __future__ import annotations

import json
import zipfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.zip_pipeline import ZipPipeline


@pytest.fixture()
def sample_conversations(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / "conversation_a").mkdir(parents=True)
    (source / "conversation_a" / "metadata.json").write_text("{\"title\": \"A\"}")
    (source / "conversation_a" / "transcript.txt").write_text("hello A")

    (source / "conversation_b" / "notes").mkdir(parents=True)
    (source / "conversation_b" / "notes" / "summary.md").write_text("# Summary\nB")
    return source


def test_pipeline_creates_archives_and_manifest(sample_conversations: Path, tmp_path: Path) -> None:
    output = tmp_path / "output"
    pipeline = ZipPipeline(
        source_root=sample_conversations,
        output_root=output,
        dataset_name="handover_final",
        manifest_name="conversations_manifest.json",
    )

    manifest_path = pipeline.run()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text())
    assert manifest["dataset"] == "handover_final"
    assert manifest["entries"]
    assert {entry["conversation_id"] for entry in manifest["entries"]} == {"conversation_a", "conversation_b"}

    # Verify archive metadata matches filesystem state
    for entry in manifest["entries"]:
        archive_path = manifest_path.parent / entry["zip_path"]
        assert archive_path.exists()
        assert entry["sha256"] == ZipPipeline.compute_file_hash(archive_path)
        with zipfile.ZipFile(archive_path) as zf:
            archived_files = sorted(zf.namelist())
        if entry["conversation_id"] == "conversation_a":
            assert archived_files == ["metadata.json", "transcript.txt"]
        else:
            assert archived_files == ["notes/summary.md"]


def test_global_index_builds_summary(sample_conversations: Path, tmp_path: Path) -> None:
    output = tmp_path / "output"
    pipeline = ZipPipeline(sample_conversations, output, "handover_final")
    manifest_path = pipeline.run()

    index_path = tmp_path / "GLOBAL_index.json"
    index = ZipPipeline.build_global_index([manifest_path], index_path)

    assert index_path.exists()
    assert index["datasets"][0]["dataset"] == "handover_final"
    assert index["datasets"][0]["entry_count"] == 2


def test_build_index_script(sample_conversations: Path, tmp_path: Path) -> None:
    output = tmp_path / "output"
    index_path = tmp_path / "GLOBAL_index.json"

    argv = [
        "--source",
        str(sample_conversations),
        "--output",
        str(output),
        "--dataset-name",
        "handover_final",
        "--index-path",
        str(index_path),
    ]

    from scripts import build_index

    assert build_index.main(argv) == 0
    assert index_path.exists()
