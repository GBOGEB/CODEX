from __future__ import annotations

from semantic_substrate.engines.replay_engine import ReplayEngine


def run_replay(snapshot_id: str | None = None) -> dict:
    engine = ReplayEngine()
    return engine.replay(snapshot_id=snapshot_id)


if __name__ == '__main__':
    print(run_replay())
