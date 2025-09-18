# ADR-001 — /FS Policy, Safety Populations, and Dot Line Naming

## Context
The Addendum II – Cryoplant Technical Requirements mandates Table 6 helium leak limits, dual analyzer coverage (compressor room & cold-box room), warm-line interfaces with DN150 S-line routed to WCS.LP, and minimized helium inventory loss. Servicing needs require replaceable joints without compromising purity.

## Decision
Adopt metal gasket face-seal (/FS, VCR-compatible) joints for serviceable warm modules, enforce panel female / module male orientation, implement DBB + eductor purge with residual ≤0.05 %, deploy tamper-evident seals, and formalize safety device populations (BD 65, PSV 210) with setpoints per subsystem. Rename SBS lines using dot notation (QRB.A/B/D/E, QINFRA.U/W/S, WCS.HP/LP/VLP/WCS.R).

## Rationale
- Preserves helium Grade 5.0 purity while allowing modular maintenance.
- Aligns with OEM leak performance (≤10⁻⁹ mbar·L/s) and Table 6 acceptance values.
- DBB purge minimizes helium losses (~1.5 L per service) and meets analyzer thresholds.
- Dot notation harmonizes with control system tagging and reduces dash confusion in ICS exports.
- Safety populations ensure QINFRA.S → WCS.LP recovery maintains 200 g/s @ 300 K capacity at 1.3 bar(a).

## Consequences
- Requires stocking of metal gaskets (SS/Ni/Cu) and tamper seals.
- Additional eductor skids and analyzer validation steps at maintenance start/finish.
- PSV/BD sizing calculations must be updated to reflect new setpoints and flow assumptions.
- P&ID legend updated with /FS note and dot notation; training required for drafting team.

## Status
Proposed baseline v1.3.0 — pending stakeholder approval via MASTER_DIFF decisions.
