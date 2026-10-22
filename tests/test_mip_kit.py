"""Tests for the shareable MIP kit: manifest, drift check, surface config."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


kit = _load("mip_kit_manifest", "scripts/mip_kit_manifest.py")
emitter = _load("mip_repo_self_index", "scripts/mip_repo_self_index.py")
verifier = _load("mip_verify_self_index", "scripts/mip_verify_self_index.py")


@pytest.fixture
def kit_copy(tmp_path: Path) -> Path:
    """A consumer-like copy of the kit files plus a manifest built from them."""
    for rel in kit.KIT_FILES:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    manifest = tmp_path / "MIP" / "kit" / "KIT_MANIFEST.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(kit.build_manifest(tmp_path)), encoding="utf-8")
    return tmp_path


def _manifest(root: Path) -> Path:
    return root / "MIP" / "kit" / "KIT_MANIFEST.json"


# --- manifest / drift check -------------------------------------------------


def test_tracked_manifest_matches_kit_files_in_this_repo():
    result = kit.check()
    assert result["verification"] == "PASS", result
    assert result["file_count"] == len(kit.KIT_FILES)


def test_tracked_manifest_is_what_write_would_produce():
    tracked = json.loads(kit.MANIFEST.read_text(encoding="utf-8"))
    assert tracked == kit.build_manifest()


def test_manifest_excludes_repo_local_surface_config():
    paths = {row["path"] for row in kit.build_manifest()["files"]}
    assert "MIP/mip_surface.json" not in paths
    assert "MIP/kit/KIT_MANIFEST.json" not in paths
    assert set(kit.REPO_LOCAL_FILES).isdisjoint(paths)


def test_clean_copy_passes_and_matches_canonical(kit_copy: Path):
    result = kit.check(kit_copy, _manifest(kit_copy), canonical_path=kit.MANIFEST)
    assert result["verification"] == "PASS", result
    assert result["matches_canonical"] is True
    assert result["diverged_from_canonical"] == []


def test_edited_kit_file_is_reported_as_changed(kit_copy: Path):
    target = kit_copy / "scripts" / "mip_verify_self_index.py"
    target.write_text(
        target.read_text(encoding="utf-8") + "\n# local edit\n", encoding="utf-8"
    )
    result = kit.check(kit_copy, _manifest(kit_copy))
    assert result["verification"] == "FAIL"
    assert result["changed_files"] == ["scripts/mip_verify_self_index.py"]
    assert result["missing_files"] == []


def test_missing_kit_file_is_reported(kit_copy: Path):
    (kit_copy / ".codex/skills/mip-repo-self-index/agents/openai.yaml").unlink()
    result = kit.check(kit_copy, _manifest(kit_copy))
    assert result["verification"] == "FAIL"
    assert result["missing_files"] == [
        ".codex/skills/mip-repo-self-index/agents/openai.yaml"
    ]


def test_crlf_checkout_is_not_drift(kit_copy: Path):
    target = kit_copy / ".codex/skills/mip-repo-self-index/SKILL.md"
    target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
    assert kit.check(kit_copy, _manifest(kit_copy))["verification"] == "PASS"


def test_tampered_manifest_digest_fails(kit_copy: Path):
    manifest = json.loads(_manifest(kit_copy).read_text(encoding="utf-8"))
    manifest["kit_digest_sha256"] = "0" * 64
    _manifest(kit_copy).write_text(json.dumps(manifest), encoding="utf-8")
    result = kit.check(kit_copy, _manifest(kit_copy))
    assert result["verification"] == "FAIL"
    assert result["manifest_digest_consistent"] is False


def test_consumer_out_of_date_with_canonical_fails(kit_copy: Path):
    # The consumer edited a file AND regenerated its own manifest: the local
    # check passes, but the canonical comparison must still fail.
    target = kit_copy / "scripts" / "mip_repo_self_index.py"
    target.write_text(
        target.read_text(encoding="utf-8") + "\n# fork\n", encoding="utf-8"
    )
    _manifest(kit_copy).write_text(
        json.dumps(kit.build_manifest(kit_copy)), encoding="utf-8"
    )
    result = kit.check(kit_copy, _manifest(kit_copy), canonical_path=kit.MANIFEST)
    assert result["missing_files"] == [] and result["changed_files"] == []
    assert result["matches_canonical"] is False
    assert result["diverged_from_canonical"] == ["scripts/mip_repo_self_index.py"]
    assert result["verification"] == "FAIL"


def test_check_cli_exit_codes_and_summary(tmp_path_factory):
    summary = tmp_path_factory.mktemp("out") / "nested" / "kit.json"
    assert kit.main(["check", "--summary", str(summary)]) == 0
    assert json.loads(summary.read_text(encoding="utf-8"))["verification"] == "PASS"

    bad = tmp_path_factory.mktemp("bad") / "manifest.json"
    manifest = json.loads(kit.MANIFEST.read_text(encoding="utf-8"))
    manifest["files"][0]["sha256"] = "0" * 64
    bad.write_text(json.dumps(manifest), encoding="utf-8")
    assert kit.main(["check", "--canonical", str(bad)]) == 1


def test_unreadable_manifest_is_a_clear_error(tmp_path: Path):
    with pytest.raises(SystemExit, match="cannot read kit manifest"):
        kit.check(tmp_path, tmp_path / "absent.json")
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(SystemExit, match="not valid JSON"):
        kit.check(tmp_path, broken)


def test_kit_files_do_not_reference_abacus_only_paths():
    for rel in kit.KIT_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "codespace_jyperter" not in text, rel


# --- surface config resolution ---------------------------------------------


def test_codex_surface_config_declares_repo_health_probe():
    config = emitter.load_surface_config()
    assert config["program"] == "MIP"
    assert config["health_probe"] == emitter.DEFAULT_HEALTH_PROBE
    resolved = emitter.resolve_health_probe(config)
    assert resolved == (ROOT / emitter.DEFAULT_HEALTH_PROBE).resolve()
    assert resolved.is_file()


def test_health_probe_absent_key_uses_default(tmp_path: Path):
    assert (
        emitter.resolve_health_probe({}, tmp_path)
        == tmp_path / emitter.DEFAULT_HEALTH_PROBE
    )


@pytest.mark.parametrize("value", [None, ""])
def test_health_probe_null_means_no_probe(tmp_path: Path, value):
    assert emitter.resolve_health_probe({"health_probe": value}, tmp_path) is None


def test_health_probe_relative_path_resolves_under_root(tmp_path: Path):
    resolved = emitter.resolve_health_probe(
        {"health_probe": "tools/probe.py"}, tmp_path
    )
    assert resolved == (tmp_path / "tools" / "probe.py").resolve()


@pytest.mark.parametrize("value", ["../outside.py", "/etc/probe.py", 7])
def test_health_probe_outside_repo_or_wrong_type_is_rejected(tmp_path: Path, value):
    with pytest.raises(SystemExit):
        emitter.resolve_health_probe({"health_probe": value}, tmp_path)


def test_missing_or_broken_surface_config_reads_as_empty(tmp_path: Path):
    assert emitter.load_surface_config(tmp_path / "absent.json") == {}
    broken = tmp_path / "broken.json"
    broken.write_text("[1, 2]", encoding="utf-8")
    assert emitter.load_surface_config(broken) == {}


def test_no_probe_leaves_health_unexecuted():
    assert emitter.run_health_selfheal_probe(None) is None


def test_verifier_tolerates_missing_surface_config(tmp_path: Path):
    surface = verifier.load_surface(tmp_path / "absent.json")
    assert surface == {"program": "MIP"}
    assert surface.get("nested_surfaces", []) == []


def test_verifier_loads_codex_surface_config():
    surface = verifier.load_surface()
    assert surface["shareable_skill"] == ".codex/skills/mip-repo-self-index"
    assert (ROOT / surface["shareable_skill"] / "SKILL.md").is_file()
    assert set(surface["required_green"]) <= set(verifier.LANES)


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"program": "OTHER"}, "program=MIP"),
        (
            {"program": "MIP", "required_green": ["not_a_lane"]},
            "unknown required_green",
        ),
        ({"program": "MIP", "required_green": "repo_self_produce"}, "must be a list"),
        ({"program": "MIP", "nested_surfaces": [{"path": "x"}]}, "path and emitter"),
    ],
)
def test_verifier_rejects_invalid_surface_config(tmp_path: Path, config, message):
    path = tmp_path / "mip_surface.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(SystemExit, match=message):
        verifier.load_surface(path)


def test_skill_validator_accepts_minimal_producer_summary(tmp_path: Path):
    validator = _load(
        "mip_validate_receipt",
        ".codex/skills/mip-repo-self-index/scripts/validate_receipt.py",
    )
    producer = {
        "schema_version": "0.1",
        "program": "MIP",
        "verification": "PASS",
        "repository": "GBOGEB/CODEX",
        "head_sha": "a" * 40,
        "raw_receipt_retention": "transient_runner_only",
        "root_self_index": {"runs": 2, "normalized_equal": True},
    }
    assert validator.validate_producer(producer, "a" * 40) == "a" * 40
    with pytest.raises(SystemExit, match="expected_sha"):
        validator.validate_producer(producer, "b" * 40)


# --- debug/LDAB lane: GREEN needs an executed diagnostic --------------------

diagnostic = _load("mip_debug_diagnostic", "scripts/mip_debug_diagnostic.py")
HEAD = emitter.run_git(["rev-parse", "HEAD"])
DEBUG_PATHS = [Path("tools/debug_helper.py")]


def _passing_diagnostic(**overrides):
    value = {
        "diagnostic": "mip-debug-diagnostic",
        "verification": "PASS",
        "exact_sha": HEAD,
        "checks": {"traceback_localizes": True, "validator_fails_closed": True},
        "failed_checks": [],
        "raw_receipt_retention": "transient_runner_only",
    }
    value.update(overrides)
    return value


def test_debug_file_names_alone_are_amber_not_green():
    lane = emitter.debug_assessment(DEBUG_PATHS, None)
    assert lane["status"] == "amber"
    assert lane["evidence"] is None


def test_no_debug_signal_and_no_diagnostic_is_red():
    assert emitter.debug_assessment([], None)["status"] == "red"


def test_passing_diagnostic_on_exact_sha_is_green():
    lane = emitter.debug_assessment([], _passing_diagnostic())
    assert lane["status"] == "green"
    assert lane["evidence"]["exact_sha"] == HEAD


@pytest.mark.parametrize(
    "overrides",
    [
        {"verification": "FAIL"},
        {"exact_sha": "0" * 40},
        {"checks": {}},
        {"checks": {"traceback_localizes": True, "validator_fails_closed": False}},
    ],
)
def test_failing_stale_or_empty_diagnostic_is_not_green(overrides):
    lane = emitter.debug_assessment(DEBUG_PATHS, _passing_diagnostic(**overrides))
    assert lane["status"] == "amber"


def test_diagnostic_outside_a_git_checkout_is_not_green(monkeypatch):
    monkeypatch.setattr(emitter, "run_git", lambda args: None)
    lane = emitter.debug_assessment([], _passing_diagnostic(exact_sha=None))
    assert lane["status"] == "amber"


def test_debug_diagnostic_absent_key_uses_kit_default(tmp_path: Path):
    assert (
        emitter.resolve_debug_diagnostic({}, tmp_path)
        == tmp_path / emitter.DEFAULT_DEBUG_DIAGNOSTIC
    )
    assert emitter.resolve_debug_diagnostic({"debug_diagnostic": None}) is None
    with pytest.raises(SystemExit, match="debug_diagnostic"):
        emitter.resolve_debug_diagnostic({"debug_diagnostic": "../x.py"}, tmp_path)


def test_kit_diagnostic_passes_on_this_checkout():
    receipt = diagnostic.build_receipt()
    assert receipt["verification"] == "PASS", receipt["failed_checks"]
    assert diagnostic.build_receipt() == receipt


def test_emitter_binds_executed_diagnostic_to_head():
    result = emitter.run_debug_diagnostic(ROOT / emitter.DEFAULT_DEBUG_DIAGNOSTIC)
    assert result["verification"] == "PASS"
    assert result["exact_sha"] == HEAD
    assert emitter.debug_assessment([], result)["status"] == "green"


def test_kit_diagnostic_traceback_check_detects_wrong_line(monkeypatch):
    monkeypatch.setattr(diagnostic, "TARGET_LINE", diagnostic.TARGET_LINE + 1)
    assert diagnostic.traceback_localizes() is False


def test_kit_diagnostic_fails_closed_without_validator(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(diagnostic, "VALIDATOR", tmp_path / "missing.py")
    receipt = diagnostic.build_receipt()
    assert receipt["verification"] == "FAIL"
    assert receipt["failed_checks"] == ["validator_fails_closed"]


def test_unparseable_diagnostic_output_is_a_failure(tmp_path: Path):
    broken = tmp_path / "broken_diagnostic.py"
    broken.write_text("raise SystemExit(3)\n", encoding="utf-8")
    result = emitter.run_debug_diagnostic(broken)
    assert result["verification"] == "FAIL"
    assert result["failed_checks"] == ["diagnostic_execution"]
    assert emitter.run_debug_diagnostic(None) is None


def _receipt_with_debug(evidence, status):
    return {
        "assessments": {
            verifier.DEBUG_LANE: {"status": status, "evidence": evidence},
        }
    }


def test_verifier_requires_passing_debug_diagnostic_when_lane_required():
    receipt = _receipt_with_debug(None, "amber")
    with pytest.raises(SystemExit, match="debug/LDAB diagnostic validation failed"):
        verifier.summarize_debug_diagnostic(
            receipt, {verifier.DEBUG_LANE: "AMBER"}, HEAD, required=True
        )


def test_verifier_records_failing_debug_diagnostic_when_not_required():
    evidence = _passing_diagnostic(verification="FAIL")
    summary = verifier.summarize_debug_diagnostic(
        _receipt_with_debug(evidence, "amber"),
        {verifier.DEBUG_LANE: "AMBER"},
        HEAD,
        required=False,
    )
    assert summary["verification"] == "FAIL"
    assert "verification" in summary["failed_checks"]


def test_verifier_accepts_passing_debug_diagnostic():
    summary = verifier.summarize_debug_diagnostic(
        _receipt_with_debug(_passing_diagnostic(), "green"),
        {verifier.DEBUG_LANE: "GREEN"},
        HEAD,
        required=True,
    )
    assert summary["verification"] == "PASS"
    assert summary["passed_checks"] == [
        "traceback_localizes",
        "validator_fails_closed",
    ]


def test_skill_validator_rejects_debug_diagnostic_on_other_sha():
    validator = _load(
        "mip_validate_receipt",
        ".codex/skills/mip-repo-self-index/scripts/validate_receipt.py",
    )
    producer = {
        "schema_version": "0.1",
        "program": "MIP",
        "verification": "PASS",
        "repository": "GBOGEB/CODEX",
        "head_sha": "a" * 40,
        "raw_receipt_retention": "transient_runner_only",
        "root_self_index": {"runs": 2, "normalized_equal": True},
        "debug_diagnostic": {
            "verification": "PASS",
            "exact_sha": "b" * 40,
            "raw_receipt_retention": "transient_runner_only",
        },
    }
    with pytest.raises(SystemExit, match="debug_sha"):
        validator.validate_producer(producer, None)
    producer["debug_diagnostic"]["exact_sha"] = "a" * 40
    assert validator.validate_producer(producer, None) == "a" * 40
