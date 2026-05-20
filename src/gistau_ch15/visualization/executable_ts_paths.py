from __future__ import annotations

from gistau_ch15.visualization.ts_reconstruction import (
    FallbackTSReconstructor,
    TSPath,
)


class ExecutableTSPathGenerator:
    """Executable T-s generation boundary.

    Future revisions may use backend-generated state stepping while preserving
    deterministic fallback behavior.
    """

    def generate(self) -> list[TSPath]:
        return FallbackTSReconstructor().build_paths()
