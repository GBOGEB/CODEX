# MissionControl Live Federation Ingestion v0.3

## Durable execution edge

`LIVE_TEMPORAL_FEDERATION_INGESTION`

This slice continues from the merged and Pages-proven v0.2.1 control plane. It
does not replay completed atoms and it does not convert UI/render state into
engineering authority.

## Source refresh contract

For every source declared in `source_registry.yaml`:

1. read repository metadata;
2. resolve the exact default-branch head SHA;
3. read only the declared public/authorized topology metadata;
4. materialize `source_status.json` plus the Pages projection;
5. append a temporal control event only when the source head or source status
   changes;
6. if a source cannot be read, retain the last known identity as
   `STALE_CACHE` and continue independent sources.

The append-only source-change event is a projection. It is not an engineering
acceptance event and it cannot promote remote truth.

## Pages boundary

GitHub Pages rebuild is the read-only **source-freshness** refresh boundary. The first 3/3 live pulse is already repository-bound by merged PR #845; this successor does not replace it.

```text
Runtime Release Gate / main
  -> Pages build
  -> ingest_missioncontrol_sources.py
  -> live source-status projection
  -> HTML Federation Control panel
```

A Pages/browser/stream failure does not block repository execution. The
committed fallback projection remains available and is visibly distinguishable
from `FRESH` or `STALE_CACHE`.

Pages does **not** append durable temporal history. Append-only control events
are emitted only by a controlled repository transaction and must then be
committed with exact repo/ref/SHA provenance.

## Federation UI

Panel 6 consumes `docs/data/missioncontrol_source_status.json` and displays:

- repository;
- exact head SHA when available;
- source state (`FRESH`, `STALE_CACHE`, or committed fallback);
- authority role;
- integration mechanism;
- preserved remote/local authority.

## Recovery tuple

```text
repo = GBOGEB/CODEX
branch = mission-control/live-federation-ingestion-v0-3
current_atom = RECURRING_FEDERATION_FRESHNESS_AUTOMATION
completed_predecessor = PR_845_LIVE_FEDERATION_PULSE_3_OF_3
first_red_scope = affected lane only
replay_completed_atoms = false
next_legal_transition =
  exact-head proof
  -> merge/readback
  -> Pages live-refresh proof
  -> bind v0.3 proof receipt / reentry
```

## Governance gate

PR #844 uses the mandatory W003 PR-classification block and must be re-evaluated from a fresh pull-request synchronization event before merge.

## Guards

`authority_transfer=false`

`formal_credit_delta=0`

`engineering_credit_delta=0`

Remote ABACUS execution/DOW authority and cryoplant-project engineering
authority remain remote. CODEX owns only the UI/orchestration/projection
contract for this slice.


## Scheduled refresh

The hourly `missioncontrol-live-federation.yml` probe described in earlier
drafts of this note was never committed. The refresh that exists is the Pages
rebuild itself:

```text
pages.yml: workflow_run (Runtime Release Gate success on a main push)
         | schedule (daily, 05:23 UTC) | workflow_dispatch on main
  -> resolve: the newest main push that passed Runtime Release Gate
  -> build that exact commit, run ingest_missioncontrol_sources.py live
  -> deploy Pages
```

The schedule and manual runs publish the same release-gated commit the last
qualifying push would have published; only the live source projection is
newer. They commit nothing, so they cannot re-trigger any workflow.

`github.token` cannot read the private cryoplant-project repository, so on
Pages that source stays `STALE_CACHE` from the committed fallback unless the
owner provides a read-only token.

## Committed fallback refresh

`mission_control/mycelium/source_status.json` is the committed fallback that
Pages recovers to when a source cannot be read. Refresh it in a reviewed PR
with:

```bash
python scripts/ingest_missioncontrol_sources.py --identity-only --emit-events
python scripts/analyze_missioncontrol_logs.py
python scripts/build_missioncontrol_metrics.py
```

`--identity-only` updates only head identity (`status`, `observed_at`,
`head_sha`, `head_url`, `identity_status`, branch). Curated census and return
fields stay as they were and keep their own `census_*` SHAs; the previous
basis is kept as `curated_measurement_basis`. No repository, pull, issue or
workflow payload is written, so the file stays public metadata only.
`--emit-events` appends one projection-only event per changed source.
