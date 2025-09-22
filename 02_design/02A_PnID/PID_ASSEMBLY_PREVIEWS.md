
# P&ID Assembly Previews (/FS Notation Applied)

The following text diagrams mirror the ISA-5.1/ISO symbol legend with dot-style SBS naming and `/FS` annotations for metal gasket face-seal joints.

## A. DBB Purge Block with Venturi Eductor (QINFRA.U/W service)
```
IN ──(D)──┬──(D)── OUT
          │
          └─[TEE]==/FS==[●]==/FS==[≡]==/FS==(D)==/FS==< >──→ QINFRA.S → WCS.LP
                          FR          FIL        bleed       eductor (dry N₂ motive)
```
Tags: DV.QINFRA.U.101 (IN), DV.QINFRA.U.102 (OUT), FR.QINFRA.U.103, FIL.QINFRA.U.104, EDC.QINFRA.U.105. All unions carry `/FS`; bleed routes to recovery header.

## B. Pressure Pickup Spool with Test Port (WCS.HP)
```
Process ──==/FS==[TEE]==/FS==── Process
                     │
                     ○ PT.WCS.HP.045
```
Use nut test-port for inboard helium leak-check; install calibration cap with `/FS` annotation.

## C. Analyzer Pick-Off and Return (WCS analyzer panel)
```
Process ──(D)==/FS==[●]==/FS==[≡]==/FS==(⊃)==/FS==→ GAP.WCS
            DV        FR        FIL        PRV/PCV
                         │
                         └───────────────→ WCS.LP return (/FS)
```
Supports continuous He purity monitoring; restrictor protects analyzer flow, return line routes to LP recovery.

## D. CF↔FS Temperature Feedthrough (QRB warm panel)
```
QRB wall ─[CF/FS]==/FS==○ TT.QRB.W.046 ─==/FS==→ Warm piping
```
All-metal feedthrough with CF clamp on cold side and `/FS` joint on warm instrumentation.

## E. Relief Path to S-Line (QINFRA.S / QRB.S)
```
Process ──[≀ BD.QPLANT.401]==/FS==→(spring) PSV.QPLANT.402──▷|──→ QINFRA.S (DN150)
                                                             NRV.QPLANT.403
```
Sizing basis: 1.3 bar(a) setpoint, ≥200 g/s helium at 300 K discharging to WCS.LP recovery header.

## F. MFC Bypass and Isolation (WCS.LP panel)
```
        ┌──(D)==/FS==→──┐
IN ──(D)==/FS==  MFC block  ==/FS==(⊃)==/FS==→ OUT
        └──(D)==/FS==→──┘
```
Bypass valves DV.WCS.LP.141 / DV.WCS.LP.142 isolate the metal-sealed mass flow controller; control valve `(⊃)` tied to AO/DO with analyzer feedback.

> Use these previews as drafting references; final CAD should place official ISA/ISO blocks and `/FS` call-outs per project legend.
