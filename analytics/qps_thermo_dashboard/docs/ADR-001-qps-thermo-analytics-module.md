# ADR-001: QPS Thermo Dashboard as Reusable ABACUS Analytics Module

## Status

Accepted

## Context

The QPS user-interface thermo dashboard package is a validated
`SSOT_DERIVATIVE` artifact. The next lifecycle step is to make it reusable for
ABACUS studies without weakening the CONTRACT as the single source of truth.
Static HTML alone is insufficient for controls, helium inventory,
pressure-drop, and digital-twin workflows because those workflows need governed
CSV datasets and repeatable rendering.

## Decision

Implement `analytics/qps_thermo_dashboard` as a self-contained analytics module
with:

1. a stdlib-only builder script;
2. governed CSV datasets with row-level CONTRACT traceability;
3. a six-slide Plotly slideshow dashboard;
4. a dedicated warm-piping dashboard for U/W/S;
5. controls response calculations derived from velocity transit-time envelopes;
6. a governed B-line deep dive from QCELL outlet to QRB interface;
7. Plotly trace metadata for source document, table, figure, and requirement.

The module preserves `CONTRACT` as SSOT and labels generated dashboards and CSVs
as derivative artifacts.

## Consequences

- The dashboard can be regenerated deterministically with one command.
- Plotly provides responsive browser rendering and PNG/SVG export.
- CSV export is available both as files and through the browser UI.
- Warm-piping studies can focus on U/W/S without cold-line A/B/D/E noise.
- Controls engineers receive explicit Reynolds number, volumetric flow,
  residence time, transport delay, effective deadtime, bandwidth, scan-period,
  PID update-period, and filter recommendations for 60 m, 91.5 m, and 151.5 m
  transit envelopes.
- The B-line route has a dedicated pressure/density/velocity/lag page using the
  31 mbar @ 2 K to 26 mbar @ 3.9 K basis.

## Traceability

All generated rows include source fields for `CONTRACT`, the QPS user interface
section, Table 7, Table 9, Figure 3, and the governing controls/warm-piping
requirements. The rendered HTML exposes the same lineage through a visible
traceability badge and Plotly trace metadata.
