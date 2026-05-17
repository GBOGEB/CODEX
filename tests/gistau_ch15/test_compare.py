"""Tests for the backend comparison framework (compare.py)."""
from __future__ import annotations

import pytest

from gistau_ch15.properties.base import State
from gistau_ch15.properties.compare import (
    BackendDefinition,
    BackendStateResult,
    BackendTier,
    PropertyDelta,
    StatePointRequest,
    as_report_rows,
    compare_to_reference,
    evaluate_state_points,
)
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FLUID = "helium"
_REQUEST = StatePointRequest(
    id="r1",
    tuple_id="T00",
    fluid=_FLUID,
    pressure_kpa=101.3,
    temperature_k=300.0,
)


def _make_definition(name: str, tier: BackendTier, backend) -> BackendDefinition:
    return BackendDefinition(
        name=name,
        tier=tier,
        backend=backend,
        role="test",
        notes="",
    )


# ---------------------------------------------------------------------------
# evaluate_state_points
# ---------------------------------------------------------------------------


def test_evaluate_available_backend_returns_state():
    backend = FallbackHeliumBackend()
    defn = _make_definition("fallback", BackendTier.FALLBACK, backend)
    results = evaluate_state_points([defn], [_REQUEST])

    assert len(results) == 1
    r = results[0]
    assert r.state is not None
    assert r.error is None
    assert r.backend_name == "fallback"
    assert r.request_id == "r1"


def test_evaluate_unavailable_backend_records_sentinel():
    defn = _make_definition("missing", BackendTier.REFPROP, None)
    results = evaluate_state_points([defn], [_REQUEST])

    assert len(results) == 1
    r = results[0]
    assert r.state is None
    assert r.error == "backend unavailable"


def test_evaluate_with_generator_request_each_backend_sees_all_requests():
    """Materialisation fix: a generator must not be silently exhausted."""
    backend = FallbackHeliumBackend()
    defn_a = _make_definition("a", BackendTier.FALLBACK, backend)
    defn_b = _make_definition("b", BackendTier.FALLBACK, backend)

    extra = StatePointRequest(
        id="r2", tuple_id="T01", fluid=_FLUID, pressure_kpa=200.0, temperature_k=200.0
    )

    def _gen():
        yield _REQUEST
        yield extra

    results = evaluate_state_points([defn_a, defn_b], _gen())

    backend_a_ids = {r.request_id for r in results if r.backend_name == "a"}
    backend_b_ids = {r.request_id for r in results if r.backend_name == "b"}
    assert backend_a_ids == {"r1", "r2"}
    assert backend_b_ids == {"r1", "r2"}


class _RaisingBackend(FallbackHeliumBackend):
    def state_pt(self, fluid, p_kpa, t_k):
        raise ValueError("simulated backend error")


def test_evaluate_backend_exception_is_recorded():
    defn = _make_definition("raiser", BackendTier.FALLBACK, _RaisingBackend())
    results = evaluate_state_points([defn], [_REQUEST])

    assert len(results) == 1
    r = results[0]
    assert r.state is None
    assert r.error == "simulated backend error"


# ---------------------------------------------------------------------------
# compare_to_reference — status codes
# ---------------------------------------------------------------------------


def _result(
    backend: str,
    tier: BackendTier,
    state: State | None,
    error: str | None = None,
) -> BackendStateResult:
    return BackendStateResult(
        backend_name=backend,
        tier=tier,
        request_id="r1",
        tuple_id="T00",
        state=state,
        error=error,
    )


def _state(t: float = 300.0, h: float = 1000.0) -> State:
    return State(
        pressure_kpa=101.3,
        temperature_k=t,
        enthalpy_j_kg=h,
        entropy_j_kgk=10.0,
        density_kg_m3=0.16,
    )


def test_compare_reference_missing_reports_blocked():
    results = [
        _result("a", BackendTier.FALLBACK, _state()),
    ]
    deltas = compare_to_reference(results, reference_backend_name="nonexistent")
    assert len(deltas) == 1
    assert deltas[0].status == "blocked_reference_missing"


def test_compare_unavailable_backend_status():
    results = [
        _result("ref", BackendTier.FALLBACK, _state()),
        _result("missing", BackendTier.REFPROP, None, error="backend unavailable"),
    ]
    deltas = compare_to_reference(results, reference_backend_name="ref")
    missing_delta = next(d for d in deltas if d.backend_name == "missing")
    assert missing_delta.status == "backend_unavailable"


def test_compare_evaluation_error_status():
    results = [
        _result("ref", BackendTier.FALLBACK, _state()),
        _result("bad", BackendTier.COOLPROP, None, error="simulated backend error"),
    ]
    deltas = compare_to_reference(results, reference_backend_name="ref")
    bad_delta = next(d for d in deltas if d.backend_name == "bad")
    assert bad_delta.status == "evaluation_error"


def test_compare_successful_delta_calculation():
    ref_state = _state(t=300.0, h=1000.0)
    other_state = _state(t=301.0, h=1010.0)
    results = [
        _result("ref", BackendTier.FALLBACK, ref_state),
        _result("other", BackendTier.COOLPROP, other_state),
    ]
    deltas = compare_to_reference(results, reference_backend_name="ref")
    other_delta = next(d for d in deltas if d.backend_name == "other")
    assert other_delta.status == "ok"
    assert other_delta.delta_temperature_k == pytest.approx(1.0)
    assert other_delta.delta_enthalpy_j_kg == pytest.approx(10.0)


def test_compare_self_delta_is_zero():
    ref_state = _state()
    results = [_result("ref", BackendTier.FALLBACK, ref_state)]
    deltas = compare_to_reference(results, reference_backend_name="ref")
    ref_delta = deltas[0]
    assert ref_delta.status == "ok"
    assert ref_delta.delta_temperature_k == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# as_report_rows
# ---------------------------------------------------------------------------


def test_as_report_rows_serialises_to_dicts():
    delta = PropertyDelta(
        request_id="r1",
        tuple_id="T00",
        backend_name="ref",
        tier=BackendTier.FALLBACK,
        reference_backend="ref",
        delta_temperature_k=0.0,
        delta_enthalpy_j_kg=0.0,
        delta_entropy_j_kgk=0.0,
        delta_density_kg_m3=0.0,
        status="ok",
    )
    rows = as_report_rows([delta])
    assert len(rows) == 1
    assert rows[0]["status"] == "ok"
    assert rows[0]["backend_name"] == "ref"
