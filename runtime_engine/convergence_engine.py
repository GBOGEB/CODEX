from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
from typing import List


@dataclass
class WaveState:
    wave: str
    completion: float
    score_before: float
    score_after: float

    @property
    def delta(self) -> float:
        return self.score_after - self.score_before


class ConvergenceEngine:
    def __init__(self, states: List[WaveState]):
        self.states = states

    def average_delta(self) -> float:
        return round(mean([s.delta for s in self.states]), 2)

    def convergence_factor(self) -> float:
        deltas = [s.delta for s in self.states]
        if not deltas:
            return 0.0
        return round(deltas[-1] / deltas[0], 3)

    def aggregate_completion(self) -> float:
        return round(mean([s.completion for s in self.states]), 2)

    def stabilization_index(self) -> float:
        deltas = [s.delta for s in self.states]
        descending = all(a >= b for a, b in zip(deltas, deltas[1:]))
        return 1.0 if descending else 0.5

    def export(self, output_path: Path) -> None:
        payload = {
            'waves': [asdict(s) | {'delta': s.delta} for s in self.states],
            'metrics': {
                'average_delta': self.average_delta(),
                'convergence_factor': self.convergence_factor(),
                'aggregate_completion': self.aggregate_completion(),
                'stabilization_index': self.stabilization_index(),
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


if __name__ == '__main__':
    runtime_states = [
        WaveState('W1', 15, 32, 48),
        WaveState('W2', 20, 48, 62),
        WaveState('W3', 20, 62, 74),
        WaveState('W4', 20, 74, 82),
        WaveState('W5', 20, 82, 87),
        WaveState('W6', 12, 87, 90),
        WaveState('W7', 8, 90, 92),
    ]

    engine = ConvergenceEngine(runtime_states)
    engine.export(Path('runtime_output/convergence_metrics.json'))

    print('Convergence metrics exported.')
