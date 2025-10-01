# Full Helium VCR Artefact Pack (All Sections)
Baseline: HELIUM_VCR_UHP_master_applied v1.3.0 (handover_master_applied.glob.yaml, 2025-09-18).

## §1 Requirements (RTM)
Sources: 01_requirements/requirements.json, 01_requirements/RTM.csv.

| Req ID | Class | Requirement | Verification | Deliverables | Source |
| --- | --- | --- | --- | --- | --- |
| RTM.001 | C | All serviceable joints shall be /FS (VCR-compatible); no PTFE or elastomer seals in wetted helium service. | Visual inspection + BOM review | P&IDs<br>Line class sheet | MASTER_PATCH §1-§8 |
| RTM.002 | C | Each /FS remake shall use a new metal gasket with batch traceability and tamper evidence. | Maintenance checklist | Maintenance log<br>Tamper-seal log | MASTER_PATCH §4 & §8 |
| RTM.003 | C | /FS orientation shall be panel-female and module-male; deviations logged. | Field inspection | Orientation checklist | MASTER_PATCH §2 |
| RTM.003b | C | Small pneumatic/solenoid pilots shall be fail-open so loss of motive air does not obstruct manual isolation flow. | Functional test | Valve FAT/SAT records | MASTER_PATCH §8 |
| RTM.004 | A | Leak acceptance shall meet Addendum Table 6 values using EN 13185 / ISO 20485 helium mass-spectrometer methods. | Helium MS leak test | Leak reports | Addendum Table 6; MASTER_PATCH §3 & §8 |
| RTM.005 | C | DBB plus eductor purge shall achieve residual air ≤0.05 % before breaking the joint. | Procedure witness | Purge log<br>Analyzer log | MASTER_PATCH §3 |
| RTM.006 | A | QINFRA.S/QRB.S shall be protected at 1.3 bar(a) with PSV capacity ≥200 g/s @ 300 K routed to WCS.LP recovery. | Sizing calculations + certificates | PSV certification dossier | MASTER_PATCH §6 |
| RTM.007 | C | Provide BD/PSV populations and setpoints as defined above with certified orifice capacity. | Manifest review + certs | BOM_Master.csv<br>Cert pack | MASTER_PATCH §6 |
| RTM.008 | C | Implement tamper-evident ties and scan-based remake counting for every /FS connection. | Inspection + system audit | Tamper log<br>Maintenance system report | MASTER_PATCH §4 |
| RTM.009 | A | Install dual helium analyzers (GAP.WCS and GAP.QRB) measuring H₂O and N₂ with ±1 ppm accuracy and ≤±1 ppm/year drift; maintain calibration certificates. | Calibration verification | Analyzer calibration certificates | Addendum analyzer clause; BOM_Master.csv |

## §2 Quality & Test Planning
### §2.1 Inspection & Test Plan (ITP_HE_VCR.csv)
| Step | H/W | Acceptance Criteria | Reference | Record |
| --- | --- | --- | --- | --- |
| Face-seal orientation check | W | Panel female / module male confirmed | MASTER_PATCH §2 | Checklist |
| DBB purge cycle | H | Residual air ≤0.05% and He loss logged | PROC_DBBA_Purge | Log sheet |
| Gasket replacement | W | New metal gasket per batch record | MASTER_PATCH §8 | Maintenance log |
| Helium leak test | H | Leakage ≤ Table 6 limit | PROC_He_LeakTest_ISO20485 | Leak report |
| Tamper seal installation | W | Seal ID recorded and scanned | MASTER_PATCH §4 | Photo + scan log |
| PSV/BD certification | H | Setpoint & orifice capacity validated | MASTER_PATCH §6 | Cert dossier |
| Analyzer calibration | W | ±1 ppm accuracy / drift verified | RTM.004 | Calibration certificate |

### §2.2 Procedure: Double-Block-and-Bleed (DBB) Purge (PROC_DBBA_Purge.md)
**Scope:** Applies to all serviceable metal gasket face-seal joints on QRB.A/B/D/E, QINFRA.U/W/S, WCS.HP/LP/VLP (and optional WCS.R) lines.

1. **Preparation**  
   - Verify analyzer availability (H₂O/N₂ ppm).  
   - Confirm tamper seal ID and gasket batch in log.  
   - Connect Venturi eductor (dry N₂ motive) or recovery hose to bleed port.
2. **Isolation**  
   - Close upstream and downstream diaphragm valves (DBB).  
   - Open bleed leg to eductor/recovery.
3. **Evacuation & Backfill**  
   - Pull cavity to ≤50 mbar(a) equivalent.  
   - Close bleed; backfill with helium to 1.05 bar(a).  
   - Vent to WCS.LP.  
   - Repeat steps 3a–3c three times.
4. **Verification**  
   - Sample with analyzer; residual air ≤0.05 %.  
   - Record He loss estimate (approx. 1.5 L STP for 0.5 L cavity per cycle).
5. **Break & Re-make**  
   - Break joint; replace gasket (new metal gasket per alloy plan).  
   - Assemble per torque/turn; install tamper seal.
6. **Testing & Records**  
   - Perform helium MS leak test to Table 6 acceptance.  
   - Update maintenance record with purge cycles, analyzer ppm, gasket batch, tamper seal ID, technician and supervisor signatures.
 – Update purge log with tag, technician, residual %, helium loss, analyzer ID, gasket batch, and tamper seal ID

### §2.3 Procedure: Helium Mass-Spectrometer Leak Test (PROC_He_LeakTest_ISO20485.md)
**Scope:** All /FS joints, welded closures, and safety-device interfaces subject to Table 6 leakage acceptance.

1. **Pre-test**  
   - Verify test instrument calibration (ISO/IEC 17025 certificate).  
   - Perform background check (<1×10⁻¹⁰ mbar·L/s He).
2. **Method**  
   - Apply tracer helium to connection (sniffer or hood) per EN 13185.  
   - For nuts with test ports, use inboard MS port.  
   - Record maximum indicated leak rate.
3. **Acceptance**  
   - Compare to Table 6 limits (≤1×10⁻⁹ mbar·L/s He per connection unless otherwise specified).  
   - Re-test after tightening if necessary (new gasket if joint is opened).
4. **Records**  
   - Capture tag ID, joint type, test method, leak rate, instrument ID, technician, supervisor sign-off.  
   - Store log in quality archive and link to RTM.004.

## §3 Bill of Materials Snapshot (BOM_Master.csv)
| Tag | Area | Description | Setpoint/Rating | Qty | Notes |
| --- | --- | --- | --- | --- | --- |
| BD.QCELL | QCELL | Bursting disc | 2.0 bar(a) | 60 | Cold users; route to recovery/tunnel vent |
| BD.QPLANT.HP | WCS.HP | Bursting disc (HP) | 18 bar(a) | 2 | Compressor discharge / ORS envelope |
| BD.QPLANT.TS | QRB.D/QRB.E | Bursting disc (thermal shield) | 3.5 bar(a) | 3 | Supply/return branches |
| BD.QPLANT.LP | WCS.LP | Bursting disc (LP auxiliaries) | 1.3 bar(a) | 0 | Use PSV per spec |
| PSV.QCELL | QCELL | Safety valve population | (varies) | 180 | Allocate per QCELL functions |
| PSV.QPLANT.HP | WCS.HP | Safety valve (HP) | 16 bar(a) | 6 | Compressor trains & headers |
| PSV.QPLANT.TS | QRB.D/QRB.E | Safety valve (thermal shield) | 4.0 bar(a) | 6 | Warm TS loops |
| PSV.QPLANT.LP | WCS.LP | Safety valve (LP header) | 1.3 bar(a) | 4 | Protect LP header |
| PSV.QPLANT.VB | Various | Vacuum breaker | 0.95 bar(a) | 4 | Thin-wall vessels |
| PSV.QPLANT.S | QINFRA.S | Safety valve (S-line header) | 1.3 bar(a) | 4 | ≥200 g/s He @300 K to WCS.LP |
| VAL.ONOFF | WCS/QRB | On/Off valves | PN rated | 180 | 1 welded bodies; /FS at instrument take-offs" |
| FSU.GASKET.ALL | ALL | Metal gasket kit | n/a | >500 | SS primary; Ni/Cu by temperature |
| GAP.WCS | WCS | Gas analyzer panel | ppm range | 1 | Moisture/N₂ analyzer; return to WCS.LP |
| GAP.QRB | QRB | Gas analyzer panel | ppm range | 1 | Cold-box room analyzer; return to WCS.LP |
| EDC.QINFRA | UHP Network | Venturi eductor set | ΔP motive | 6 | Dry N₂ motive purge blocks |
| SOL.FAILOPEN | WCS/QRB | Fail-open pilot solenoids | 24 VDC | 60 | Manual isolation assist |

## §4 Vendor Landscape (VENDOR_COSTS.md)
# Vendor Triplets & Indicative EU Pricing

All costs are ballpark ranges pulled from publicly available catalog or distributor listings to support early tender benchmarking. Final quotations from suppliers shall govern the contract baseline.

## Face-Seal (/FS) Fittings and Gaskets
- **Swagelok** (VCR® catalog; EU sales centres). Example public list prices show metal gaskets and bodies depending on finish/cleaning.  
- **Parker Veriflo** (VacuSeal™ series; EU distributors). Online listings for standard glands, bodies, and gaskets.  
- **FITOK** (FR metal gasket face-seal; FITOK GmbH, DE). Catalogue pricing available via EU branch.

Indicative retail ranges (1/4"–1/2" sizes):
- Metal gaskets (SS/Ni/Cu): ~€2–€15 each (varies by alloy and packaging).  
- Female/male bodies and weld glands: ~€20–€120 each (standard vs EP finish).

## Pressure Safety Valves (PSV)
- **Leser** (Germany) – High-performance spring-loaded PSVs, DN25–DN80.  
- **Herose** (Germany) – Cryogenic PSVs suitable for helium service.  
- **Advance Valve / EU stockists** – Distribute Leser/Herose lines.

Indicative range for DN25–DN50 cryogenic PSVs: ~€400–€1,200 each depending on materials, certification, and cleaning.

## Bursting Discs (BD)
- **REMBE** (Germany) – BT/BT-KUB series; compatible holders for DN80–DN150.  
- **OsecoElfab** (UK/EU) – OP/DC forward-acting discs; example DN100 disc ~€499 (public retail).  
- **Fike Europe** (Belgium) – Cryogenic bursting discs; pricing on request.

Typical range: disc €250–€600; holder €400–€900 depending on size and material grade.

## Venturi Eductors & Purge Hardware
- **SMC** (ZH series vacuum ejectors) – dry nitrogen motive; ~€20–€150.  
- **Piab** (piINLINE® eductors) – configurable orifices; similar pricing.

## Fail-Open Pilot Solenoids
- **ASCO** / **Bürkert** three-way NO valves (1/4" instrument-air) – ~€100–€550 depending on materials and certification.

## Online He Purity Analyzers
- **Michell Instruments** (Easidew moisture transmitter) – ~€2.7k for ppm H₂O transmitters.  
- **Edgetech Instruments** / **Process Sensing Technologies** – trace moisture and N₂/Ar analyzers (upper four-to-low five-figure packages when dual-channel with sample conditioning).

> **Note:** Apply vendor-specific cleaning (e.g., SC-01) and certification costs when converting to project budgets.

## §5 Architecture Decision Record (ADR/ADR.md)
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

## §6 Operational Concept Background (OCD/OCD.md)
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
