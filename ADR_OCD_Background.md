# ADR & OCD Background (Full Text)

## ADR-001 (/FS Policy, Safety Populations, SBS Integration)
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
- Retain legacy dash naming (QRB-A, etc.) – rejected to align with SBS dot notation.  
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

## Operational Concept Document Extract (/FS Serviceability & Testing)
# Operational Concept Document – /FS Serviceability & Testing

## 1. Purpose
Describe how operators, maintenance teams, and automated controls manage metal gasket face-seal (/FS) assemblies within the helium cryoplant while preserving Grade 5.0 purity, Table 6 leakage limits, and helium recovery targets.

## 2. Stakeholders & Roles
- **Operations crew:** Execute start-up, normal run, shutdown, and emergency procedures; initiate purge cycles.  
- **Maintenance technicians:** Perform /FS make-break, gasket replacement, tamper-seal management, leak testing.  
- **Reliability engineering:** Monitor MTBF, purge metrics, KPI dashboard.  
- **Control system (CIS):** Provides prompts, tracks tamper scans, logs analyzer data, enforces interlocks.

## 3. Operational Scenarios
1. **Warm start-up:** Pressurise QINFRA.U/W/S, verify analyzers (GAP.WCS, GAP.QRB), check PSV/BD readiness (setpoints).  
2. **Thermal-shield standby:** Maintain TS loops via QRB.D/QRB.E; DBB purge available for any module swap.  
3. **4.5 K standby / 2 K standby:** Monitor relief valves on QRB.S; maintain helium guard; confirm DBB purge readiness for interventions.  
4. **2 K operation:** Continuous analyzer monitoring; S-line PSV status; helium loss KPI tracked daily.  
5. **Maintenance outage:** Execute DBB purge, replace gaskets, perform leak test, log tamper info.  
6. **Emergency depressurisation / LOOP:** Follow Addendum event tree; S-line directs 200 g/s @300 K to WCS.LP; CIS records flow and helium recovery volumes.

## 4. User Stories → Requirements
- **US-OPS-01:** As an operator, I need a standard purge workflow so helium purity remains ≥99.999% after maintenance. → RTM.005.  
- **US-MAINT-02:** As maintenance, I need tamper seals and logs to prove new gasket installation. → RTM.002 & RTM.008.  
- **US-RELIAB-03:** As reliability engineering, I need analyzer data and helium loss metrics to maintain KPI ≤1 Nm³/day. → RTM.004 + KPI dashboard.  
- **US-SAFETY-04:** As safety manager, I require PSV/BD population and sizing data to certify S-line performance. → RTM.006 & RTM.007.  
- **US-CONTROL-05:** As CIS owner, I require fail-open pilots so loss of air does not block manual valves. → RTM.003b.

## 5. Interfaces
- **Mechanical:** `/FS` joints located at WCS panels, QRB warm panels, analyzer spools, storage sampling ports.  
- **Process:** QINFRA.S / QRB.S tie to WCS.LP for recovery; analyzers loop back to LP.  
- **Electrical/Controls:** Instrument air (fail-open), DO/DI for valves, AO for MFC, analyzer Ethernet/OPC-UA to CIS.  
- **Data:** Tamper scan IDs, purge logs, leak test results stored in CIS/QA databases.

## 6. Operational Constraints
- No PTFE or elastomer seals in wetted helium service.  
- Analyzer accuracy ±1 ppm with drift ≤±1 ppm/year; calibration at FAT/SAT.  
- Helium loss KPI ≤1 Nm³/day steady state; ≤1% per abnormal event with recovery strategy.  
- Residual air after purge ≤0.05% prior to break-in.  
- Relief devices certified for setpoint and capacity; S-line maintained at 1.3 bar(a).

## 7. Support & Maintenance
- Spare gasket kits, nuts, and select bodies maintained per BOM_Master.csv.  
- Scheduled verification of eductor motive pressure and solenoid fail-open function.  
- Quarterly review of purge logs, leak reports, and tamper seal counts; feed into DMAIC control loop.

## 8. Data & Logging
- CIS captures: purge cycle metrics, analyzer ppm data, helium losses, PSV/BD activations, tamper seal scans.  
- QA archive stores: leak test reports, calibration certificates, PSV/BD certificates, RTM compliance evidence.

## 9. Handover & Training
- Provide operators with PID symbol cheat-sheet and assembly previews.  
- Train maintenance on DBB purge and tamper sealing.  
- Conduct dry-run of S-line relief scenario verifying 200 g/s capability and WCS.LP recovery response.
