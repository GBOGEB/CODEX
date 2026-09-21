import json
from pathlib import Path

from scripts.refresh_model_package_index import build_index, refresh_index


def test_index_is_deterministic_and_excludes_generated_and_cache_files(tmp_path: Path):
    (tmp_path / "intent_manifest.md").write_text("intent\n", encoding="utf-8")
    nested = tmp_path / "model"
    nested.mkdir()
    (nested / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "ignored.pyc").write_bytes(b"ignored")
    (tmp_path / "index.json").write_text("stale", encoding="utf-8")

    first = build_index(tmp_path)
    first_paths = [entry["path"] for entry in first["entries"]]

    assert first_paths == ["intent_manifest.md", "model/data.csv"]
    assert first["entry_count"] == 2
    assert all(len(entry["sha256"]) == 64 for entry in first["entries"])

    output = refresh_index(tmp_path)
    first_bytes = output.read_bytes()
    refresh_index(tmp_path)
    assert output.read_bytes() == first_bytes

    payload = json.loads(first_bytes)
    assert payload["schema"] == "codex-model-package-index/v1"


def test_custom_index_name_is_excluded(tmp_path: Path):
    (tmp_path / "payload.txt").write_text("x", encoding="utf-8")
    (tmp_path / "manifest-index.json").write_text("old", encoding="utf-8")

    payload = build_index(tmp_path, index_name="manifest-index.json")

    assert [entry["path"] for entry in payload["entries"]] == ["payload.txt"]
