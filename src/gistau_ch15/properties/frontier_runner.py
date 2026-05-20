from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from gistau_ch15.calculations.expander_replay import CryogenicExpanderReplay
from gistau_ch15.properties.backend_selector import select_available_backends
from gistau_ch15.properties.comparison_runner import ComparisonRunner
from gistau_ch15.properties.compare import (
    BackendDefinition,
    BackendTier,
    StatePointRequest,
    compare_to_reference,
    evaluate_state_points,
)
from gistau_ch15.properties.experimental_correlation import ExperimentalCorrelation
from gistau_ch15.properties.json_export import JsonExportWriter
from gistau_ch15.properties.refprop_verification import RefpropVerificationRunner
from gistau_ch15.properties.saturation_overlays import SaturationOverlayBuilder
from gistau_ch15.properties.uncertainty_quantification import UncertaintyQuantification
from gistau_ch15.properties.validation_dataset import (
    CANONICAL_2K_POINTS,
    REFPROP_GAS_REGION_POINTS,
)
from gistau_ch15.properties.wetness_validation import WetnessValidationRunner


class FrontierEngineeringRunner:
    """End-to-end frontier engineering validation runner.

    This runner intentionally executes with fallback-only environments while
    producing explicit unavailable-state reports for REFPROP and HEPAK. When
    licensed/numerical backends are installed, the same path emits real values.
    """

    def __init__(self, output_directory: str = "outputs/gistau_ch15") -> None:
        self.output_directory = Path(output_directory)
        self.writer = JsonExportWriter(str(self.output_directory))

    def run(self) -> dict[str, Any]:
        backends, availability = select_available_backends()
        backend_definitions = self._backend_definitions(backends)
        requests = self._state_requests()

        state_results = evaluate_state_points(backend_definitions, requests)
        reference_name = "fallback" if "fallback" in backends else backend_definitions[0].name
        deltas = compare_to_reference(state_results, reference_name)

        comparison_runner = ComparisonRunner()
        comparison_rows = comparison_runner.build_rows(deltas)
        summary = comparison_runner.build_summary(comparison_rows)
        heatmap = comparison_runner.build_heatmap_matrix(comparison_rows)

        refprop_rows = RefpropVerificationRunner.as_rows(
            RefpropVerificationRunner().run(
                backend=backends[reference_name],
                backend_name=reference_name,
            )
        )

        wetness_rows = WetnessValidationRunner.as_rows(
            WetnessValidationRunner().run(
                backend=backends[reference_name],
                backend_name=reference_name,
            )
        )

        saturation_builder = SaturationOverlayBuilder()
        saturation_rows = saturation_builder.as_rows(
            saturation_builder.build_temperature_trace(
                backend_name=reference_name,
                backend=backends[reference_name],
                fluid="Helium",
                temperatures_k=saturation_builder.default_helium_2k_grid(),
            )
        )

        expander_replay = CryogenicExpanderReplay().as_dict(
            CryogenicExpanderReplay().replay(
                backend=backends[reference_name],
                fluid="Helium",
                p1_kpa=120.0,
                t1_k=4.5,
                p2_kpa=20.0,
                eta_isentropic=0.75,
                mdot_kg_s=0.05,
            )
        )

        uncertainty = UncertaintyQuantification().as_dict(
            UncertaintyQuantification().summarize(
                quantity="delta_temperature_k",
                backend_name=reference_name,
                values=[
                    row["delta_temperature_k"] or 0.0
                    for row in comparison_rows
                    if row["status"] == "ok"
                ]
                or [0.0],
            )
        )

        correlation = ExperimentalCorrelation().as_dict(
            ExperimentalCorrelation().compare(
                experiment_id="PUBLICATION-REPRODUCTION-SCAFFOLD",
                tuple_id="expander-2k-001",
                backend_name=reference_name,
                quantity="outlet_temperature_k",
                measured_value=4.2,
                predicted_value=float(expander_replay["outlet_temperature_k"]),
                notes="placeholder measured value until experimental campaign data are provided",
            )
        )

        report = {
            "backend_availability": [asdict(item) for item in availability],
            "backend_comparison_rows": comparison_rows,
            "backend_delta_summary": summary,
            "backend_heatmap_matrix": heatmap,
            "refprop_validation_rows": refprop_rows,
            "wetness_validation_rows": wetness_rows,
            "saturation_overlay_rows": saturation_rows,
            "cryogenic_expander_replay": expander_replay,
            "uncertainty_summary": uncertainty,
            "experimental_correlation": correlation,
        }

        self.writer.write_backend_reports(comparison_rows, summary, heatmap)
        self.writer.write_json("refprop_validation_rows.json", refprop_rows)
        self.writer.write_json("wetness_validation_rows.json", wetness_rows)
        self.writer.write_json("saturation_overlay_rows.json", saturation_rows)
        self.writer.write_json("cryogenic_expander_replay.json", expander_replay)
        self.writer.write_json("uncertainty_summary.json", uncertainty)
        self.writer.write_json("experimental_correlation.json", correlation)
        self.writer.write_json("frontier_engineering_report.json", report)

        return report

    @staticmethod
    def _state_requests() -> list[StatePointRequest]:
        points = list(REFPROP_GAS_REGION_POINTS) + list(CANONICAL_2K_POINTS)
        return [
            StatePointRequest(
                id=point.example_id,
                tuple_id=point.tuple_id,
                fluid=point.fluid,
                pressure_kpa=point.pressure_kpa,
                temperature_k=point.temperature_k,
                notes=point.notes,
            )
            for point in points
        ]

    @staticmethod
    def _backend_definitions(backends: dict[str, Any]) -> list[BackendDefinition]:
        tier_map = {
            "fallback": BackendTier.FALLBACK,
            "coolprop": BackendTier.COOLPROP,
            "refprop": BackendTier.REFPROP,
            "hepak": BackendTier.HEPAK,
        }
        definitions: list[BackendDefinition] = []
        for name in ["fallback", "coolprop", "refprop", "hepak"]:
            definitions.append(
                BackendDefinition(
                    name=name,
                    tier=tier_map[name],
                    backend=backends.get(name),
                    role="frontier engineering validation",
                    notes="available" if name in backends else "backend unavailable",
                )
            )
        return definitions


def main() -> None:
    FrontierEngineeringRunner().run()


if __name__ == "__main__":
    main()
