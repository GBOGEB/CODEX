from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationPoint:
    example_id: str
    tuple_id: str
    fluid: str
    pressure_kpa: float
    temperature_k: float
    notes: str = ""


CANONICAL_2K_POINTS: list[ValidationPoint] = [
    ValidationPoint(
        example_id="WE-T02-SAT-LIQUID-HELIUM-003",
        tuple_id="sat-2k-001",
        fluid="Helium",
        pressure_kpa=3.2,
        temperature_k=2.0,
        notes="canonical 2 K saturated helium validation point",
    ),
    ValidationPoint(
        example_id="WE-T04-CRYOGENIC-EXPANDER-001",
        tuple_id="expander-2k-001",
        fluid="Helium",
        pressure_kpa=120.0,
        temperature_k=4.5,
        notes="cryogenic expander validation anchor",
    ),
]


REFPROP_GAS_REGION_POINTS: list[ValidationPoint] = [
    ValidationPoint(
        example_id="WE-T00-REFPROP-H-PT-001",
        tuple_id="refprop-gas-001",
        fluid="Helium",
        pressure_kpa=101.325,
        temperature_k=300.0,
        notes="canonical gas-region PT validation",
    ),
    ValidationPoint(
        example_id="WE-T00-REFPROP-HSD-PT-002",
        tuple_id="refprop-gas-002",
        fluid="Helium",
        pressure_kpa=500.0,
        temperature_k=80.0,
        notes="cryogenic gas-region PT validation",
    ),
]
