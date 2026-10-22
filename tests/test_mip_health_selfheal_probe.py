"""Tests for CODEX's repo-local MIP health/self-heal probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


probe = _load("mip_health_selfheal_probe", "scripts/mip_health_selfheal_probe.py")
emitter = _load("mip_repo_self_index", "scripts/mip_repo_self_index.py")

CHECKOUT_CHECKS = {
    "source_checkout_clean_before",
    "source_checkout_clean_after_repair",
    "source_checkout_unchanged",
}


def _clean_git(monkeypatch, sha: str = "a" * 40):
    def fake_git(*args: str) -> str:
        return sha if args[0] == "rev-parse" else ""

    monkeypatch.setattr(probe, "git", fake_git)


def test_repair_closes_every_missing_artifact_on_a_clean_checkout(monkeypatch):
    _clean_git(monkeypatch)
    receipt = probe.build_receipt()
    assert receipt["verification"] == "PASS", receipt["failed_checks"]
    assert receipt["return_state"] == "IMPROVED"
    assert receipt["before_metric"] == 3
    assert receipt["after_metric"] == 0
    assert receipt["delta"] == -3
    assert receipt["exact_sha"] == "a" * 40
    assert receipt["execution_context"] == "transient_controlled_fixture"
    assert receipt["raw_receipt_retention"] == "transient_runner_only"
    assert receipt["promotion_authority"] is False


def test_probe_never_writes_into_the_source_checkout(monkeypatch):
    _clean_git(monkeypatch)
    module = probe.load_primitive()
    targets = list(module.MINIMAL_ARTIFACTS)
    before = {path: path.exists() for path in targets}
    probe.build_receipt()
    assert {path: path.exists() for path in targets} == before


def test_dirty_checkout_fails_closed(monkeypatch):
    def dirty_git(*args: str) -> str:
        return "a" * 40 if args[0] == "rev-parse" else " M somefile.py"

    monkeypatch.setattr(probe, "git", dirty_git)
    receipt = probe.build_receipt()
    assert receipt["verification"] == "FAIL"
    assert receipt["return_state"] == "REGRESSED"
    assert CHECKOUT_CHECKS <= set(receipt["failed_checks"])


def test_broken_primitive_fails_closed(monkeypatch):
    _clean_git(monkeypatch)
    real_load = probe.load_primitive

    def broken_load():
        module = real_load()
        module.repair_missing_artifacts = lambda: {
            "status": "repair-complete",
            "repaired": [],
            "existing": [],
            "repair_count": 0,
        }
        return module

    monkeypatch.setattr(probe, "load_primitive", broken_load)
    receipt = probe.build_receipt()
    assert receipt["verification"] == "FAIL"
    assert "after_metric_closed" in receipt["failed_checks"]
    assert receipt["delta"] == 0


def test_passing_probe_makes_health_lane_green(monkeypatch):
    _clean_git(monkeypatch)
    receipt = probe.build_receipt()
    monkeypatch.setattr(emitter, "run_git", lambda args: "a" * 40)
    lane = emitter.classify([], receipt)["repo_self_assess_codz_health_selfheal"]
    assert lane["status"] == "green"
    assert lane["evidence"]["delta"] == -3
