# Dynamic ingestion v0.2

`scripts/build_missioncontrol_graph.py` upgrades the Mycelium graph from a
hand-maintained snapshot to a build-time materialized view of governed public
GitHub metadata.

The source contract is `mission_control/mycelium/sources.json`.

Live mode:
```bash
python scripts/build_missioncontrol_graph.py
```

Deterministic CI mode:
```bash
MISSIONCONTROL_NOW=2026-09-30T10:00:00+00:00 \
python scripts/build_missioncontrol_graph.py \
  --fixture tests/fixtures/missioncontrol_github_public_metadata.json
```

Only repository identity, exact default-branch SHA and open-PR topology are
ingested. Remote engineering state is not promoted. If a live source is
unavailable, the last good graph node is retained and marked
`*_STALE_SOURCE`; unrelated sources continue.
