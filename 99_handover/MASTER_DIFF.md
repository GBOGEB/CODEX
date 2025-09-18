# MASTER — Diff Ledger (Redline/Greenline)

Key: `[- deleted -]` (red) • `[+ added +]` (green) • Decision: ✅ Yes / ❌ No / ⏳ Maybe

| Change ID | Where (Anchor → Subclause) | Page | Old text | New text | Decision |
|---|---|---:|---|---|---|
| C01 | Table 1 – Major Interfacing and fluid transport lines → Naming | {auto} | [- QRB-A, QRB-B, QRB-D, QRB-E; QINFRA-U/W/S; WCS-HP/LP/VLP -] | [+ QRB.A, QRB.B, QRB.D, QRB.E; QINFRA.U/W/S; WCS.HP/LP/VLP (optional WCS.R) +] | ⏳ |
| C02 | Warm line interfaces (DN & duties) | {auto} | [- “The QINFRA-S is a safety Line … to the LP suction …” -] | [+ “QINFRA.S (S-line) is the safety/recovery header; QRB.S local header protected at 1.3 bar(a) with capacity for 200 g/s @ 300 K to WCS.LP recovery.” +] | ⏳ |
| C03 | Table 6 – Leakage requirements | {auto} | [- (no explicit /FS practice) -] | [+ “Serviceable joints shall be metal gasket face-seal (/FS, VCR-compatible); new metal gasket at every remake; verification by He MS test vs Table 6.” +] | ⏳ |
| C04 | Purging and conditioning | {auto} | [- Manual purging may be implemented … -] | [+ “Double-block-and-bleed (DBB) with eductor purge: 3-cycle pull-down to ≤50 mbar(a), helium backfill to 1.05 bar(a), analyzer check, then break /FS joint with new gasket; bleed routed to recovery (WCS.LP) or eductor using dry N₂ motive gas.” +] | ⏳ |
| C05 | Measuring points – WCS/QRB (Tables 7–8) | {auto} | [- (no explicit VCR test port) -] | [+ “Where /FS nuts with test ports exist, provide helium mass-spectrometer inboard leak-check ports and calibration tees for PT/AI sampling.” +] | ⏳ |
| C06 | Valve requirements | {auto} | [- (no FO clause) -] | [+ “Small pneumatic/solenoid pilots shall be fail-open so that loss of instrument air does not obstruct manual isolation flow.” +] | ⏳ |
| C07 | Recovery and safety devices | {auto} | [- (counts not specified) -] | [+ “Population: BD = 60 QCELL + 5 QPLANT; PSV = 180 QCELL + 30 QPLANT. Setpoints (abs): QCELL BD 2.0 bar, QPLANT HP BD 18 bar / PSV 16 bar, TS BD 3.5 bar / PSV 4.0 bar, LP PSV 1.3 bar, vacuum breaker PSV 0.95 bar, S-line PSV 1.3 bar sized for ≥200 g/s @ 300 K to WCS.LP.” +] | ⏳ |
| C08 | P&ID legend | {auto} | [- (no /FS annotation) -] | [+ “Add legend delta: /FS = Metal gasket face-seal (VCR-compatible); new gasket each remake; panel side female, module side male.” +] | ⏳ |
| C09 | New chapter insertion (after Table 6) | {auto} | [- — -] | [+ “VCR Face-Seal Policy & Serviceability” chapter (orientation, DBB purge, tamper-evident ties, /FS map, safety population). +] | ⏳ |
| C10 | Tender / vendor references | {auto} | [- — -] | [+ “Vendor triplets with indicative EU pricing for /FS fittings, BD/PSV, eductors, solenoids, analyzers; link to deliverables.” +] | ⏳ |
| C11 | Acceptance testing | {auto} | [- (no /FS remake traceability) -] | [+ “Add /FS make-break & gasket replacement checklist; helium MS record; tamper-tag scan to CIS.” +] | ⏳ |
| C12 | Requirements Traceability Matrix | {auto} | [- — -] | [+ “Insert RTM.001–RTM.008 ‘shall’ statements for /FS policy, purge, leakage, analyzers, S-line protection, tamper control.” +] | ⏳ |

> **How to use:** mark Decision column (✅/❌/⏳). Optional macro `FillMasterDiffPages` (see instructions) can auto-fill page numbers after the table is pasted into the Word master.
