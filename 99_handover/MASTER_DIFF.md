# MASTER — Diff Ledger (Redline/Greenline)

Key: [- deleted -] (red) • [+ added +] (green) • Decision: ✅ Yes / ❌ No / ⏳ Maybe

| Change ID | Where (Anchor → Subclause) | Page | Old text ([-…-]) | New text ([+…+]) | Decision |
|---|---|---:|---|---|---|
| C01 | Table 1 – Major Interfacing and fluid transport lines → Naming | {auto} | [- QRB-A, QRB-B, QRB-D, QRB-E; QINFRA-U/W/S; WCS-HP/LP/VLP -] | [+ QRB.A, QRB.B, QRB.D, QRB.E; QINFRA.U/W/S; WCS.HP/LP/VLP (optionally WCS.R) +] | ⏳ |
| C02 | Warm line interfaces (DN & duties) | {auto} | [- “The QINFRA-S is a safety Line … to the LP suction …” -] | [+ “QINFRA.S (S-line) is the safety/recovery header; QRB.S local header protected at 1.3 bar(a) with capacity for 200 g/s @ 300 K to WCS.LP recovery.” +] | ⏳ |
| C03 | Table 6 – Leakage requirements | {auto} | [- — -] | [+ “Serviceable joints shall be metal gasket face-seal (/FS, VCR-compatible); new metal gasket at every remake; verification by He MS test vs Table 6.” +] | ⏳ |
| C04 | Purging and conditioning | {auto} | [- Manual purging may be implemented … -] | [+ “Double-block-and-bleed (DBB) purge with Venturi eductor: pull-down to ≤50 mbar(a), helium backfill to 1.05 bar(a), analyzer confirmation, then remake /FS with new gasket; bleed routed to recovery (WCS.LP) or eductor with dry N₂ motive.” +] | ⏳ |
| C05 | Measuring points (Tables 7–8) | {auto} | [- — -] | [+ “/FS nuts with test ports shall provide MS inboard leak-check ports and calibration tees for PT/AI sampling.” +] | ⏳ |
| C06 | Valve requirements | {auto} | [- — -] | [+ “Small pneumatic/solenoid pilots shall fail open so loss of air supply does not obstruct nominal manual flow.” +] | ⏳ |
| C07 | Recovery and safety devices | {auto} | [- — -] | [+ “Populations: Bursting discs = 60 QCELL + 5 QPLANT; PSVs = 180 QCELL + 30 QPLANT. Setpoints (abs): QCELL BD 2.0 bar; QPLANT HP BD 18 bar / PSV 16 bar; TS BD 3.5 bar / PSV 4.0 bar; LP PSV 1.3 bar; vacuum breaker PSV 0.95 bar; S-line PSV 1.3 bar sized for ≥200 g/s @ 300 K to WCS.LP.” +] | ⏳ |
| C08 | P&ID legend (ISA/ISO) | {auto} | [- — -] | [+ “Add legend delta: ‘/FS = Metal gasket face-seal (VCR-compatible); new metal gasket at each remake; panel side female, module side male.’” +] | ⏳ |
| C09 | New chapter (after Table 6 / before Acceptance Testing) | {auto} | [- — -] | [+ Insert “VCR Face-Seal Policy & Serviceability” chapter (orientation policy, DBB purge, tamper-evident control, /FS area map, safety populations, RTM references). +] | ⏳ |
| C10 | Tender / vendor sections | {auto} | [- — -] | [+ “Add vendor triplets and ballpark (€) costs for /FS fittings, bursting discs, PSVs, eductors, solenoids, analyzers for tender benchmarking.” +] | ⏳ |
| C11 | Acceptance testing | {auto} | [- — -] | [+ “Introduce /FS make-break & gasket replacement checklist, helium MS leak record, and tamper-tag scan logging to CIS.” +] | ⏳ |
| C12 | Requirements traceability | {auto} | [- — -] | [+ “Append RTM.001–RTM.008 ‘shall’ statements covering /FS policy, remakes, Table 6 leakage, analyzers in two rooms, DBB purge ≤0.05% residual air, S-line PSV ≥200 g/s @ 300 K, safety device populations, and tamper evidence.” +] | ⏳ |

> **Reviewer action** – mark Decision column with ✅/❌/⏳ and return for implementation.

### Optional macro (Word VBA) to auto-fill page numbers

```vba
Sub FillMasterDiffPages()
    Dim t As Table, r As Row, anchor As String, p As Long, f As Range
    For Each t In ActiveDocument.Tables
        If InStr(1, t.Cell(1, 1).Range.Text, "Change ID") > 0 Then
            For Each r In t.Rows
                If r.Index = 1 Then GoTo nxt
                anchor = Split(r.Cells(2).Range.Text, "→")(0)
                Set f = ActiveDocument.Range
                With f.Find
                    .Text = anchor
                    .MatchCase = False
                    .Execute
                End With
                If f.Find.Found Then
                    p = f.Information(wdActiveEndPageNumber)
                Else
                    p = 0
                End If
                r.Cells(3).Range.Text = IIf(p > 0, CStr(p), "—")
nxt:        Next r
        End If
    Next t
End Sub
```
