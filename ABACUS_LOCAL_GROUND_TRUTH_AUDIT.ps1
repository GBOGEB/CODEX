# ===== ABACUS LOCAL GROUND-TRUTH AUDIT =====
# Run this from a fresh PowerShell window on the Windows machine that contains
# the real Master_Input workspace. It is read-only: it writes audit output files
# but does not git add, commit, push, move, or delete anything.

$root = "C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Master_Input"
Set-Location $root
$auditDir = Join-Path $root "_AUDIT"
New-Item -ItemType Directory -Force -Path $auditDir | Out-Null

# 1. Real tracked file count + list (what is actually tracked by the root ABACUS repo).
git --no-pager ls-files > "$auditDir\TRACKED_files.txt"
$tracked = (Get-Content "$auditDir\TRACKED_files.txt").Count

# 2. Embedded repos: find every nested .git below root (candidate ghost/local-only repos).
Get-ChildItem -Recurse -Force -Directory -Filter ".git" -ErrorAction SilentlyContinue |
  Where-Object { $_.Parent.FullName -ne $root } |
  ForEach-Object { $_.Parent.FullName.Replace($root,'.') } |
  Out-File "$auditDir\EMBEDDED_repos.txt"
$embedded = (Get-Content "$auditDir\EMBEDDED_repos.txt" -ErrorAction SilentlyContinue).Count

# 3. Top-level folders + whether each is tracked in ABACUS or workspace-only ghost content.
$folders = Get-ChildItem $root -Directory | ForEach-Object {
    $name = $_.Name
    $hasGit = Test-Path (Join-Path $_.FullName ".git")
    $trackedHere = git --no-pager ls-files -- "$name/" 2>$null | Select-Object -First 1
    [PSCustomObject]@{
        Folder      = $name
        OwnGitRepo  = if($hasGit){'EMBEDDED-REPO'}else{'-'}
        InABACUS    = if($trackedHere){'TRACKED'}else{'GHOST (not in ABACUS)'}
    }
}
$folders | Format-Table -AutoSize
$folders | Export-Csv "$auditDir\FOLDER_MAP.csv" -NoTypeInformation

# 4. Backup bloat locations.
Get-ChildItem -Recurse -Directory -Filter "BACKUPS" -ErrorAction SilentlyContinue |
  Select-Object FullName | Out-File "$auditDir\BACKUP_folders.txt"

Write-Host "`n===== SUMMARY ====="
Write-Host "Tracked files in ABACUS : $tracked"
Write-Host "Embedded ghost repos    : $embedded"
Write-Host "Audit written to        : $auditDir"
Write-Host "`nOpen _AUDIT\FOLDER_MAP.csv — that is the tracked-vs-ghost map."
