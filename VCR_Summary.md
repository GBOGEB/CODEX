# VCR Requirements, Quality, BOM & Vendor Summary

This markdown consolidates the VCR-specific slices requested for PDF export.

## 1. Requirements Overview
| Req ID | Theme | Verification | Artifact Hook |
| --- | --- | --- | --- |
| RTM.001 | All serviceable joints shall be /FS (VCR-compatible) | Visual inspection + BOM review | P&IDs, Line class sheet |
| RTM.002 | Each /FS remake shall use a new metal gasket with batch traceability and tamper evidence. | Maintenance checklist | Maintenance log, Tamper-seal log |
| RTM.003 | /FS orientation shall be panel-female and module-male | Field inspection | Orientation checklist |
| RTM.003b | Small pneumatic/solenoid pilots shall be fail-open so loss of motive air does not obstruct manual isolation flow. | Functional test | Valve FAT/SAT records |
| RTM.004 | Leak acceptance shall meet Addendum Table 6 values using EN 13185 / ISO 20485 helium mass-spectrometer methods. | Helium MS leak test | Leak reports |
| RTM.005 | DBB plus eductor purge shall achieve residual air <=0.05% before breaking the joint. | Procedure witness | Purge log, Analyzer log |
| RTM.006 | QINFRA.S/QRB.S shall be protected at 1.3 bar(a) with PSV capacity >=200 g/s @ 300 K routed to WCS.LP recovery. | Sizing calculations + certificates | PSV certification dossier |
| RTM.007 | Provide BD/PSV populations and setpoints as defined above with certified orifice capacity. | Manifest review + certificates | BOM_Master.csv, Certification pack |
| RTM.008 | Implement tamper-evident ties and scan-based remake counting for every /FS connection. | Inspection + system audit | Tamper log, Maintenance system report |
| RTM.009 | Install dual helium analyzers (GAP.WCS and GAP.QRB) measuring H2O and N2 with +/-1 ppm accuracy and <=1 ppm/year drift | Calibration verification | Analyzer calibration certificates |

## 2. Quality Controls Snapshot
- Hold/Witness plan: see VCR_Quality_Procedures.docx Section 1.
- DBB purge and helium leak test steps remain mandatory before any /FS joint return to service.
- Analyzer calibration (+/-1 ppm, <=1 ppm/year drift) anchors acceptance for RTM.004/009.

## 3. BOM Elements Driving the VCR Envelope
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
| PSV.QPLANT.S | QINFRA.S | Safety valve (S-line header) | 1.3 bar(a) | 4 | >=200 g/s He @300 K to WCS.LP |
| VAL.ONOFF | WCS/QRB | On/Off valves | PN rated | 180 | 1" welded bodies; /FS at instrument take-offs |
| FSU.GASKET.ALL | ALL | Metal gasket kit | n/a | >500 | SS primary; Ni/Cu by temperature |
| GAP.WCS | WCS | Gas analyzer panel | ppm range | 1 | Moisture/N2 analyzer; return to WCS.LP |
| GAP.QRB | QRB | Gas analyzer panel | ppm range | 1 | Cold-box room analyzer; return to WCS.LP |
| EDC.QINFRA | UHP Network | Venturi eductor set | ?P motive | 6 | Dry N2 motive purge blocks |
| SOL.FAILOPEN | WCS/QRB | Fail-open pilot solenoids | 24 VDC | 60 | Manual isolation assist |

## 4. Vendor Landscape (budgetary only)
| Scope | Vendors | Indicative Range | Notes |
| --- | --- | --- | --- |
| /FS fittings & gaskets | Swagelok; Parker Veriflo; FITOK | Metal gaskets ~EUR 2-15; bodies/weld glands ~EUR 20-120 (finish dependent) | Catalog/distributor pricing; include cleaning premiums |
| Pressure safety valves | Leser; Herose; Advance Valve (stockist) | DN25-DN50 cryogenic PSV ~EUR 400-1,200 | Cryogenic helium service; certification costs apply |
| Bursting discs | REMBE; OsecoElfab; Fike Europe | Disc EUR 250-600; holder EUR 400-900 | Match holders to disc series per supplier guidance |
| Venturi eductors & purge hardware | SMC ZH; Piab piINLINE | Approx. EUR 20-150 | Dry N2 motive supply, size orifices per purge calc |
| Fail-open pilot solenoids | ASCO; Buerkert | Approx. EUR 100-550 | Three-way NO valves; certification/material adders |
| Online He purity analyzers | Michell; Edgetech/PST | Dual-channel packages mid four- to low five-figure EUR | Include sample conditioning + calibration service |

## 5. Architecture & Ops Touchpoints
- ADR-001 enforces the /FS policy, purge discipline, and relief population baseline.
- OCD scenarios: maintenance outage + emergency depressurization demand live proof of purge, analyzer, and S-line capacity.
- Evidence flow: P&IDs / BOM -> RTM -> QA logs -> CIS records -> vendor cert dossiers.
