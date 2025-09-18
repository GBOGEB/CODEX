# MASTER — Diff Ledger (Redline/Greenline)

Key: [- deleted -] (red) • [+ added +] (green) • Decision: ✅ Yes / ❌ No / ⏳ Maybe

| Change ID | Where (Anchor → Subclause) | Page | Old text ([-…-]) | New text ([+…+]) | Decision |
|---|---|---:|---|---|---|
| C01 | **Table 1 – Major Interfacing and Fluid Transport Lines** → Naming | {auto} | [- QRB-A, QRB-B, QRB-D, QRB-E; QINFRA-U/W/S; WCS-HP/LP/VLP -] | [+ QRB.A, QRB.B, QRB.D, QRB.E; QINFRA.U/W/S; WCS.HP/LP/VLP; optional WCS.R +] | ⏳ |
| C02 | **Warm Line Interfaces** (DN & duties) | {auto} | [- "The QINFRA-S is a safety line to the LP suction." -] | [+ "QINFRA.S (S-line) is the safety/recovery header; QRB.S local header protected at 1.3 bar(a) with ≥200 g/s @ 300 K capacity to WCS.LP." +] | ⏳ |
| C03 | **Table 6 – Leakage Requirements** | {auto} | [- (no explicit face-seal policy) -] | [+ "Serviceable joints shall be metal gasket face-seal (/FS, VCR-compatible); new metal gasket at every remake; verification by He MS test per Table 6." +] | ⏳ |
| C04 | **Purging and Conditioning** | {auto} | [- Manual purging guidance without DBB steps. -] | [+ Double-block-and-bleed with Venturi eductor purge (≤50 mbar(a), three He backfills to 1.05 bar(a), analyzer check, new gasket, leak test). +] | ⏳ |
| C05 | **Measuring Points (Tables 7–8)** | {auto} | [- No reference to /FS test ports. -] | [+ Add note: "Where /FS nuts with test ports exist, provide MS inboard leak-check and calibration tee." +] | ⏳ |
| C06 | **Valve Requirements** | {auto} | [- Solenoid pilot philosophy not defined. -] | [+ Specify small pneumatic/solenoid pilots shall fail open so loss of air does not obstruct manual flow. +] | ⏳ |
| C07 | **Recovery & Safety Devices** | {auto} | [- Population counts and setpoints absent. -] | [+ BD totals = 60 QCELL + 5 QPLANT; PSV totals = 180 QCELL + 30 QPLANT. Setpoints: QCELL BD 2.0 bar(a); QPLANT HP BD 18 bar(a)/PSV 16 bar(a); TS BD 3.5 bar(a)/PSV 4.0 bar(a); LP PSV 1.3 bar(a); vacuum breaker 0.95 bar(a); S-line PSV 1.3 bar(a) sized for ≥200 g/s He @ 300 K to WCS.LP. +] | ⏳ |
| C08 | **P&ID Legend** | {auto} | [- Lacked /FS annotation and dot notation. -] | [+ Add legend delta: "/FS = Metal gasket face-seal (VCR-compatible); new gasket each remake; panel female, module male." Apply dot notation (QRB.A etc.). +] | ⏳ |
| C09 | **New Chapter (after Table 6)** | {auto} | [- — -] | [+ Insert "VCR Face-Seal Policy & Serviceability" chapter covering orientation, purge, tamper control, allowed /FS areas, safety populations. +] | ⏳ |
| C10 | **Tender/Vendor Guidance** | {auto} | [- Vendor cost context absent. -] | [+ Add EU vendor triplets and indicative €/unit ranges for /FS fittings, PSV/BD, eductors, solenoids, analyzers. +] | ⏳ |
| C11 | **Acceptance Testing** | {auto} | [- No /FS make-break traceability. -] | [+ Add /FS make-break & gasket replacement checklist, DBB purge log, tamper-tag scan into CIS. +] | ⏳ |
| C12 | **Requirements Traceability Matrix** | {auto} | [- RTM entries not covering /FS policy. -] | [+ Append RTM.001–RTM.008 "shall" statements (face-seal policy, remakes, orientation, Table 6 leakage, analyzers, DBB purge, S-line PSV sizing, tamper control). +] | ⏳ |

*Use the provided VBA macro (optional) to populate the Page column after pasting this table into MASTER.*
