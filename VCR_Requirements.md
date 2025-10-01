# VCR Requirements Trace

Baseline: HELIUM_VCR_UHP_master_applied v1.3.0 (handover_master_applied.glob.yaml, dated 2025-09-18).

Sources: 01_requirements/requirements.json, 01_requirements/RTM.csv.

| Req ID | Class | Requirement | Verification | Deliverables | Source |
| --- | --- | --- | --- | --- | --- |
| RTM.001 | C | All serviceable joints shall be /FS (VCR-compatible); no PTFE or elastomer seals in wetted helium service. | Visual inspection + BOM review | P&IDs<br>Line class sheet | MASTER_PATCH Sec 1-8 |
| RTM.002 | C | Each /FS remake shall use a new metal gasket with batch traceability and tamper evidence. | Maintenance checklist | Maintenance log<br>Tamper-seal log | MASTER_PATCH Sec 4 & Sec 8 |
| RTM.003 | C | /FS orientation shall be panel-female and module-male; deviations logged. | Field inspection | Orientation checklist | MASTER_PATCH Sec 2 |
| RTM.003b | C | Small pneumatic/solenoid pilots shall be fail-open so loss of motive air does not obstruct manual isolation flow. | Functional test | Valve FAT/SAT records | MASTER_PATCH Sec 8 |
| RTM.004 | A | Leak acceptance shall meet Addendum Table 6 values using EN 13185 / ISO 20485 helium mass-spectrometer methods. | Helium MS leak test | Leak reports | Addendum Table 6; MASTER_PATCH Sec 3 & Sec 8 |
| RTM.005 | C | DBB plus eductor purge shall achieve residual air <=0.05% before breaking the joint. | Procedure witness | Purge log<br>Analyzer log | MASTER_PATCH Sec 3 |
| RTM.006 | A | QINFRA.S/QRB.S shall be protected at 1.3 bar(a) with PSV capacity >=200 g/s @ 300 K routed to WCS.LP recovery. | Sizing calculations + certificates | PSV certification dossier | MASTER_PATCH Sec 6 |
| RTM.007 | C | Provide BD/PSV populations and setpoints as defined above with certified orifice capacity. | Manifest review + certificates | BOM_Master.csv<br>Certification pack | MASTER_PATCH Sec 6 |
| RTM.008 | C | Implement tamper-evident ties and scan-based remake counting for every /FS connection. | Inspection + system audit | Tamper log<br>Maintenance system report | MASTER_PATCH Sec 4 |
| RTM.009 | A | Install dual helium analyzers (GAP.WCS and GAP.QRB) measuring H2O and N2 with +/-1 ppm accuracy and <=1 ppm/year drift; maintain calibration certificates. | Calibration verification | Analyzer calibration certificates | Addendum analyzer clause; BOM_Master.csv |

Notes:
- Deliverable titles mirror RTM.csv entries to keep CIS evidence tags consistent.
- Source shorthand "MASTER_PATCH Sec X" matches the patch blocks enumerated in 99_handover/MASTER_PATCH.md.
