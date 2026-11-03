"""Coverage wave 8 (L3): block validators/preview, bridge + agent validators,
federation metric semantics and the QPS W56 returned-evidence hash gate.

Validators that read fixed repo paths are pointed at ``tmp_path`` copies by
patching their module-level ``ROOT``/path constants; the real-repo PASS path is
also asserted read-only.
"""
from __future__ import annotations

import shutil

import pytest
import yaml

from tests.coverage_waves._loader import load

BLOCKS = "scripts/validate_blocks.py"
PREVIEW = "scripts/render_markdown_preview.py"
BRIDGE = "scripts/bridge_orchestrator.py"
AGENTS = "scripts/validate_agent_implementations.py"
FEDSEM = "scripts/validate_federation_metric_semantics.py"
W56 = "scripts/qps_w56_verify_hash_receipt_v3.py"


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _block(bid, level=2, **extra):
    b = {"block_id": bid, "block_type": "text", "title": f"T {bid}", "status": "draft", "version": "1",
         "section": {"heading_id": "H", "heading_level": level, "word_style": f"Heading {level}"},
         "lineage": {"created_from": "prompt"}, "render": {"markdown": True, "word": True, "excel": False,
                                                            "html": True},
         "content": "body"}
    b.update(extra)
    return b


# ---------------------------------------------------------------- validate_blocks
def test_validate_block_ok():
    assert load(BLOCKS).validate_block(_block("B1"), 0) == []


def test_validate_block_every_error():
    m = load(BLOCKS)
    errs = " | ".join(m.validate_block({"section": 1, "render": 2, "lineage": 3, "content": " "}, 4))
    for needle in ("block[4] missing required fields", "section must be a mapping", "render must be a mapping",
                   "lineage must be a mapping", "content must be a non-empty string"):
        assert needle in errs
    errs = m.validate_block(_block("B", 3, section={"heading_level": 3, "word_style": "Heading 2"},
                                   render={"markdown": 1}, lineage={}), 0)
    joined = " | ".join(errs)
    assert "section missing fields: heading_id" in joined
    assert "should match heading_level as 'Heading 3'" in joined
    assert "render missing fields: excel, html, word" in joined
    assert "lineage.created_from is required" in joined


def test_validate_blocks_file_and_main(tmp_path, monkeypatch, capsys):
    m = load(BLOCKS)
    good = _write(tmp_path / "g.yaml", yaml.safe_dump({"blocks": [_block("A"), _block("B")]}))
    assert m.validate_file(good) == (2, [])
    bad = _write(tmp_path / "b.yaml", yaml.safe_dump({"blocks": [_block("A"), _block("A"), "junk"]}))
    count, errors = m.validate_file(bad)
    assert count == 3 and "duplicate block_id: A" in errors and "block[2] must be a mapping" in errors
    assert m.validate_file(_write(tmp_path / "x.yaml", "blocks: {}\n")) == (0, ["root key 'blocks' must be a list"])
    with pytest.raises(ValueError):
        m.load_yaml(_write(tmp_path / "l.yaml", "[1]\n"))
    monkeypatch.setattr("sys.argv", ["v", str(good)])
    assert m.main() == 0
    monkeypatch.setattr("sys.argv", ["v", str(bad)])
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "PASS:" in out and "FAIL:" in out and "- duplicate block_id: A" in out


def test_validate_blocks_repo_sample_is_valid():
    m = load(BLOCKS)
    count, errors = m.validate_file(m.Path(__file__).resolve().parents[2] / "ssot/blocks/sample_blocks.yaml")
    assert count > 0 and errors == []


# ---------------------------------------------------------------- render_markdown_preview
@pytest.mark.parametrize(("lang", "fence"), [("Python", "python"), ("rust", "text"), (None, "text")])
def test_fence_language(lang, fence):
    assert load(PREVIEW).fence_language({"language": lang}) == fence


@pytest.mark.parametrize(("level", "marks"), [(1, "##"), (4, "####"), (9, "######"), ("x", "##")])
def test_render_block_heading_clamp(level, marks):
    lines = load(PREVIEW).render_block({"section": {"heading_level": level}, "title": "T"})
    assert lines[0] == f"{marks} T"


def test_render_block_defaults_and_fields():
    m = load(PREVIEW)
    lines = m.render_block({})
    assert lines[0] == "## Untitled block" and "- Block ID: `UNKNOWN-BLOCK`" in lines
    full = m.render_block(_block("B9", language="yaml", content="k: v\n\n"))
    assert "```yaml" in full and "k: v" in full and "- Created from: `prompt`" in full


def test_render_preview_and_main(tmp_path, monkeypatch, capsys):
    m = load(PREVIEW)
    src = _write(tmp_path / "b.yaml", yaml.safe_dump({"blocks": [_block("A"), "skip-me"]}))
    out = tmp_path / "o" / "p.md"
    m.render_preview(src, out)
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# CODEX Reusable Block Library Preview") and text.count("- Block ID:") == 1
    with pytest.raises(ValueError):
        m.load_blocks(_write(tmp_path / "bad.yaml", "blocks: 1\n"))
    assert m.load_blocks(_write(tmp_path / "e.yaml", "")) == []
    monkeypatch.setattr("sys.argv", ["p", str(src), str(tmp_path / "p2.md")])
    assert m.main() == 0 and "Wrote Markdown preview" in capsys.readouterr().out


# ---------------------------------------------------------------- bridge orchestrator
def _bridge_root(tmp_path, links, manifest=True, bridges=None):
    _write(tmp_path / "governance" / "federation_registry.yml", yaml.safe_dump({"federation_links": links}))
    if manifest:
        _write(tmp_path / "bridge_manifest.yaml",
               yaml.safe_dump({"federation_bridge": {"repos": {"CODEX": {"role": "gov"}, "X": {}}}}))
    for name, body in (bridges or {}).items():
        _write(tmp_path / "bridges" / f"{name}.yml", yaml.safe_dump(body))
    return tmp_path


def test_bridge_ok_with_and_without_configs(tmp_path, monkeypatch, capsys):
    m = load(BRIDGE)
    root = _bridge_root(tmp_path, [{"id": "office-link", "purpose": "docs"}, {"id": "diagram-link"}],
                        bridges={"office_bridge": {"bridge": {"name": "o"}}})
    monkeypatch.setattr(m, "ROOT", root)
    assert m.main() == 0
    out = capsys.readouterr().out
    assert "[office-link]" in out and "No bridge config" in out and "Repos tracked: 2" in out
    assert "- X: N/A" in out


def test_bridge_missing_key_fails(tmp_path, monkeypatch, capsys):
    m = load(BRIDGE)
    root = _bridge_root(tmp_path, [{"id": "office-link"}], manifest=False, bridges={"office_bridge": {"x": 1}})
    monkeypatch.setattr(m, "ROOT", root)
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "missing 'bridge' key" in out and "Bridge manifest not found" in out


def test_bridge_no_links_and_no_registry(tmp_path, monkeypatch, capsys):
    m = load(BRIDGE)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    assert m.main() == 1
    _bridge_root(tmp_path, [])
    assert m.main() == 0
    out = capsys.readouterr().out
    assert "Federation registry not found" in out and "No federation links defined" in out


def test_bridge_repo_registry_validates():
    assert load(BRIDGE).main() == 0


# ---------------------------------------------------------------- agent implementations
def _agents_root(tmp_path, agents, mappings, stats=None):
    _write(tmp_path / "governance" / "agent_registry.yml", yaml.safe_dump({"agents": agents}))
    _write(tmp_path / "governance" / "agent_implementation_map.yml",
           yaml.safe_dump({"mappings": mappings, "statistics": stats or {}}))
    return tmp_path


def test_agents_all_ok(tmp_path, monkeypatch, capsys):
    m = load(AGENTS)
    _write(tmp_path / "impl.py", "")
    root = _agents_root(tmp_path, [{"id": "a1"}], [{"agent_id": "a1", "capabilities": [
        {"capability": "c1", "implementation": "impl.py", "status": "done"},
        {"capability": "c2", "status": "scaffold"}]}],
        {"total_capabilities": 2, "implemented_capabilities": 1})
    monkeypatch.setattr(m, "ROOT", root)
    assert m.main() == 0
    out = capsys.readouterr().out
    assert "Implemented: 1 (50.0%)" in out and "Statistics mismatch" not in out


def test_agents_failures_and_stat_mismatch(tmp_path, monkeypatch, capsys):
    m = load(AGENTS)
    root = _agents_root(tmp_path, [{"id": "a1"}, {"id": "a2"}], [{"agent_id": "a1", "capabilities": [
        {"capability": "c1", "implementation": "missing.py"}]}], {"total_capabilities": 5,
                                                                  "implemented_capabilities": 3})
    monkeypatch.setattr(m, "ROOT", root)
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "a2: NO MAPPING" in out and "FILE NOT FOUND: missing.py" in out
    assert "counted 1 capabilities, map claims 5" in out and "counted 0 implemented, map claims 3" in out


def test_agents_missing_files(tmp_path, monkeypatch, capsys):
    m = load(AGENTS)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    assert m.main() == 1
    _write(tmp_path / "governance" / "agent_registry.yml", "agents: []\n")
    assert m.main() == 1
    out = capsys.readouterr().out
    assert "Agent registry not found" in out and "implementation map not found" in out


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: scripts/validate_agent_implementations.py divides by total_caps when printing "
        "the summary, so an implementation map with zero capabilities crashes with ZeroDivisionError"
    ),
)
def test_agents_zero_capabilities_does_not_crash(tmp_path, monkeypatch):
    m = load(AGENTS)
    monkeypatch.setattr(m, "ROOT", _agents_root(tmp_path, [], []))
    assert m.main() == 0


def test_agents_repo_map_validates():
    assert load(AGENTS).main() == 0


# ---------------------------------------------------------------- federation metric semantics
def test_federation_semantics_repo_pass(capsys):
    m = load(FEDSEM)
    assert m.main() == 0
    out = capsys.readouterr().out
    assert '"status": "PASS"' in out and '"formal_credit_delta": 0' in out


def test_federation_semantics_load_helpers(tmp_path):
    m = load(FEDSEM)
    with pytest.raises(AssertionError, match="Expected JSON object"):
        m._load_json(_write(tmp_path / "a.json", "[1]"))
    with pytest.raises((RuntimeError, FileNotFoundError, OSError)):
        m._load_module("l3_missing_mod", tmp_path / "nope.txt")


def test_federation_semantics_detects_promoted_metric(tmp_path, monkeypatch):
    import json as _json
    m = load(FEDSEM)
    contract = _json.loads(m.CONTRACT_PATH.read_text(encoding="utf-8"))
    first = next(iter(contract["metrics"]))
    contract["metrics"][first]["promotion_to_semantically_bound_allowed"] = True
    monkeypatch.setattr(m, "CONTRACT_PATH", _write(tmp_path / "c.json", _json.dumps(contract)))
    with pytest.raises(AssertionError):
        m.main()


# ---------------------------------------------------------------- QPS W56 hash gate
def test_w56_gate_repo_pass(capsys):
    m = load(W56)
    assert m.main() == 0
    out = capsys.readouterr().out
    assert "HASH GATE PASSED" in out and '"network_access": "NONE"' in out


def test_w56_require_and_load(tmp_path):
    m = load(W56)
    m.require(True, "never")
    with pytest.raises(SystemExit, match="boom"):
        m.require(False, "boom")
    with pytest.raises(SystemExit, match="expected mapping"):
        m.load(_write(tmp_path / "x.yaml", "- 1\n"))


def _w56_copy(tmp_path, monkeypatch, m):
    for attr in ("RECEIPT", "CHILD_PROOF", "INTAKE", "DOW_RETURN"):
        src = getattr(m, attr)
        dst = tmp_path / src.name
        shutil.copyfile(src, dst)
        monkeypatch.setattr(m, attr, dst)
    return tmp_path


@pytest.mark.parametrize(
    ("attr", "path", "value", "message"),
    [
        ("RECEIPT", ("status",), "FAIL", "KEB hash receipt is not PASS"),
        ("CHILD_PROOF", ("workflow_result",), "FAIL", "child source-owner workflow result is not PASS"),
        ("INTAKE", ("input", "child_repo"), "x/y", "intake repo mismatch"),
        ("DOW_RETURN", ("mutation_assertion", "payload_mutated_by_dow"), True, "DOW mutation assertion violated"),
        ("RECEIPT", ("route_gate", "fail_closed"), False, "hash gate is not fail-closed"),
    ],
)
def test_w56_gate_fails_closed_on_tamper(tmp_path, monkeypatch, attr, path, value, message):
    m = load(W56)
    _w56_copy(tmp_path, monkeypatch, m)
    target = getattr(m, attr)
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    target.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(SystemExit, match=message):
        m.main()


@pytest.mark.xfail(
    strict=True,
    reason=(
        "production_defect: scripts/bridge_orchestrator.py and scripts/validate_agent_implementations.py print "
        "emoji status markers, which raise UnicodeEncodeError on the cp1252 Windows console (CLAUDE.md: keep "
        "CLI prints ASCII)"
    ),
)
def test_bridge_output_is_cp1252_safe(capsys):
    load(BRIDGE).main()
    capsys.readouterr().out.encode("cp1252")
