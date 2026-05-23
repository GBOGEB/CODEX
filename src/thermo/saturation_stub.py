from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SaturationRegion:
    temperature_k: float
    pressure_pa: float
    region: str
    heii_relevant: bool
    quality_defined: bool
    notes: str


class HeliumSaturationScaffold:
    """Topology-aware helium saturation scaffold.

    This does not claim validated phase-boundary accuracy. It marks regions
    where HEPAK/NIST/REFPROP/CoolProp convergence is required.
    """

    def classify(self, temperature_k: float, pressure_pa: float) -> SaturationRegion:
        heii_relevant = temperature_k < 2.2

        if temperature_k < 1.8:
            region = 'below_current_scope'
        elif temperature_k < 2.2:
            region = 'near_heii_lambda_region'
        elif temperature_k <= 5.2:
            region = 'low_temperature_saturation_candidate'
        else:
            region = 'single_phase_candidate'

        return SaturationRegion(
            temperature_k=temperature_k,
            pressure_pa=pressure_pa,
            region=region,
            heii_relevant=heii_relevant,
            quality_defined=region in {
                'near_heii_lambda_region',
                'low_temperature_saturation_candidate',
            },
            notes='Topology scaffold only; validate against HEPAK/NIST saturation data.',
        )
