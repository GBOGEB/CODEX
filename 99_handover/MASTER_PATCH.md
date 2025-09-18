# VCR Face-Seal Policy & Serviceability (QRB.A/B/D/E · QINFRA.U/W/S · WCS.HP/LP/VLP)

## 1. Scope and Applicability
All serviceable warm subassemblies shall use **metal gasket face-seal (/FS, VCR-compatible)** joints; primary spines remain welded. This chapter formalizes /FS usage, purge, tamper-evidence, and safety populations consistent with Table 6 leakage acceptance and the measuring-point philosophy (Tables 7–8).

## 2. Orientation Policy (panel female / module male)
Fixed panels, racks, and manifolds shall present **female** seats; replaceable modules and instruments use **male** noses. Deviations shall be tagged and logged (RTM.003).

## 3. DBB + Eductor Purge (min-loss; recovery)
For any /FS service:
1. Isolate with double diaphragm valves (DBB); open bleed to **recovery** or **Venturi eductor** (motive dry N₂).
2. Pull to ≤ **50 mbar(a)** equivalent; close; **He backfill to 1.05 bar(a)**; vent to **WCS.LP**; repeat ×3.
3. Analyzer check vs project thresholds; break joint; install **new metal gasket**; re-make per torque/turn; leak test vs **Table 6**.

## 4. Tamper-Evident Control
Stainless wire seal across /FS nut flats to an anchor tab; serialized crimp; barcode/QR scan before & after. Log gasket alloy/batch, remake count, leak test ID (RTM.002/RTM.008).

## 5. Where /FS is Allowed
- **WCS:** instrument tees; analyzer manifolds; service spools.
- **QRB (cold):** only warm external panel & INVAC feedthrough assemblies.
- **QINFRA.U/W/S:** welded mains; /FS at service tees and analyzer pick-offs.
- **Storages:** analysis pick-offs. (Welded elsewhere.)

## 6. Safety Devices & S-Line
- **Populations:** **BD 65** total (60 QCELL + 5 QPLANT); **PSV 210** total (180 QCELL + 30 QPLANT).
- **Setpoints (abs):** QCELL BD **2.0 bar(a)**; QPLANT HP **BD 18 bar(a) / PSV 16 bar(a)**; TS **BD 3.5 bar(a) / PSV 4.0 bar(a)**; LP PSV **1.3 bar(a)**; vacuum breaker **0.95 bar(a)**.
- **S-line header:** **QINFRA.S → QRB.S** protected at **1.3 bar(a)**; PSV capacity **≥ 200 g/s He @ 300 K** with discharge to **WCS.LP** recovery. Final sizing per API 520/521 and ISO 21013-1/-2 using event backpressures from the warm-line interface (DN150).

## 7. P&ID Legend Delta (ISA/ISO)
Add: “**/FS = Metal gasket face-seal (VCR-compatible); new metal gasket at each remake; panel side female, module side male**.” Apply dot notation for all lines: **QRB.A/B/D/E; QINFRA.U/W/S; WCS.HP/LP/VLP**; optional **WCS.R**.

## 8. “Shall” Requirements (append to RTM)
- **RTM.001 (C):** All serviceable joints **shall** be /FS (VCR-compatible); no PTFE/elastomer in wetted helium service.
- **RTM.002 (C):** Each /FS remake **shall** use a **new metal gasket** with batch trace and tamper scan.
- **RTM.003 (C):** Orientation **shall** be panel-female/module-male; deviations logged.
- **RTM.003b (C):** Small solenoid pilots **shall** be **fail-open** so loss of air does not obstruct nominal manual flow.
- **RTM.004 (A):** Leak acceptance **shall** meet **Table 6** under ambient & standby conditions (EN 13185/ISO 20485).
- **RTM.005 (C):** DBB+eductor purge **shall** achieve residual air ≤ **0.05 %** before breaking /FS joints.
- **RTM.006 (A):** QINFRA.S/QRB.S **shall** be protected at **1.3 bar(a)** with PSV capacity **≥ 200 g/s @ 300 K** to **WCS.LP**.
- **RTM.007 (C):** Provide BD/PSV **populations & setpoints** as above and certify capacity.
- **RTM.008 (C):** Implement tamper-evident ties across /FS nuts with scan-based remake counting.

## 9. Acceptance Testing & Records
- **/FS Make-Break & Gasket Replacement form** (scan IDs, gasket batch, leak result vs Table 6).
- **DBB Purge log** (pressure, cycles, analyzer ppm).
- **PSV/BD dossier** (setpoint, orifice class, certified capacity).

## 10. Vendor Envelope (for tender benchmarking)
Triplets and indicative ranges for /FS fittings, BD/PSV, eductors, solenoids, analyzers; final EU tender pricing supersedes. See `05_vendor/VENDOR_COSTS.md`.
