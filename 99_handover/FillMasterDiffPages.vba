Sub FillMasterDiffPages()
    Dim t As Table, r As Row, anchor As String, pageNumber As Long, searchRange As Range
    For Each t In ActiveDocument.Tables
        If InStr(1, t.Cell(1, 1).Range.Text, "Change ID") > 0 Then
            For Each r In t.Rows
                If r.Index = 1 Then GoTo NextRow
                anchor = Split(r.Cells(2).Range.Text, "→")(0)
                Set searchRange = ActiveDocument.Range
                With searchRange.Find
                    .Text = anchor
                    .MatchCase = False
                    .Execute
                End With
                If searchRange.Find.Found Then
                    pageNumber = searchRange.Information(wdActiveEndPageNumber)
                    r.Cells(3).Range.Text = CStr(pageNumber)
                Else
                    r.Cells(3).Range.Text = "—"
                End If
NextRow:
            Next r
        End If
    Next t
End Sub
