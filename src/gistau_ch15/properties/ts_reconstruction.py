from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

from .base import State


@dataclass(frozen=True)
class ProcessNode:
    node_id: str
    label: str
    state: State


@dataclass(frozen=True)
class ProcessSegment:
    segment_id: str
    process_type: str
    start_node: str
    end_node: str
    notes: str = ""


@dataclass(frozen=True)
class ReconstructionResult:
    cycle_name: str
    nodes: list[ProcessNode]
    segments: list[ProcessSegment]


class TSReconstruction:
    """Thermodynamic path reconstruction scaffold.

    Phase K foundation layer for:
    - compressor trajectories,
    - JT expansion lines,
    - expander entropy paths,
    - cold-box process chains,
    - cryoplant replay generation.
    """

    def reconstruct(
        self,
        cycle_name: str,
        nodes: Iterable[ProcessNode],
        segments: Iterable[ProcessSegment],
    ) -> ReconstructionResult:
        return ReconstructionResult(
            cycle_name=cycle_name,
            nodes=list(nodes),
            segments=list(segments),
        )

    @staticmethod
    def as_dict(result: ReconstructionResult) -> dict:
        return {
            "cycle_name": result.cycle_name,
            "nodes": [asdict(n) for n in result.nodes],
            "segments": [asdict(s) for s in result.segments],
        }
