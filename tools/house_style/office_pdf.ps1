<#
  Export a deck or Word file to PDF with the installed Microsoft Office over COM (Windows only).
  qps_post.export_pdf() uses it when LibreOffice (soffice) is not on PATH, or with --pdf-engine office.

  powershell.exe -NoProfile -ExecutionPolicy Bypass -File office_pdf.ps1 -In deck.pptx -Out deck.pdf
#>
param([Parameter(Mandatory = $true)][string]$In, [Parameter(Mandatory = $true)][string]$Out)
$ErrorActionPreference = 'Stop'
$src = (Resolve-Path -LiteralPath $In).Path
$dst = [IO.Path]::GetFullPath($Out)
$ext = [IO.Path]::GetExtension($src).ToLowerInvariant()

if ($ext -in '.pptx', '.potx', '.ppt') {
  $app = New-Object -ComObject PowerPoint.Application
  try {
    $doc = $app.Presentations.Open($src, $true, $false, $false)   # ReadOnly, Untitled, WithWindow
    try { $doc.SaveAs($dst, 32) } finally { $doc.Close() }         # 32 = ppSaveAsPDF
  } finally {
    # PowerPoint runs one instance per user: leave it open when the user has other presentations in it.
    if ($app.Presentations.Count -eq 0) { $app.Quit() }
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
  }
} elseif ($ext -in '.docx', '.dotx', '.doc') {
  $app = New-Object -ComObject Word.Application
  try {
    $app.Visible = $false
    $app.DisplayAlerts = 0                                          # wdAlertsNone: no field-update prompt
    $doc = $app.Documents.Open($src, $false, $true)                 # ConfirmConversions, ReadOnly
    # 17 = wdExportFormatPDF. Close() and Quit() take [ref] arguments in Windows PowerShell, so mark the
    # document saved (fields may have updated on open) and call them without arguments.
    try { $doc.ExportAsFixedFormat($dst, 17) } finally { $doc.Saved = $true; $doc.Close() }
  } finally {
    if ($app.Documents.Count -eq 0) { $app.Quit() }
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
  }
} else {
  throw "office_pdf.ps1: unsupported file type '$ext'"
}
