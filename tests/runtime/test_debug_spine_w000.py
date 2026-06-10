from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEBUG_SPINE_DIR = ROOT / "abacus_runtime" / "debug_spine"


def _load_manifest() -> dict:
    return yaml.safe_load((DEBUG_SPINE_DIR / "debug_spine_manifest.yaml").read_text(encoding="utf-8"))


def test_debug_spine_manifest_declares_w000_identity() -> None:
    manifest = _load_manifest()

    assert manifest["track"]["id"] == "ABACUS_DEBUG_SPINE_W000"
    assert manifest["track"]["wave"] == "W000"
    assert manifest["track"]["branch"] == "wave/W000-debug-spine-lldb-dap-swift"


def test_debug_spine_manifest_preserves_control_backbone_and_targets() -> None:
    manifest = _load_manifest()

    assert manifest["control_surface"]["adapter"] == "lldb-dap"
    assert manifest["control_surface"]["protocol"] == "Debug Adapter Protocol"
    assert manifest["native_backbone"]["language"] == "Swift"

    target_languages = {target["language"] for target in manifest["federated_targets"]}
    assert target_languages == {"Python", "JavaScript", "TypeScript"}


def test_debug_spine_manifest_requires_abacus_render_and_github_audit() -> None:
    manifest = _load_manifest()

    governance = manifest["abacus_governance"]
    assert governance["layer"] == "trace_render_evidence"
    assert governance["render_required"] is True
    assert governance["evidence_required"] is True

    github = manifest["github_substrate"]
    assert github["repository"] == "GBOGEB/ABACUS"
    assert github["audit_required"] is True
    assert {"actions_log", "artifact_bundle", "pull_request_lineage", "commit_sha"}.issubset(
        set(github["persistence_channels"])
    )


def test_trace_contract_schema_is_json_and_pins_debug_invariants() -> None:
    schema = json.loads((DEBUG_SPINE_DIR / "trace_contract.schema.json").read_text(encoding="utf-8"))

    assert schema["title"] == "ABACUS_DEBUG_SPINE_W000 Trace Contract"
    assert schema["properties"]["track_id"]["const"] == "ABACUS_DEBUG_SPINE_W000"
    assert schema["properties"]["adapter"]["properties"]["name"]["const"] == "lldb-dap"
    assert schema["properties"]["backbone"]["properties"]["language"]["const"] == "Swift"
    assert schema["properties"]["target"]["properties"]["language"]["enum"] == [
        "Python",
        "JavaScript",
        "TypeScript",
    ]
    assert schema["properties"]["render"]["properties"]["required"]["const"] is True


def test_runtime_manifest_registers_debug_spine_module() -> None:
    runtime_manifest = yaml.safe_load((ROOT / "abacus_runtime" / "runtime_manifest.yaml").read_text(encoding="utf-8"))

    assert "debug_spine" in runtime_manifest["modules"]
