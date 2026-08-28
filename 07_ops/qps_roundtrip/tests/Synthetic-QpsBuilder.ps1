[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [Parameter(Mandatory = $true)][string]$EvidenceRoot,
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$ReleaseId,
    [Parameter(Mandatory = $true)][string]$BuildLabel
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.IO.Compression.FileSystem

function New-MinimalZipPackage {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][hashtable]$Entries
    )
    if (Test-Path -LiteralPath $Path) { Remove-Item -LiteralPath $Path -Force }
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew)
    try {
        $zip = [System.IO.Compression.ZipArchive]::new($stream, [System.IO.Compression.ZipArchiveMode]::Create, $false)
        try {
            foreach ($name in ($Entries.Keys | Sort-Object)) {
                $entry = $zip.CreateEntry($name)
                $writer = [System.IO.StreamWriter]::new($entry.Open(), [System.Text.UTF8Encoding]::new($false))
                try { $writer.Write([string]$Entries[$name]) } finally { $writer.Dispose() }
            }
        }
        finally { $zip.Dispose() }
    }
    finally { $stream.Dispose() }
}

New-Item -ItemType Directory -Force $OutputDirectory | Out-Null

$xlsxEntries = @{
    'xl/workbook.xml' = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Summary" sheetId="1" r:id="rId1"/></sheets><definedNames><definedName name="QPS_Total">Summary!$B$1</definedName></definedNames></workbook>'
    'xl/_rels/workbook.xml.rels' = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    'xl/worksheets/sheet1.xml' = '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>QPS Total</t></is></c><c r="B1"><f>1+1</f><v>2</v></c></row></sheetData></worksheet>'
}
New-MinimalZipPackage -Path (Join-Path $OutputDirectory 'QPS_COST_Master.xlsx') -Entries $xlsxEntries

$docxEntries = @{
    'word/document.xml' = '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>QPS Cost Handover</w:t></w:r></w:p><w:p><w:r><w:t>Controlled synthetic content.</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Item</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Value</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'
}
New-MinimalZipPackage -Path (Join-Path $OutputDirectory 'QPS_Cost_Engineering_Handover.docx') -Entries $docxEntries

$pptxEntries = @{
    'ppt/presentation.xml' = '<?xml version="1.0" encoding="UTF-8"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst></p:presentation>'
    'ppt/_rels/presentation.xml.rels' = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/></Relationships>'
    'ppt/slides/slide1.xml' = '<?xml version="1.0" encoding="UTF-8"?><p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:nvSpPr/><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>QPS Cost Summary</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
}
New-MinimalZipPackage -Path (Join-Path $OutputDirectory 'QPS_Cost_Management_Deck.pptx') -Entries $pptxEntries

Set-Content -LiteralPath (Join-Path $OutputDirectory 'QPS_Cost_Engineering_Handover.pdf') -Value '%PDF-1.4 synthetic-qps-test' -NoNewline -Encoding ascii
Set-Content -LiteralPath (Join-Path $OutputDirectory 'index.html') -Value '<!doctype html><html><body><section id="summary"><h1>QPS Cost Summary</h1><script type="application/json">{"total":2}</script></section></body></html>' -NoNewline -Encoding utf8
Set-Content -LiteralPath (Join-Path $OutputDirectory 'QA_REPORT.md') -Value '# QA REPORT`n`nPASS' -Encoding utf8
Set-Content -LiteralPath (Join-Path $OutputDirectory 'RELEASE_NOTES.md') -Value '# Synthetic release' -Encoding utf8

$meta = [ordered]@{
    schema_version = 1
    control_id = 'GOV-001'
    release_id = $ReleaseId
    generated_utc = '2026-01-01T00:00:00Z'
    repositories = [ordered]@{ codex = [ordered]@{ repository = 'GBOGEB/CODEX'; commit = 'synthetic' } }
    source_tree_sha256 = ('0' * 64)
    evidence_registry_sha256 = ('1' * 64)
    qa = [ordered]@{ status = 'PASS'; report = 'QA_REPORT.md' }
    publication = [ordered]@{ immutable_release = $true; office_review_copy = $true }
}
$meta | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'BUILD_META.json') -Encoding utf8
