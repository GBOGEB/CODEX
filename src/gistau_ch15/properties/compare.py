from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Iterable, Mapping, Any

from .base import PropertyBackend, State


class BackendTier(str, Enum):
    """Property backend tier classification for GISTAU Ch15 validation."""

    FALLBACK = "tier0_fallback"
    COOLPROP = "tier1_coolprop"
    REFPROP = "tier2_refprop"
    HEPAK = "tier3_hepak"
    NIST_REFERENCE = "tier4_nist_reference"


@dataclass(frozen=True)
class StatePointRequest:
    id: str
    tuple_id: str
    fluid: str
    pressure_kpa: float
    temperature_k: float
    notes: str = ""


@dataclass(frozen=True)
class BackendStateResult:
    backend_name: str
    tier: BackendTier
    request_id: str
    tuple_id: str
    state: State | None
    error: str | None = None


@dataclass(frozen=True)
class PropertyDelta:
    request_id: str
    tuple_id: str
    backend_name: str
    tier: BackendTier
    reference_backend: str
    delta_temperature_k: float | None
    delta_enthalpy_j_kg: float | None
    delta_entropy_j_kgk: float | None
    delta_density_kg_m3: float | None
    status: str


@dataclass(frozen=True)
class BackendDefinition:
    name: str
    tier: BackendTier
    backend: PropertyBackend | None
    role: str
    notes: str


def evaluate_state_points(
    backend_definitions: Iterable[BackendDefinition],
    requests: Iterable[StatePointRequest],
) -> list[BackendStateResult]:
    """Evaluate PT state points across available backends.

    Missing optional backends should be represented with backend=None so the
    comparison report can show an explicit blocked/missing status instead of
    silently disappearing.
    """

    # Materialize once so every backend sees the full request list even when
    # callers pass a generator or other one-shot iterable.
    # Note: for validation workloads the full request set is held in memory
    # simultaneously. This is intentional — cross-backend comparisons require
    # each backend to see identical requests, so streaming is not applicable
    # here. Callers with very large request corpora should batch externally.
    request_list = list(requests)

    results: list[BackendStateResult] = []
    for definition in backend_definitions:
        for request in request_list:
            if definition.backend is None:
                results.append(
                    BackendStateResult(
                        backend_name=definition.name,
                        tier=definition.tier,
                        request_id=request.id,
                        tuple_id=request.tuple_id,
                        state=None,
                        error="backend unavailable",
                    )
                )
                continue

            try:
                state = definition.backend.state_pt(
                    request.fluid,
                    request.pressure_kpa,
                    request.temperature_k,
                )
                results.append(
                    BackendStateResult(
                        backend_name=definition.name,
                        tier=definition.tier,
                        request_id=request.id,
                        tuple_id=request.tuple_id,
                        state=state,
                    )
                )
            except Exception as exc:  # pragma: no cover - backend-specific path
                results.append(
                    BackendStateResult(
                        backend_name=definition.name,
                        tier=definition.tier,
                        request_id=request.id,
                        tuple_id=request.tuple_id,
                        state=None,
                        error=str(exc),
                    )
                )
    return results


def compare_to_reference(
    results: Iterable[BackendStateResult],
    reference_backend_name: str,
) -> list[PropertyDelta]:
    """Compare all backend results against a named reference backend.

    Intended references by maturity:
    - early development: CoolProp or fallback
    - canonical engineering: REFPROP or HEPAK depending on region
    - source validation: NIST/canonical table where available
    """

    grouped: dict[str, list[BackendStateResult]] = {}
    for result in results:
        grouped.setdefault(result.request_id, []).append(result)

    deltas: list[PropertyDelta] = []
    for request_id, group in grouped.items():
        ref = next((r for r in group if r.backend_name == reference_backend_name), None)
        if ref is None or ref.state is None:
            for result in group:
                deltas.append(
                    PropertyDelta(
                        request_id=request_id,
                        tuple_id=result.tuple_id,
                        backend_name=result.backend_name,
                        tier=result.tier,
                        reference_backend=reference_backend_name,
                        delta_temperature_k=None,
                        delta_enthalpy_j_kg=None,
                        delta_entropy_j_kgk=None,
                        delta_density_kg_m3=None,
                        status="blocked_reference_missing",
                    )
                )
            continue

        for result in group:
            if result.state is None:
                # Distinguish: backend was never available (definition.backend is
                # None → "backend unavailable" sentinel) vs a per-state evaluation
                # failure on an available backend.
                if result.error == "backend unavailable":
                    status = "backend_unavailable"
                elif result.error:
                    status = "evaluation_error"
                else:
                    status = "blocked_no_state"
                deltas.append(
                    PropertyDelta(
                        request_id=request_id,
                        tuple_id=result.tuple_id,
                        backend_name=result.backend_name,
                        tier=result.tier,
                        reference_backend=reference_backend_name,
                        delta_temperature_k=None,
                        delta_enthalpy_j_kg=None,
                        delta_entropy_j_kgk=None,
                        delta_density_kg_m3=None,
                        status=status,
                    )
                )
                continue

            deltas.append(
                PropertyDelta(
                    request_id=request_id,
                    tuple_id=result.tuple_id,
                    backend_name=result.backend_name,
                    tier=result.tier,
                    reference_backend=reference_backend_name,
                    delta_temperature_k=result.state.temperature_k - ref.state.temperature_k,
                    delta_enthalpy_j_kg=result.state.enthalpy_j_kg - ref.state.enthalpy_j_kg,
                    delta_entropy_j_kgk=result.state.entropy_j_kgk - ref.state.entropy_j_kgk,
                    delta_density_kg_m3=result.state.density_kg_m3 - ref.state.density_kg_m3,
                    status="ok",
                )
            )
    return deltas


def as_report_rows(deltas: Iterable[PropertyDelta]) -> list[Mapping[str, Any]]:
    """Serialize deltas for JSON, workbook, or static HTML tables."""

    return [asdict(delta) for delta in deltas]
