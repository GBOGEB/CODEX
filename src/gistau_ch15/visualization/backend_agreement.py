from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgreementMatrix:
    backends: list[str]
    tuples: list[str]
    values: list[list[float]]


class BackendAgreementBuilder:
    """Deterministic agreement scaffold.

    Future revisions will compute agreement metrics from executable backend
    comparison outputs.
    """

    def build(self) -> AgreementMatrix:
        return AgreementMatrix(
            backends=["fallback", "coolprop", "refprop", "hepak"],
            tuples=[
                "T00 property",
                "T02 saturation",
                "T04 expander",
                "T05 compressor",
            ],
            values=[
                [0.62, 0.88, 1.00, 0.95],
                [0.30, 0.72, 0.86, 1.00],
                [0.45, 0.78, 0.91, 0.96],
                [0.28, 0.70, 0.89, 1.00],
            ],
        )
