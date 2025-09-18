# P&ID Assembly Previews (/FS Notation + Dot SBS Names)

## A. DBB Purge Block with Venturi Eductor (QINFRA.U / QINFRA.W)
```
      ──(D)──┬──(D)──→ Process downstream
   IN        │    OUT
             │
             └─[TEE]─[●]─[≡]─(D)─< >──→ QINFRA.S → WCS.LP
                    FR  FIL        EDC (dry N₂ motive)
```
- Tags: DV.QINFRA.U.101, DV.QINFRA.U.102, FR.QINFRA.U.103, FIL.QINFRA.U.104, EDC.QINFRA.U.105.  
- Annotate every coupling “/FS”; bleed leg returns to recovery or venturi exhaust.

## B. Pressure Pickup Spool with Test Port (QRB.W)
```
Process ──◼︎──[TEE]──◼︎──→ Process
                │
                ○ PT-045 (/FS test port)
```
- PT.QRB.W.045 uses face-seal take-off with nut test-port for inboard MS leak-check.

## C. Analyzer Pick-off to Gas Analysis Panel (WCS)
```
Process ──(D)──[●]──[≡]──(⊃)──→ GAP.WCS → WCS.LP
           DV    FR    FIL    Reg (PRV/PCV)
```
- Analyzer panel GAP.WCS returns to WCS.LP; restrictor union maintains sample draw; include /FS annotation at each removable joint.

## D. CF↔FS Temperature Feedthrough (QRB.B Warm Panel)
```
INVAC wall ─[CF/FS]─ ○ TT-046 ─◼︎─→ Warm process
```
- Adapter ADP.QRB.B.131; all-metal feedthrough maintains INVAC integrity.

## E. Relief Train to S-Line (QINFRA.S → QRB.S)
```
Process ──[≀ BD-01]──(spring PSV-02)──▷|──→ QINFRA.S (DN150) → WCS.LP
```
- PSV sized for ≥200 g/s He @ 300 K at 1.3 bar(a); include NRV toward recovery header.

## F. MFC Bypass / Isolation (WCS Analyzer Skid)
```
      ─(D)─◼︎──→┐
                │ MFM/MFC (FS base blocks)
      ─(D)─◼︎──→┘
```
- DV.WCS.ANL.141 / 142 for bypass; FT.WCS.ANL.143 output; annotate /FS at each removable coupling.

> Export tip: `pandoc PID_ASSEMBLY_PREVIEWS.md -V toc=true -V numbersections=true -o PID_ASSEMBLY_PREVIEWS.pdf`
