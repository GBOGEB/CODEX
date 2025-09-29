# VCR Face-Seal Policy & Serviceability (QRB.A/B/D/E · QINFRA.U/W/S · WCS.HP/LP/VLP)

## 1. Scope and Applicability
All serviceable warm subassemblies shall use **metal gasket face-seal (/FS, VCR-compatible)** joints while primary spines remain welded. This chapter anchors /FS usage, purge controls, tamper evidence, and safety device populations to Addendum II leakage limits (Table 6) and measuring-point requirements (Tables 7–8).

## 2. Orientation Policy (panel female / module male)
Fixed panels, racks, and manifolds shall present **female** face-seal seats; replaceable modules and instruments shall use **male** noses. Any deviation shall be tagged and recorded in the maintenance log.

## 3. DBB + Eductor Purge (min-loss; recovery compliant)
1. Isolate with double diaphragm valves (DBB); open the bleed leg to the **recovery header (WCS.LP)** or to a Venturi eductor driven by dry nitrogen.
2. Draw the cavity to ≤ **50 mbar(a)** equivalent; close valves; **helium backfill to 1.05 bar(a)**; vent to WCS.LP; repeat three times.
3. Verify purity using the local analyzer (ppm H₂O/N₂ within limits); break the joint; install a **new metal gasket**; re-make per torque/turn guidance; execute a helium MS leak test to the acceptance in **Table 6**.

## 4. Tamper-Evident Control
Apply stainless sealing wire across each /FS nut to an anchor tab with a serialized crimp. Scan barcode/QR identifiers before and after maintenance. Record gasket alloy/batch, remake count, and leak-test ID in the maintenance system.

## 5. Where /FS Is Allowed
- **WCS:** instrument tees, analyzer manifolds, service spools.
- **QRB (cold area):** warm external panel and INVAC feedthrough assemblies only.
- **QINFRA.U/W/S:** welded mains; /FS permitted at service tees, analyzer pick-offs, and purge modules.
- **Storages:** analysis pick-offs with recovery routing.

## 6. Safety Devices & S-Line Protection
- **Populations:** **Bursting discs = 60 QCELL + 5 QPLANT; Safety valves = 180 QCELL + 30 QPLANT.**
- **Setpoints (absolute):**

  | Location/Device         | BD Setpoint      | PSV Setpoint     |
  |------------------------|------------------|------------------|
  | QCELL                  | **2.0 bar(a)**   | -                |
  | QPLANT HP              | **18 bar(a)**    | **16 bar(a)**    |
  | Thermal shield         | **3.5 bar(a)**   | **4.0 bar(a)**   |
  | Warm LP                | -                | **1.3 bar(a)**   |
  | Vacuum breaker         | -                | **0.95 bar(a)**  |

- **S-line header:**
  - **Setpoint:** **QINFRA.S → QRB.S** protected at **1.3 bar(a)**.
  - **PSV capacity:** **≥ 200 g/s helium at 300 K**.
  - **Discharge routing:** PSV discharges to **WCS.LP** recovery.
  - **Sizing standards:** Final sizing shall comply with **API 520/521** and **ISO 21013-1/-2** using Addendum event backpressures.

## 7. P&ID Legend Delta (ISA/ISO)
Add to legend: **"/FS = Metal gasket face-seal (VCR-compatible); new gasket at each remake; panel female, module male."** Apply dot notation for all line identifiers (QRB.A/B/D/E; QINFRA.U/W/S; WCS.HP/LP/VLP; optional WCS.R).

## 8. "Shall" Requirements (add to RTM)
- **RTM.001:** All serviceable joints **shall** be /FS (VCR-compatible); no PTFE or elastomer seals in wetted helium service.
- **RTM.002:** Each /FS remake **shall** use a new metal gasket with batch traceability and tamper evidence.
- **RTM.003:** /FS orientation **shall** be panel-female and module-male; deviations logged.
- **RTM.003b:** Small pneumatic/solenoid pilots **shall** be fail-open so loss of motive air does not obstruct manual isolation flow.
- **RTM.004:** Leak acceptance **shall** meet Addendum Table 6 values using EN 13185 / ISO 20485 helium mass-spectrometer methods.
- **RTM.005:** DBB plus eductor purge **shall** achieve residual air ≤ **0.05 %** before breaking the joint.
- **RTM.006:** QINFRA.S/QRB.S **shall** be protected at **1.3 bar(a)** with PSV capacity **≥ 200 g/s @ 300 K** routed to WCS.LP recovery.
- **RTM.007:** Provide BD/PSV populations and setpoints as defined above with certified orifice capacity.
- **RTM.008:** Implement tamper-evident ties and scan-based remake counting for every /FS connection.

## 9. Acceptance Records
Issue: **/FS Make-Break & Gasket Replacement** checklist; **DBB purge log**; **PSV/BD certification dossier** documenting setpoint, orifice class, and capacity.

## 10. Vendor Envelope (Indicative)
Record EU vendor triplets and indicative price bands for /FS fittings, bursting discs, safety valves, eductors, solenoids, and analyzers. Actual tender responses shall supersede ballpark figures.

