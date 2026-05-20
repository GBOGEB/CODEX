from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TSPath:
    name: str
    entropy: list[float]
    temperature: list[float]


class FallbackTSReconstructor:
    """Deterministic T-s path scaffold for review dashboards.

    This module owns the T-s reconstruction boundary. Later revisions can
    replace deterministic paths with backend-generated state trajectories.
    """

    def build_paths(self) -> list[TSPath]:
        return [
            TSPath(
                name="expander path",
                entropy=[90, 108, 132, 160, 190],
                temperature=[80, 58, 36, 18, 5],
            ),
            TSPath(
                name="low temperature path",
                entropy=[45, 60, 82, 115, 165],
                temperature=[12, 8, 5, 3, 2],
            ),
        ]
