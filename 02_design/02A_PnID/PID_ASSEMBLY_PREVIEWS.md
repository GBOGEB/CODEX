# P&ID Assembly Previews (/FS Examples)

All tags use dot notation (e.g., QRB.W, QINFRA.S, WCS.HP). Add the **/FS** legend note to each coupling on final drawings.

## A. DBB Purge Block with Venturi Eductor
Line: QINFRA.U (or QINFRA.W) · Class HE-UHP-SS316L-EP(FS)

```
IN ──(D)──┬──(D)── OUT
          │
          └─[TEE]─[●]─[≡]─(D)─< >──→ QINFRA.S or WCS.LP
               FR   FIL       EDC
```
- DV.QINFRA.U.101 (IN), DV.QINFRA.U.102 (OUT), FR.QINFRA.U.103, FIL.QINFRA.U.104, EDC.QINFRA.U.105.  
- All couplings annotated **/FS**; bleed leg discharges to recovery header or eductor return.

## B. Pressure Pickup Spool with Test Port

```
Process ──◼︎──[TEE]──◼︎──→ Process
                 │
                 ○ PT.QRB.W.045 (/FS nut with test port)
```
- Tee uses /FS union; pressure transmitter tagged PT.QRB.W.045 with calibration port accessible via face-seal nut test point.

## C. Analyzer Pick-Off (Return to WCS.LP)

```
Process ──(D)──[●]──[≡]──(⊃)──→ GAP.WCS (sample)
           DV   FR    FIL   PCV
           │
           └──────────────→ WCS.LP (return)
```
- DV.WCS.HP.121, FR.WCS.HP.122, FIL.WCS.HP.123, PCV.WCS.HP.124 regulating to analyzer. Return line ties back to WCS.LP.

## D. CF↔FS Temperature Feedthrough (QRB Warm Panel)

```
INVAC ─[CF/FS]─○ TT.QRB.W.046 ─◼︎─→ Warm process
```
- Adapter ADP.QRB.W.131 (CF to /FS). TT.QRB.W.046 uses metal feedthrough; annotate /FS at warm connection.

## E. PSV + BD to S-Line Header

```
Process ──[≀ BD.QCELL.201]──(spring PSV.QCELL.301)──▷|──→ QINFRA.S (DN150 to WCS.LP)
```
- BD setpoint 2.0 bar(a) (QCELL example); PSV sized for required flow; non-return valve into S-line; instrumentation monitors backpressure.

## F. MFC Bypass Module (Metal-Sealed Base Blocks)

```
        ┌──(D)──→ Bypass
IN ──(D)┤
        └── MFC (○FT) ─(⊃)──→ OUT
```
- DV.WCS.HP.141 / DV.WCS.HP.142 isolate/bypass; FT.WCS.HP.143 reports flow; FV.WCS.HP.144 controls; all base-block interfaces /FS.
