# VCR Quality & Procedure Extract

Artifacts referenced: 04_quality/ITP_HE_VCR.csv, 04_quality/PROC_DBBA_Purge.md, 04_quality/PROC_He_LeakTest_ISO20485.md.

## 1. Inspection & Test Plan (Hold/Witness Summary)
| Step | H/W | Acceptance Criteria | Reference | Record |
| --- | --- | --- | --- | --- |
| Face-seal orientation check | W | Panel female / module male confirmed | MASTER_PATCH Sec 2 | Checklist |
| DBB purge cycle | H | Residual air <=0.05% and He loss logged | PROC_DBBA_Purge | Log sheet |
| Gasket replacement | W | New metal gasket per batch record | MASTER_PATCH Sec 8 | Maintenance log |
| Helium leak test | H | Leakage <= Table 6 limit | PROC_He_LeakTest_ISO20485 | Leak report |
| Tamper seal installation | W | Seal ID recorded and scanned | MASTER_PATCH Sec 4 | Photo + scan log |
| PSV/BD certification | H | Setpoint & orifice capacity validated | MASTER_PATCH Sec 6 | Cert dossier |
| Analyzer calibration | W | +/-1 ppm accuracy / drift verified | RTM.004 | Calibration certificate |

## 2. Procedure Highlights
### 2.1 DBB Purge (PROC_DBBA_Purge.md)
| Sequence | Key Actions |
| --- | --- |
| Preparation | Verify analyzer availability, tamper seal ID, and gasket batch; connect Venturi eductor or recovery hose. |
| Isolation | Close upstream and downstream diaphragm valves and open the bleed leg to the eductor/recovery line. |
| Evacuation & backfill | Pump down to <=50 mbar(a), backfill with helium to 1.05 bar(a), vent to WCS.LP, repeat three times. |
| Verification | Sample with analyzer and confirm residual air <=0.05%; record helium loss estimate. |
| Break & re-make | Break joint, install new metal gasket, reassemble per torque/turn, install tamper seal. |
| Testing & records | Perform helium MS leak test, update maintenance and purge logs with all IDs and signatures. |

### 2.2 Helium Mass-Spectrometer Leak Test (PROC_He_LeakTest_ISO20485.md)
| Phase | Key Actions |
| --- | --- |
| Pre-test | Verify ISO/IEC 17025 calibration and background <1e-10 mbar*L/s He. |
| Method | Apply tracer helium (sniffer/hood or inboard port) per EN 13185 and log maximum leak rate. |
| Acceptance | Compare to Table 6 limits (<=1e-9 mbar*L/s per connection unless noted); re-test after tightening as needed. |
| Records | Capture tag, joint type, method, leak rate, instrument ID, personnel, and store in QA archive linked to RTM.004. |

## 3. Requirement-to-Artifact Map
| Requirement(s) | QA / Ops Artifact Hook |
| --- | --- |
| RTM.001/002/003 | Orientation checklist; Maintenance log; Tamper-seal log |
| RTM.004/005 | PROC_He_LeakTest_ISO20485; PROC_DBBA_Purge; ITP_HE_VCR |
| RTM.006/007 | BOM_Master.csv; PSV certificate dossier; ITP hold points |
| RTM.008/009 | Tamper log; Analyzer calibration certificates; CIS audit trail |

## 4. Implementation Guidance
- Keep analyzer availability, residual air proofs, and helium loss estimations logged in the same maintenance entry to satisfy RTM.005 evidence.
- Treat Hold points (H) as stop works; secure QA sign-off before progressing to next step.
- Leak testing and purge logs shall be cross-linked to CIS entries referenced in RTM.004 / RTM.005 to keep traceability intact.
