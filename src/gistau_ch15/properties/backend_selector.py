from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from gistau_ch15.properties.compare import BackendTier
from gistau_ch15.properties.fallback_helium import FallbackHeliumBackend
from gistau_ch15.properties.errors import PropertyBackendUnavailable


@dataclass(frozen=True)
class BackendAvailability:
    name: str
    tier: BackendTier
    available: bool
    reason: str


def _try_backend(name: str, tier: BackendTier, factory: Any) -> tuple[Any | None, BackendAvailability]:
    try:
        backend = factory()
        load = getattr(backend, "_load", None)
        if callable(load):
            load()
        return backend, BackendAvailability(name=name, tier=tier, available=True, reason="available")
    except PropertyBackendUnavailable as exc:
        return None, BackendAvailability(name=name, tier=tier, available=False, reason=str(exc))
    except Exception as exc:
        return None, BackendAvailability(name=name, tier=tier, available=False, reason=str(exc))


def select_available_backends() -> tuple[dict[str, Any], list[BackendAvailability]]:
    """Return available property backends and explicit availability statuses.

    Optional backends must never hard-fail CI. Missing REFPROP, HEPAK or
    CoolProp is reported as structured status and the fallback backend remains
    available.
    """

    backends: dict[str, Any] = {
        "fallback": FallbackHeliumBackend(),
    }
    availability: list[BackendAvailability] = [
        BackendAvailability(
            name="fallback",
            tier=BackendTier.FALLBACK,
            available=True,
            reason="deterministic built-in backend",
        )
    ]

    optional_specs = [
        ("coolprop", BackendTier.COOLPROP, "gistau_ch15.properties.coolprop_adapter", "CoolPropAdapter"),
        ("refprop", BackendTier.REFPROP, "gistau_ch15.properties.refprop_adapter", "REFPROPAdapter"),
        ("hepak", BackendTier.HEPAK, "gistau_ch15.properties.hepak_adapter", "HEPAKAdapter"),
    ]

    for name, tier, module_name, class_name in optional_specs:
        def factory(module_name=module_name, class_name=class_name):
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            return cls()

        backend, status = _try_backend(name, tier, factory)
        availability.append(status)
        if backend is not None:
            backends[name] = backend

    availability.append(
        BackendAvailability(
            name="nist_gistau_reference",
            tier=BackendTier.NIST_REFERENCE,
            available=True,
            reason="fixture/reference data from worked_examples.json",
        )
    )

    return backends, availability


def availability_report_rows() -> list[dict[str, Any]]:
    """Serialize backend availability for JSON and HTML review pages."""

    _, availability = select_available_backends()
    rows = []
    for item in availability:
        row = asdict(item)
        row["tier"] = item.tier.value
        rows.append(row)
    return rows
