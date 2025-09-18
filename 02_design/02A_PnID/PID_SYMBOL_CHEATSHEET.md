# P&ID Symbol Cheat-Sheet (ISA/ISO Aligned with /FS Annotation)

Project: HELIUM_VCR_UHP · Rev 1.0 · Date 2025-09-18  
Basis: ISA-5.1 tag & instrument symbols, ISO 10628 / ISO 14617 line and equipment conventions.  
Project delta: annotate every metal gasket face-seal joint as `/FS` and apply dot-style SBS names (e.g., `QRB.A`, `QINFRA.S`, `WCS.HP`).

## A. Line Types & Connectors
| Name | ISO/ISA Basis | ASCII Preview | Project Note |
|---|---|---|---|
| Process line (He) | ISO 10628 | `─────────` | Standard thickness solid line |
| Capillary/sample line | ISO 10628 | `─ ─ ─ ─` (thin) | Use thin dashed line |
| Pneumatic signal | ISA-5.1 | `– – – –` | For instrument air |
| Electric signal | ISA-5.1 | `– · – · –` | Dash-dot |
| Data/comm signal | ISA-5.1 | `· · · · ·` | Dotted |
| Off-page connector | ISO 10628 | `○→TAG` | Reference to destination |
| Face-seal union (/FS) | Project note | `==/FS==` | Call-out “/FS = metal gasket face-seal (VCR-compatible)” |

## B. Valves & Fittings
| Component | Standard | ASCII Preview | Typical Tag | Project Note |
|---|---|---|---|---|
| Hand valve (ball) | ISO 10628 | `─◼︎─` | HV-### | On/off isolation |
| Diaphragm valve | ISA-5.1 | `─(D)─` | DV-### | Clean-service /FS DBB |
| Control valve | ISA-5.1 | `─(⊃)─` | FV-### / CV-### | Add positioner bubble |
| Check valve | ISO 10628 | `─▷|─` | NRV-### | Non-return on recovery headers |
| Pressure safety valve | ISO 10628 | `─(spring)↗` | PSV-### | Route to QINFRA.S / WCS.LP |
| Bursting disc | ISO 10628 | `─[≀]─` | BD-### | Houses DN & burst rating |
| Inline filter | ISO 10628 | `─[≡]─` | FIL-### | 0.003 µm UHP filter |
| Flow restrictor union | Project | `─[●]─` | FR-### | OEM /FS restrictor |
| CF↔FS adapter | Project | `─[CF/FS]─` | ADP-### | For INVAC feedthroughs |

## C. Instruments & Accessories
| Instrument | ISA Letter | Symbol | Example Tag | Project Note |
|---|---|---|---|---|
| Pressure transmitter | PT | `○ PT` | PT-0xx | Use /FS tee with nut test port |
| Temperature transmitter | TT | `○ TT` | TT-0xx | CF↔FS feedthrough |
| Flow transmitter | FT | `○ FT` | FT-0xx | MFM/MFC base block |
| Analyzer indicator | AI | `○ AI` | AI-0xx | H₂O & N₂ ppm monitoring |
| Positioner | FY | `◐ FY` | FV-0xx-FY | On control valve |
| Local gauge | PI/TI/FI | `◌ PI` | PI-0xx | Remove for maintenance |
| Solenoid (fail-open) | Y | `◖ Y` | Y-0xx | Pilot for manual valves |
| Limit switch | ZS | `◖ ZS` | ZS-0xx | Dual end-switches where SIL relevant |

## D. Equipment & Specials
| Item | Standard | Symbol | Tag | Note |
|---|---|---|---|---|
| Venturi eductor | ISO 10628 | `─< >─` | EDC-### | Dry N₂ motive purge |
| Gas analyzer panel | Project | `[ANLZ]` | GAP.WCS / GAP.QRB | Return to WCS.LP |
| Ambient heater | ISO 10628 | `[EH]` | EH-### | Cold-box room |
| Vacuum pump (temporary) | ISO 14617 | `[P(VAC)]` | VP-### | Conditioning option |

## E. Instrument/Signal Legend
- Solid line: process helium.  
- Thin dashed: sample/capillary.  
- Long dashed: pneumatic.  
- Dash-dot: electric.  
- Dotted: data/comm.  
- Annotation `/FS`: metal gasket face-seal (VCR-compatible); **new gasket each remake**; panel side female, module side male.  
- Tagging pattern: `{Area}.{Service}.{Type}.{Seq}` e.g., `QRB.W-HE-PT-023` → `QRB.W-HE-PT-023`.

## F. Usage Guidance
1. Apply `/FS` to every face-seal union or component call-out.  
2. Reference Tables 6–8 (Addendum II) for leak acceptance and measuring points when placing PT/AI instrumentation.  
3. For S-line tie-ins (QINFRA.S / QRB.S) note PSV setpoints and discharge to WCS.LP.  
4. For analyzer pick-offs, depict restrictor union `[●]`, fine metering valve `(D)`, filter `[≡]`, regulator `(⊃)`, and return line to WCS.LP.
