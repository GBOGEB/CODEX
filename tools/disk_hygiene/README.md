# Disk hygiene

`disk_hygiene.py` finds byte-identical duplicate files and stale git clones on the owner's Windows PC. With `--apply`, it sends the extra copies to the Recycle Bin. It needs only Python 3.12 and the standard library.

```powershell
python tools\disk_hygiene\disk_hygiene.py                    # dry run: report only
python tools\disk_hygiene\disk_hygiene.py --apply            # also recycle the extra copies
python tools\disk_hygiene\disk_hygiene.py --roots D:\a D:\b  # scan other folders
python tools\disk_hygiene\disk_hygiene.py --min-mb 5 --min-age-days 14
```

## Which copy is kept

Duplicates are files with the same SHA-256. Each group keeps one copy, chosen in this order:

1. **The most normal name.** Penalties apply to `(1)`, `copy`/`kopie`, `recovered`, `AutoRecovered`, `backup`/`old`, `tmp` and OneDrive `-MACHINENAME` conflict suffixes.
2. The most recently modified copy.
3. The shortest path.

## Safety

- **Recycle Bin only:** copies go to the Recycle Bin, never straight to deletion. Every move is written to `recycled_<stamp>.csv`, so it can be restored. Emptying the Recycle Bin stays a manual step.
- **Re-checked before each move:** a copy is re-hashed right before it is moved. It is skipped if it changed, or if the kept copy is gone.
- **Never touched:**
  - `.git`, `node_modules`, virtualenvs and caches
  - OneDrive cloud-only files, because hashing them would download them
  - files changed in the last 7 days
  - files under `--min-mb`
- **Stale git clones are reported, never removed.** A clone counts as stale when it has no local changes, no unpushed commits and no stashes.

## Output

Reports go to `%LOCALAPPDATA%\disk-hygiene\reports\`, never into the repo: `report_<stamp>.json`, `report_<stamp>.md` and, with `--apply`, the CSV manifest.

## Schedule

On the owner's PC, the Windows task **"Disk Hygiene (weekly)"** runs it with `--apply` on Mondays at 08:30. After this lands, point that task at a CODEX checkout of this file instead of the old `_tools` copy.
