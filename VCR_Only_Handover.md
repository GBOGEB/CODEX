# VCR-Only Extract (Cross-Referenced)
This extract mirrors the full artefact pack but filters for the VCR scope. Section references (e.g., §2.1) map to headings in `Full_VCR_Handover.md`.

## Requirements (see §1)
| Req ID | Class | Requirement | Verification | Deliverables | Source | Full Ref |
| --- | --- | --- | --- | --- | --- | --- |
| RTM.001 | C | All serviceable joints shall be /FS (VCR-compatible); no PTFE or elastomer seals in wetted helium service. | Visual inspection + BOM review | P&IDs<br>Line class sheet | MASTER_PATCH §1-§8 | §1 |
| RTM.002 | C | Each /FS remake shall use a new metal gasket with batch traceability and tamper evidence. | Maintenance checklist | Maintenance log<br>Tamper-seal log | MASTER_PATCH §4 & §8 | §1 |
| RTM.003 | C | /FS orientation shall be panel-female and module-male; deviations logged. | Field inspection | Orientation checklist | MASTER_PATCH §2 | §1 |
| RTM.003b | C | Small pneumatic/solenoid pilots shall be fail-open so loss of motive air does not obstruct manual isolation flow. | Functional test | Valve FAT/SAT records | MASTER_PATCH §8 | §1 |
| RTM.004 | A | Leak acceptance shall meet Addendum Table 6 values using EN 13185 / ISO 20485 helium mass-spectrometer methods. | Helium MS leak test | Leak reports | Addendum Table 6; MASTER_PATCH §3 & §8 | §1 |
| RTM.005 | C | DBB plus eductor purge shall achieve residual air ≤0.05 % before breaking the joint. | Procedure witness | Purge log<br>Analyzer log | MASTER_PATCH §3 | §1 |
| RTM.006 | A | QINFRA.S/QRB.S shall be protected at 1.3 bar(a) with PSV capacity ≥200 g/s @ 300 K routed to WCS.LP recovery. | Sizing calculations + certificates | PSV certification dossier | MASTER_PATCH §6 | §1 |
| RTM.007 | C | Provide BD/PSV populations and setpoints as defined above with certified orifice capacity. | Manifest review + certs | BOM_Master.csv<br>Cert pack | MASTER_PATCH §6 | §1 |
| RTM.008 | C | Implement tamper-evident ties and scan-based remake counting for every /FS connection. | Inspection + system audit | Tamper log<br>Maintenance system report | MASTER_PATCH §4 | §1 |
| RTM.009 | A | Install dual helium analyzers (GAP.WCS and GAP.QRB) measuring H₂O and N₂ with ±1 ppm accuracy and ≤±1 ppm/year drift; maintain calibration certificates. | Calibration verification | Analyzer calibration certificates | Addendum analyzer clause; BOM_Master.csv | §1 |

## Quality Controls (see §2)
### ITP snapshot (see §2.1)
| Step | H/W | Acceptance Criteria | Record | Full Ref |
| --- | --- | --- | --- | --- |
| Face-seal orientation check | W | Panel female / module male confirmed | Checklist | §2.1 |
| DBB purge cycle | H | Residual air ≤0.05% and He loss logged | Log sheet | §2.1 |
| Gasket replacement | W | New metal gasket per batch record | Maintenance log | §2.1 |
| Helium leak test | H | Leakage ≤ Table 6 limit | Leak report | §2.1 |
| Tamper seal installation | W | Seal ID recorded and scanned | Photo + scan log | §2.1 |
| PSV/BD certification | H | Setpoint & orifice capacity validated | Cert dossier | §2.1 |
| Analyzer calibration | W | ±1 ppm accuracy / drift verified | Calibration certificate | §2.1 |

### DBB purge focus (see §2.2)
- Residual air target: <=0.05% before breaking any /FS joint.
- Records: purge log, analyzer ppm, helium loss estimate, gasket batch, tamper seal ID, technicians/supervisors.
- Tooling: Venturi eductor or recovery hose; analyzer proof logged in CIS.

### Helium leak testing focus (see §2.3)
- Method: EN 13185 / ISO 20485 helium MS (sniffer/hood or inboard ports).
- Acceptance: Table 6 leak limits (<=1e-9 mbar·L/s unless specified otherwise).
- Records: Tag, joint type, leak rate, instrument ID, personnel, QA archive link to RTM.004.

## BOM elements (see §3)
| Tag | Area | Description | Qty | Full Ref |
| --- | --- | --- | --- | --- |
| BD.QCELL | QCELL | Bursting disc | 60 | §3 |
| BD.QPLANT.HP | WCS.HP | Bursting disc (HP) | 2 | §3 |
| BD.QPLANT.TS | QRB.D/QRB.E | Bursting disc (thermal shield) | 3 | §3 |
| BD.QPLANT.LP | WCS.LP | Bursting disc (LP auxiliaries) | 0 | §3 |
| PSV.QCELL | QCELL | Safety valve population | 180 | §3 |
| PSV.QPLANT.HP | WCS.HP | Safety valve (HP) | 6 | §3 |
| PSV.QPLANT.TS | QRB.D/QRB.E | Safety valve (thermal shield) | 6 | §3 |
| PSV.QPLANT.LP | WCS.LP | Safety valve (LP header) | 4 | §3 |
| PSV.QPLANT.VB | Various | Vacuum breaker | 4 | §3 |
| PSV.QPLANT.S | QINFRA.S | Safety valve (S-line header) | 4 | §3 |
| VAL.ONOFF | WCS/QRB | On/Off valves | 180 | §3 |
| FSU.GASKET.ALL | ALL | Metal gasket kit | >500 | §3 |
| GAP.WCS | WCS | Gas analyzer panel | 1 | §3 |
| GAP.QRB | QRB | Gas analyzer panel | 1 | §3 |
| EDC.QINFRA | UHP Network | Venturi eductor set | 6 | §3 |
| SOL.FAILOPEN | WCS/QRB | Fail-open pilot solenoids | 60 | §3 |

## Vendor hooks (see §4)
- `/FS` fittings & gaskets: Swagelok, Parker Veriflo, FITOK — EUR 2-15 per gasket; EUR 20-120 per body (finish dependent).
- PSVs: Leser, Herose, Advance Valve — DN25-DN50 cryogenic PSVs EUR 400-1,200.
- Bursting discs: REMBE, OsecoElfab, Fike Europe — discs EUR 250-600; holders EUR 400-900.
- Venturi purge hardware: SMC ZH, Piab piINLINE — EUR 20-150.
- Fail-open pilots: ASCO, Bürkert — EUR 100-550 (three-way NO valves).
- Online He analyzers: Michell, Edgetech/PST — dual-channel packages mid four- to low five-figure EUR.

## ADR/OCD tie-ins (see §§5-6)
- ADR-001 enforces /FS policy, DBB purge discipline, tamper tracking, and PSV/BD populations tied to WCS.LP recovery.
- OCD scenarios: warm start-up (analyzers + PSV readiness), maintenance outage (DBB purge + leak test), emergency depressurization/LOOP (S-line directs 200 g/s @ 300 K to WCS.LP with CIS logging).
