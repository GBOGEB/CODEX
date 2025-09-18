# Operational Concept Document: /FS Serviceability & Testing

## 1. Stakeholder & User Requirements
- **StR.HE.Purity:** Maintain He 5.0 purity at all removable interfaces (from Addendum II).  
- **StR.HE.Leak:** Meet Table 6 leakage limits under ambient and standby conditions.  
- **StR.Recovery:** Route relief and purge flows to WCS.LP recovery via QINFRA.S.  
- **UR.Serviceability:** Operators shall replace analyzers, transmitters, and purge modules without compromising purity.  
- **UR.Traceability:** Maintenance shall log every /FS make-break, gasket batch, and tamper seal ID.

## 2. Scenarios
| Scenario | Description | Key /FS Actions |
|---|---|---|
| Warm stop | Transition QRB.A/B and WCS headers to standby | Perform DBB purge on open points; verify analyzers |
| Thermal shield standby | Maintain QRB.D/E loops at standby temps | Monitor PSV/BD readiness; check purge panels |
| 4.5 K standby | Cold box isolated, still cold | Keep INVAC feedthrough /FS closed and tagged |
| 2 K standby | Sub-atm regions guarded | Maintain helium guard; no /FS openings without purge permit |
| 2 K operation | Full load | Continuous analyzer monitoring; S-line PSV armed |

## 3. Operations Concept
- **Start-up:** Confirm PSV/BD certification, analyzers calibrated, tamper seals intact.  
- **Normal operation:** Monitor KPIs (He loss/day, leak per joint, purge residual).  
- **Maintenance:** Execute DBB purge, replace gasket, log data, run helium leak test.  
- **Abnormal:** If purge residual >0.05 %, repeat cycle; if PSV lifts on QINFRA.S, log mass-flow event and inspect BD/PSV population.

## 4. Interfaces & Dependencies
- ICS tags for analyzers, purge valves, PSV switches integrate via ISA-5.1 naming.  
- Maintenance system receives tamper-seal scan data and populates RTM.002/008 evidence.  
- Recovery skid (WCS.LP/WCS.R) handles eductor exhaust and S-line flows.

## 5. Verification & Validation Mapping
- FAT: P&ID compliance, DBB purge demonstration, tamper seal traceability, PSV certification review.  
- SAT: Helium leak tests, analyzer performance verification, recovery integration tests, KPI initialization.

## 6. Transition to Operations
- Handover bundle includes MASTER_DIFF, MASTER_PATCH, RTM, ITP, procedures, vendor costs, ADR, OCD, .glob script.  
- Update baseline tag (SEED_20250918) post-approval.
