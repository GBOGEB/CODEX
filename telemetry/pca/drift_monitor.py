"""W000 federated semantic drift monitor.

Tracks drift between semantic and sequential layers and emits a lightweight
telemetry payload for orchestration gating.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class DriftSnapshot:
    semantic_alignment: float
    temporal_alignment: float
    drift_score: float
    pca_monitor: bool = True


def compute_drift(semantic_alignment: float, temporal_alignment: float) -> DriftSnapshot:
    """Return a bounded drift snapshot.

    Drift score is absolute deviation between semantic and temporal alignment.
    """
    semantic = max(0.0, min(1.0, semantic_alignment))
    temporal = max(0.0, min(1.0, temporal_alignment))
    score = abs(semantic - temporal)
    return DriftSnapshot(
        semantic_alignment=semantic,
        temporal_alignment=temporal,
        drift_score=round(score, 4),
    )


def render_snapshot(snapshot: DriftSnapshot) -> dict:
    """Render snapshot as serializable telemetry."""
    payload = asdict(snapshot)
    payload["state"] = "STABLE" if snapshot.drift_score <= 0.2 else "DRIFTING"
    payload["trace"] = "FEDERATION.RUNTIME.W000"
    return payload


if __name__ == "__main__":
    sample = compute_drift(semantic_alignment=0.85, temporal_alignment=0.55)
    print(render_snapshot(sample))
