# Operational Concept — /FS Serviceability & Testing

## Scenarios (aligned to Addendum II)
1. Warm stop / start (QRB.A/B warm loops).  
2. Thermal shield standby (QRB.D/E).  
3. 4.5 K standby (WCS.HP to QINFRA.U).  
4. 2 K standby & operation (QRB.E + INVAC interfaces).  
5. Abnormal event: S-line relief to WCS.LP with recovery.

## User Stories → Requirements
- **Maintenance tech** swaps analyzer module: needs DBB purge, analyzer check, new gasket, tamper logging → RTM.001, RTM.002, RTM.005, RTM.008.
- **Operations engineer** monitors S-line relief: ensures PSV certificate and data logging → RTM.006, RTM.007.
- **Instrumentation lead** updates P&IDs: uses dot notation and /FS legend → RTM.001, P&ID deliverables.

## Operational Steps
1. Plan intervention (review diff decisions, confirm spare kits).  
2. Execute DBB purge procedure (PROC_DBBA_Purge.md).  
3. Replace module, torque /FS joint, apply tamper seal.  
4. Perform leak test (PROC_He_LeakTest_ISO20485.md).  
5. Update CIS with remake count, analyzer results, He loss estimate.  
6. Review KPIs (He loss/day, leak per joint, PSV readiness) in quarterly QA meeting.

## Support Systems
- CIS / historian for leak logs and tamper scan data.  
- Analyzer DAS (two analyzers: GAP.WCS, GAP.QRB).  
- Recovery routing: QINFRA.S → WCS.LP; WCS.R optional future tie-in.

## Maintenance Windows & Constraints
- QRB cold sections require warm-up or isolation to warm panel via CF↔FS adapters.  
- FO solenoid pilots default valves to safe-open on air failure; manual intervention required to close.  
- 4 K / 2 K vessels: ensure BD/PSV accessible; maintain spare discs in clean storage.

## Outputs & Deliverables
- Signed purge and leak logs.  
- Updated RTM trace with closure evidence.  
- KPI dashboard updates (DMAIC Control phase).  
- Handover bundle (MASTER_DIFF, MASTER_PATCH, RTM.csv, ITP, procedures, P&ID sheets).
