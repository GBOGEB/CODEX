[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ToolRoot,
    [Parameter(Mandatory = $true)][string]$SchemaPath,
    [Parameter(Mandatory = $true)][string]$WorkRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$local = Join-Path $WorkRoot 'local'
$published = Join-Path $WorkRoot 'published'
$receipts = Join-Path $WorkRoot 'receipts'
New-Item -ItemType Directory -Force $local, $published, $receipts | Out-Null

$files = [ordered]@{
    'QPS_COST_Master.xlsx' = 'xlsx-bytes'
    'QPS_Cost_Engineering_Handover.docx' = 'docx-bytes'
    'QPS_Cost_Management_Deck.pptx' = 'pptx-bytes'
    'QPS_Cost_Engineering_Handover.pdf' = 'pdf-bytes'
    'index.html' = '<html>same</html>'
    'QA_REPORT.md' = '# PASS'
    'RELEASE_NOTES.md' = '# synthetic'
    'BUILD_META.json' = '{"qa":{"status":"PASS"}}'
}
foreach ($entry in $files.GetEnumerator()) {
    Set-Content -LiteralPath (Join-Path $local $entry.Key) -Value $entry.Value -NoNewline -Encoding utf8
    Copy-Item -LiteralPath (Join-Path $local $entry.Key) -Destination (Join-Path $published $entry.Key)
}

function Write-Manifest {
    param([string]$Root)
    $lines = @('# synthetic manifest')
    foreach ($name in $files.Keys) {
        $hash = (Get-FileHash -LiteralPath (Join-Path $Root $name) -Algorithm SHA256).Hash.ToLowerInvariant()
        $lines += "$hash  $name"
    }
    [System.IO.File]::WriteAllLines((Join-Path $Root 'MANIFEST.sha256'), $lines, [System.Text.UTF8Encoding]::new($false))
}
Write-Manifest -Root $local
Copy-Item -LiteralPath (Join-Path $local 'MANIFEST.sha256') -Destination (Join-Path $published 'MANIFEST.sha256')

$semanticHash = ('ab' * 32)
$roundtripPath = Join-Path $receipts 'ROUNDTRIP_RECEIPT.json'
@{
    result = 'PASS'
    all_semantic_comparisons_pass = $true
    private_source_semantic_sha256 = $semanticHash
} | ConvertTo-Json | Set-Content -LiteralPath $roundtripPath -Encoding utf8

$releaseReceiptPath = Join-Path $receipts 'RELEASE_RECEIPT.json'
@{
    result = 'PASS'
    release_id = 'synthetic-accepted-v1'
} | ConvertTo-Json | Set-Content -LiteralPath $releaseReceiptPath -Encoding utf8

$acceptancePath = Join-Path $receipts 'ACCEPTANCE_RECEIPT.json'
$pointerPath = Join-Path $receipts 'release_pointer.yaml'
$result = & (Join-Path $ToolRoot 'New-QpsAcceptanceReceipt.ps1') `
    -LocalDist $local `
    -PublishedReleaseDirectory $published `
    -RoundtripReceiptPath $roundtripPath `
    -ReleaseReceiptPath $releaseReceiptPath `
    -ReleaseId 'synthetic-accepted-v1' `
    -SsotVersion '2.2' `
    -CodexCommit ('c' * 40) `
    -AbacusCommit ('a' * 40) `
    -LocalArtifactReference 'artifact-git:synthetic' `
    -OneDriveRelativePath 'QPS COST_Master/Published/synthetic-accepted-v1' `
    -OutputPath $acceptancePath `
    -BridgePointerOutput $pointerPath | ConvertFrom-Json

if ($result.disposition -ne 'ACCEPTED') { throw 'Synthetic acceptance did not reach ACCEPTED.' }
if (-not $result.all_artifact_hashes_match) { throw 'Synthetic artifact parity did not pass.' }
if ($result.qa_passed -ne $result.qa_total) { throw 'Synthetic QA parity count is incomplete.' }
if (-not (Test-Path -LiteralPath $pointerPath -PathType Leaf)) { throw 'Public release pointer was not written.' }

python -c "import json,sys,yaml; from jsonschema import validate; d=yaml.safe_load(open(sys.argv[1],encoding='utf-8')); s=json.load(open(sys.argv[2],encoding='utf-8')); validate(d,s); assert set(d)==set(s['required'])|{'confidentiality'}" $pointerPath $SchemaPath
if ($LASTEXITCODE -ne 0) { throw 'Public release pointer failed schema validation.' }

$badPublished = Join-Path $WorkRoot 'published-tampered'
Copy-Item -LiteralPath $published -Destination $badPublished -Recurse
Set-Content -LiteralPath (Join-Path $badPublished 'index.html') -Value '<html>tampered</html>' -NoNewline -Encoding utf8
$held = $false
try {
    & (Join-Path $ToolRoot 'New-QpsAcceptanceReceipt.ps1') `
        -LocalDist $local `
        -PublishedReleaseDirectory $badPublished `
        -RoundtripReceiptPath $roundtripPath `
        -ReleaseReceiptPath $releaseReceiptPath `
        -ReleaseId 'synthetic-accepted-v1' `
        -SsotVersion '2.2' `
        -CodexCommit ('c' * 40) `
        -AbacusCommit ('a' * 40) `
        -LocalArtifactReference 'artifact-git:synthetic' `
        -OneDriveRelativePath 'QPS COST_Master/Published/synthetic-accepted-v1' | Out-Null
} catch {
    $held = $true
}
if (-not $held) { throw 'Tampered published artifact did not force HOLD.' }

[ordered]@{ result = 'PASS'; disposition = $result.disposition; qa_total = $result.qa_total } | ConvertTo-Json
