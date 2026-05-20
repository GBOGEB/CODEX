from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from semantic_substrate.engines.replay_engine import ReplayEngine


def run_replay(snapshot_id: str | None = None) -> dict:
    engine = ReplayEngine()
    return engine.replay(snapshot_id=snapshot_id)


if __name__ == '__main__':
    print(run_replay())
