from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from abacus_runtime.debug_spine.render_evidence import REQUIRED_EVENT_NAMES, load_trace_jsonl, render_trace_file

ROOT = Path(__file__).resolve().parents[2]
DEBUG_SPINE_DIR = ROOT / "abacus_runtime" / "debug_spine"
SWIFT_DIR = DEBUG_SPINE_DIR / "swift"


def test_swift_executable_package_is_versioned() -> None:
    package = (SWIFT_DIR / "Package.swift").read_text(encoding="utf-8")
    main = (SWIFT_DIR / "Sources" / "AbacusDebugSpine" / "main.swift").read_text(encoding="utf-8")

    assert "// swift-tools-version: 5.9" in package
    assert 'name: "abacus-debug-spine"' in package
    assert "ABACUS_DEBUG_SPINE_W000" in main
    assert "abacus_debug_spine_w001_trace.jsonl" in main


def test_lldb_dap_launch_template_pins_runtime_evidence_paths() -> None:
    launch = json.loads((DEBUG_SPINE_DIR / "lldb-dap" / "launch.template.json").read_text(encoding="utf-8"))

    assert launch["version"] == "0.1.0"
    assert launch["adapter"] == "lldb-dap"
    assert launch["type"] == "lldb-dap"
    assert launch["request"] == "launch"
    assert launch["track_id"] == "ABACUS_DEBUG_SPINE_W000"
    assert launch["wave"] == "W001"
    assert launch["evidence"]["jsonl_trace"].endswith("abacus_debug_spine_w001_trace.jsonl")
    assert launch["evidence"]["markdown_render"].endswith("abacus_debug_spine_w001_evidence.md")


def test_sample_trace_contains_required_event_fields() -> None:
    trace_path = DEBUG_SPINE_DIR / "evidence" / "sample_runtime_trace.jsonl"
    events = load_trace_jsonl(trace_path)

    assert [event["event"]["name"] for event in events] == REQUIRED_EVENT_NAMES
    for event in events:
        assert event["track_id"] == "ABACUS_DEBUG_SPINE_W000"
        assert event["adapter"]["name"] == "lldb-dap"
        assert event["backbone"]["language"] == "Swift"
        assert event["target"]["language"] in {"Python", "JavaScript", "TypeScript"}
        assert event["github"]["repository"] == "GBOGEB/ABACUS"
        assert event["render"]["required"] is True
        assert event["event"]["timestamp"]
        assert event["event"]["evidence_ref"]


def test_renderer_writes_markdown_evidence(tmp_path: Path) -> None:
    trace_path = DEBUG_SPINE_DIR / "evidence" / "sample_runtime_trace.jsonl"
    output_path = tmp_path / "debug_spine_evidence.md"

    rendered = render_trace_file(trace_path, output_path)
    markdown = rendered.read_text(encoding="utf-8")

    assert rendered == output_path
    assert "# ABACUS Debug Spine Runtime Evidence" in markdown
    assert "`ABACUS_DEBUG_SPINE_W000`" in markdown
    assert "session.created" in markdown
    assert "session.closed" in markdown


def test_runtime_proof_manifest_links_executable_evidence_path() -> None:
    manifest = yaml.safe_load((DEBUG_SPINE_DIR / "debug_spine_manifest.yaml").read_text(encoding="utf-8"))
    proof = manifest["runtime_proof"]

    assert proof["wave"] == "W001"
    assert proof["branch"] == "wave/W001-debug-spine-runtime-proof"
    assert proof["swift_package"] == "swift/Package.swift"
    assert proof["executable"] == "abacus-debug-spine"
    assert proof["lldb_dap_launch_template"] == "lldb-dap/launch.template.json"
    assert proof["renderer"] == "render_evidence.py"


@pytest.mark.skipif(subprocess.run(["bash", "-lc", "command -v swift"], capture_output=True).returncode != 0, reason="swift is not installed")
def test_swift_runtime_emits_jsonl_trace(tmp_path: Path) -> None:
    trace_path = tmp_path / "swift_trace.jsonl"
    subprocess.run(
        [
            "swift",
            "run",
            "--package-path",
            str(SWIFT_DIR),
            "abacus-debug-spine",
            "--trace-output",
            str(trace_path),
            "--session-id",
            "pytest-swift",
            "--target-language",
            "TypeScript",
            "--branch",
            "wave/W001-debug-spine-runtime-proof",
            "--commit-sha",
            "pytest-sha",
        ],
        check=True,
        cwd=ROOT,
    )

    events = load_trace_jsonl(trace_path)
    assert [event["event"]["name"] for event in events] == REQUIRED_EVENT_NAMES
    assert {event["target"]["language"] for event in events} == {"TypeScript"}
