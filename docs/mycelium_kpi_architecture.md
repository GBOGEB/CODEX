# Mycelium / MIP KPI measurement architecture

Mycelium already produces receipts (value report, metrics snapshot, log
analysis, registry, MIP lane register), but until now no single place said
which numbers are KPIs, what each one is for, how it is computed, or what
"good" looks like. This layer adds that, without adding new hand-entered
numbers.

```
receipts (committed / regenerated)          manifest                        report
───────────────────────────────────    ────────────────────────    ──────────────────────────────
executable_value_report.json   ─┐      MANIFEST/                      docs/data/
metrics_snapshot.json           │      MYCELIUM_KPI_MANIFEST.yaml     mycelium_kpi_measurement.json
log_analysis.json               ├──▶   sources · dimensions ──▶       kpis[] · checks[] · summary
executable_integration_registry │      kpis · checks · unlock          red_kpis · withheld_kpis
control_observations.json       │            ▲                         source sha256 fingerprints
MIP/mip_lanes.json, surface     ─┘            │
debt classification (in memory)     scripts/measure_mycelium_kpis.py
```

## Contract

- **Every KPI is bound.** A KPI has a source alias, a path into that source,
  an aggregate (`value`, `len`, `sum`, `sum_keys`, `count_where`,
  `not_null`, `distribution`) and a formula (`value`, `ratio`, `ratio_pct`).
- **Every KPI has a purpose.** It states the question it answers. Its
  dimension states the decision it supports, plus unit, direction, target,
  GREEN/AMBER bands and the DMAIC phase it serves.
- **Measured or withheld.** A missing source, an upstream `WITHHELD` status,
  a null input or a zero denominator gives `WITHHELD` with a reason, never a
  default number. A present source lacking the bound path gives
  `BINDING_ERROR`, and the script exits 1.
- **No composite score.** Bands are control signals, not credit;
  `composite_score` is always `null`.
- **Disagreements are reported.** `checks` compare the same fact across two
  producers and report `FAIL` instead of reconciling. A check only pairs
  values over the same population under the same definition; two measures
  that merely share a name are separate KPIs, not a check.
- **One tested-orphan definition.** A tested orphan is a tested registered
  node with no operational edge and no downstream consumer that is not
  `LIBRARY_REFERENCE_ONLY` (`executable_integration_value_contract.yaml`
  `orphan_policy`). `validate_executable_integration_value.py` evaluates it
  over `executable_integration_registry.yaml`. The metrics snapshot's
  `executable_value` block uses that same registry and evaluator. The debt
  classifier's `TESTED_ORPHAN` class (EXE-05) is a pre-registration triage
  class over the disjoint unregistered population, so it is reported on its
  own and never compared with the registered count.
- **Unbound numbers are named.** `unbound_declared_metrics` lists metric
  files that carry hand-entered scores (currently
  `MANIFEST/PROGRAM_METRICS.yaml`), so they are not mistaken for
  measurements.

## Dimensions

| Dimension | Question |
|---|---|
| execution | Are registered executable assets run, proven and integrated? |
| reach | How far does proven value travel (repository → project → federation → recursive control)? |
| signals | How connected is the graph, and how much of it carries proof? |
| health | Do measured nodes run green, and how much of the graph is observed? |
| dmaic | How many nodes have an evidenced DMAIC phase, and where? |
| mip | Is the MIP kit moving toward its DoV? |
| maturity_scoring | Are maturity and ranking scores computable from real observations? |

Coverage KPIs (e.g. `DMC-01`, `SCR-01`) measure how much of a dimension is
evidenced at all. A withheld field elsewhere becomes an explicit, banded
number here instead of a silent gap.

## Running

```bash
python scripts/measure_mycelium_kpis.py          # write docs/data/mycelium_kpi_measurement.json
python scripts/measure_mycelium_kpis.py --check  # exit 1 if the committed report is stale
```

The report is deterministic, with no wall-clock timestamps. Each source
carries a sha256 fingerprint (CRLF normalised), so a stale report is visible
by comparing fingerprints. The debt classification is always recomputed in
memory from tracked inputs, because its file is an untracked regen
byproduct.

Re-run the measurement after `scripts/regen_missioncontrol_inventory.py`
changes receipts. The script is not yet a regen step, because the Mycelium
CI and reconcile workflows hard-code their output lists.

## Adding a KPI

1. Add an entry under `kpis:` with `id`, `dimension`, `name`, `purpose`,
   `formula`, selectors, `unit`, `direction`, and, unless `info`, a
   `target` and `bands`.
2. Optionally add an `unlock:` line saying what moves it toward target.
3. Run the script and `pytest tests/test_mycelium_kpi_manifest.py`, then
   commit the manifest and the report together.
