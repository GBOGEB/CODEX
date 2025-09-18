# P&ID Symbol Cheat-Sheet (ISA/ISO with /FS Annotation)

Project: HELIUM_VCR_UHP · Rev 1.0 · Date 2025-09-18  
Standards: ISA-5.1 (2024) instrument symbols & tag letters; ISO 10628 / ISO 14617 linework.  
Project delta: annotate every face-seal coupling with **/FS = Metal gasket face-seal (VCR-compatible); new gasket each remake; panel female, module male.**

## A. Line Types & Connectors
| Name | Standard | ASCII Preview | Notes |
|---|---|---|---|
| Process line (He) | ISO 10628 | ───────── | Full-thickness solid line |
| Capillary / sample | ISO 10628 | ─ ─ ─ ─ | Thin dashed line |
| Pneumatic signal | ISA-5.1 | – – – – | Long dash |
| Electric signal | ISA-5.1 | – · – · – | Dash-dot |
| Data / comms | ISA-5.1 | · · · · · · | Dotted |
| Off-page connector | ISO 10628 | ○→TAG | Circle with arrow & reference |
| Face-seal union | Project | ==/FS== | Add call-out “/FS” near coupling |

## B. Valves & Inline Devices
| Name | Standard | ASCII Preview | Typical Tag | Notes |
|---|---|---|---|---|
| Hand valve (ball) | ISO 10628 | ─◼︎─ | HV.### | Warm on/off isolation |
| Diaphragm valve | ISA-5.1 | ─(D)─ | DV.### | UHP/DBB blocks |
| Control valve | ISA-5.1 | ─(⊃)─ | FV.### / CV.### | Add positioner bubble |
| Check valve | ISO 10628 | ─▷|─ | NRV.### | Relief return/non-return |
| Safety valve (PSV) | ISO 10628 | ─(spring)↗ | PSV.### | Link to QINFRA.S |
| Bursting disc (BD) | ISO 10628 | ─[≀]─ | BD.### | DN100 housings etc. |
| Inline filter | ISO 10628 | ─[≡]─ | FIL.### | 0.003 μm upstream analyzers |
| Flow restrictor | Project | ─[●]─ | FR.### | VCR restrictor union |
| Face-seal coupling | Project | ─◁▷─/FS | FSU.### | Use /FS annotation |
| CF↔FS adapter | Project | ─[CF/FS]─ | ADP.### | INVAC feedthrough |

## C. Instruments & Accessories
| Function | ISA Letter | Symbol | Example Tag | Notes |
|---|---|---|---|---|
| Pressure transmitter | PT | ○PT | QRB.W-HE-PT.045 | Use nut test port |
| Temperature transmitter | TT | ○TT | QRB.W-HE-TT.046 | CF↔FS feedthrough |
| Flow transmitter / MFC | FT | ○FT | WCS.HP-HE-FT.047 | Base blocks /FS |
| Analyzer indicator | AI | ○AI | GAP.WCS-AI.201 | H₂O / N₂ ppm |
| Positioner | FY | ◐FY | FV.047-FY | For control valves |
| Local indicator | PI/TI | ◌PI | WCS.LP-PI.012 | Gauges |
| Solenoid | Y | ◖Y | Y.501 | Fail-open pilot |
| Limit switch | ZS | ◖ZS | ZS.047A/B | Dual end-switches |

## D. Equipment & Specials
| Item | Symbol | Tag | Note |
|---|---|---|---|
| Venturi eductor | ─< >─ | EDC.105 | Dry N₂ motive |
| Gas analyzer panel | [ANLZ] | GAP.WCS / GAP.QRB | Returns to WCS.LP |
| Ambient heater | [EH] | EH.QRB | Cold-box room |
| Vacuum pump (portable) | [P(VAC)] | VP.WCS | Purge assist |

## E. Signal Legend
- Solid line = process helium.  
- Thin dashed = sample/capillary.  
- Long dash = pneumatic.  
- Dash-dot = electric power/command.  
- Dotted = data/comm.  
- All face-seal joints carry **/FS** note and orientation policy.

## F. Tagging Syntax
`{Area}.{Service}-{Type}.{Seq}` → e.g., `QRB.W-HE-PT.045`.  
Area codes: QRB.A/B/D/E, QINFRA.U/W/S, WCS.HP/LP/VLP, optional WCS.R.  
Include /FS annotation at each coupling in CAD drawings.
