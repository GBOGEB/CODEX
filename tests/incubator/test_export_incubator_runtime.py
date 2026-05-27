"""Tests for export_incubator_runtime.py utility."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.export_incubator_runtime import export_incubator_runtime


def test_export_incubator_runtime(tmp_path):
    """Export utility should copy expected incubator artifacts."""
    export_dir = tmp_path / "incubator_export"
    result = export_incubator_runtime(REPO_ROOT, export_dir)

    assert result == export_dir
    assert (export_dir / "incubator" / "session_tuple_schema.yml").exists()
    assert (
        export_dir
        / "incubator"
        / "26_W22_12_35__INCUBATOR__RUNTIME_GOVERNANCE__CHAT_TUPLE_INGRESS_MAPPING__W000.yml"
    ).exists()
    assert (export_dir / "maps" / "repo_ingress_map.yml").exists()
    assert (export_dir / "scripts" / "parse_chat_tuple.py").exists()
    assert (export_dir / "docs" / "incubator_index.md").exists()
    assert (export_dir / "docs" / "INCUBATOR_ABACUS_BRIDGE.md").exists()

    metadata = (export_dir / "EXPORT_METADATA.txt").read_text(encoding="utf-8")
    assert "Tuple count validated pre-export" in metadata
    assert "scripts/export_abacus_runtime.py" in metadata
