"""Logic of tools/physics_crosscheck.py, exercised without CoolProp or an ABACUS checkout."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tool():
    spec = importlib.util.spec_from_file_location("physics_crosscheck", REPO_ROOT / "tools" / "physics_crosscheck.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def tool():
    return _tool()


@pytest.fixture(scope="module")
def spec(tool):
    return tool.load_pin()["output_crosscheck"]


@pytest.fixture(scope="module")
def basic(tool):
    return tool.basic_incarnation()


def _scaled(fn, rho=1.0):
    def g(t, p):
        out = dict(fn(t, p))
        out["density_kg_m3"] *= rho
        return out

    return g


def test_grid_has_in_domain_points_and_out_of_domain_probes(tool, spec, basic):
    _, in_domain = basic
    points = tool.grid_points(spec)
    assert len(points) == len(spec["grid_T_K"]) * len(spec["grid_p_kPa"]) + len(spec["probes_T_K_p_kPa"])
    assert all(in_domain(t, p) for t, p in points[: len(points) - len(spec["probes_T_K_p_kPa"])])
    assert not any(in_domain(t, p) for t, p in spec["probes_T_K_p_kPa"])
    assert tuple(spec["reference_T_K_p_kPa"]) in points


def test_identical_providers_pass_everywhere_in_domain(tool, spec, basic):
    fn, in_domain = basic
    report = tool.run(spec, fn, fn, in_domain, "test")
    assert report["in_domain_failures"] == 0
    verdicts = {r["verdict"] for r in report["rows"]}
    assert verdicts == {"PASS", "NOT_APPLICABLE"}
    assert report["worst_in_domain"]["density_rel_dev"] == pytest.approx(0.0, abs=1e-15)


def test_density_disagreement_inside_domain_fails_the_gate(tool, spec, basic):
    fn, in_domain = basic
    report = tool.run(spec, _scaled(fn, rho=1.05), fn, in_domain, "test")
    assert report["in_domain_failures"] == report["in_domain_points"]
    problems = tool.gate(report, {**spec, "output_checksum_sha256": report["output_checksum_sha256"], "coolprop_version": "test"})
    assert any(p.startswith("IN_DOMAIN_TOLERANCE") for p in problems)


def test_out_of_domain_disagreement_is_reported_not_judged(tool, spec, basic):
    fn, in_domain = basic

    def governing(t, p):
        return _scaled(fn, rho=2.0 if not in_domain(t, p) else 1.0)(t, p)

    report = tool.run(spec, governing, fn, in_domain, "test")
    assert report["in_domain_failures"] == 0
    assert report["worst_out_of_domain"]["density_rel_dev"] == pytest.approx(0.5)


def test_output_checksum_ignores_sub_rounding_noise_but_tracks_real_change(tool, spec, basic):
    fn, in_domain = basic
    base = tool.run(spec, fn, fn, in_domain, "7.2.0")["output_checksum_sha256"]
    noisy = tool.run(spec, _scaled(fn, rho=1 + 1e-12), fn, in_domain, "7.2.0")["output_checksum_sha256"]
    moved = tool.run(spec, _scaled(fn, rho=1 + 1e-6), fn, in_domain, "7.2.0")["output_checksum_sha256"]
    other_cp = tool.run(spec, fn, fn, in_domain, "7.3.0")["output_checksum_sha256"]
    assert noisy == base
    assert moved != base
    assert other_cp != base


def test_gate_requires_a_recorded_checksum_and_matching_coolprop(tool, spec, basic):
    fn, in_domain = basic
    report = tool.run(spec, fn, fn, in_domain, "7.1.0")
    problems = tool.gate(report, {**spec, "output_checksum_sha256": tool.PENDING})
    assert any(p.startswith("OUTPUT_CHECKSUM_NOT_RECORDED") for p in problems)
    assert any(p.startswith("COOLPROP_VERSION") for p in problems)
    drift = tool.gate(report, {**spec, "output_checksum_sha256": "0" * 64, "coolprop_version": "7.1.0"})
    assert any(p.startswith("OUTPUT_DRIFT") for p in drift)


def test_zero_in_domain_points_is_a_failure(tool, spec, basic):
    fn, _ = basic
    report = tool.run(spec, fn, fn, lambda t, p: False, "test")
    assert report["in_domain_points"] == 0
    assert any(p.startswith("ZERO_IN_DOMAIN_POINTS") for p in tool.gate(report, spec))
