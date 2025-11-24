

# ADR-001: /FS Policy, Safety Populations, and SBS Integration

## Context
- Addendum II – Cryoplant Technical Requirements mandates Table 6 leakage limits, helium recovery via QINFRA.S → WCS.LP, analyzer coverage in the compressor and cold-box rooms, and SBS naming for warm lines (QINFRA.U/W/S, QRB.A/B/D/E, WCS.HP/LP/VLP).
- Serviceable joints must allow maintenance without compromising helium purity (Grade 5.0) or leak performance.
- Relief network sizing requires explicit BD/PSV populations and setpoints to protect QRB.S, QINFRA.S, and downstream recovery.

## Decision
1. Adopt metal gasket face-seal (/FS, VCR-compatible) joints for all warm serviceable interfaces while keeping main spines welded.
2. Enforce orientation: fixed infrastructure female, removable modules male; track deviations.
3. Implement DBB + bleed to recovery or Venturi eductor with residual air target ≤0.05%.
4. Install tamper-evident seals and scan workflow to track remake counts and gasket batches.
5. Freeze BD/PSV populations and setpoints (BD 65; PSV 210) with S-line PSV capacity ≥200 g/s @ 300 K at 1.3 bar(a) setpoint, tying discharge to WCS.LP.

## Status
Accepted – baseline v1.3.0 (2025-09-18).

## Consequences
- Simplifies maintenance: predictable female seats on panels, sacrificial male noses on LRUs.
- Purge procedure minimises helium loss and supports analyzer validation.
- Tamper tracking enforces single-use gaskets and leak integrity.
- Relief design references align with API 520/521 and ISO 21013-1/-2, ensuring compliance for QRB.S/QINFRA.S events.

## Alternatives Considered
- Retain legacy dash naming (legacy “QRB-A” style) – rejected to align with SBS dot notation (QRB.A, QINFRA.S, WCS.HP, etc.).
- Allow elastomer/PTFE back-up seals – rejected (contamination risk and non-conformance to Addendum purity requirement).  
- Rely solely on welded joints – rejected (does not support modular replacement of analyzers/instruments).

## Related Requirements
- RTM.001–RTM.008 (see 01_requirements/RTM.csv).  
- Table 6 leakage acceptance; Tables 7–8 measuring points.  
- Warm line interface section (DN150 QINFRA.S tie to WCS.LP).

## Risks & Mitigations
- **Risk:** Air ingress during maintenance on sub-atmospheric segments.  
  **Mitigation:** DBB purge with eductor plus analyzer verification; helium guard per Addendum.  
- **Risk:** PSV sizing misalignment with recovery capacity.  
  **Mitigation:** Certified calculations per API/ISO and documentation in PSV dossier.  
- **Risk:** Failure to replace gaskets.  
  **Mitigation:** Tamper wire + scan workflow and maintenance checklist hold point.

## SBS Mapping
- `/FS` joints present in: WCS analyzer panels & service tees; QRB warm panel & INVAC feedthroughs; QINFRA.U/W/S service connections; storage vessel sampling spools.
- All other SBS segments remain welded (cryogenic cold mass, main headers, S-line backbone).

