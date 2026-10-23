# Machine relief

`Fix-Machine.ps1` is a PowerShell 7 tool that keeps the owner's Windows work PC able to run several Claude Code sessions at once. It works like the ABACUS stack tools (`tools/stack`): **scan** first, then **fix stage by stage until unblocked**, **report**, and offer an **extended final step** when the earlier stages are not enough.

It was written on 2026-10-22/23, after C: filled up repeatedly while about 30 sessions were open. On a full disk, sessions crash and git can truncate tracked files.

| File | What it does |
|---|---|
| `Relief-Tools.cmd` | Double-click menu for everything below |
| `Fix-Machine.ps1` | Scan, run the stages, report, log |
| `../disk_hygiene/disk_hygiene.py` | Weekly duplicate-file cleaner; see its README |
| skill `/archive-idle` | Archives idle Claude sessions. Lives in `~/.claude/skills`; run it in any session |

The tool reads the OneDrive root from `%OneDriveCommercial%`, falling back to `%OneDrive%`. Two parameters override which folders it may free and which it protects: `-FreeDirs` and `-Protect`. Their defaults are the owner's layout.

## States

The tool reports the machine in one of three states:

| State | When | Exit code |
|---|---|---|
| **UNBLOCKED** | C: free ≥ `-TargetGB` (10) and memory commit < `-MaxCommitPct` (80 %) | 0 |
| **TIGHT** | between the other two | 0 |
| **BLOCKED** | C: free < `-MinFreeGB` (5) or commit ≥ 90 % | 2 |

The tool shows the Claude process count but does not judge by it. The desktop app runs about 20 helper processes of its own. Commit charge is what grows `C:\pagefile.sys`.

## Stages

The stages run cheapest first. The run stops as soon as the machine is unblocked, unless you pass `-All` or `-Stage`.

| Stage | Frees | Safe because |
|---|---|---|
| `temp` | `%TEMP%` files older than 2 days | Claude task folders (`\claude\`) are never touched, and locked files are skipped |
| `pkgcache` | pip and npm download caches | They refill on the next install |
| `onedrive` | Unpinned OneDrive documents become online-only | Nothing is deleted, and files re-download when opened. `Master_Input`, `ariana_trace_project`, `Documents\.git` and `Documents\Development` stay pinned, and a guard re-checks them afterwards |
| `sessions` | Memory commit, if it is ≥ `-MaxCommitPct` | Copies `/archive-idle` to the clipboard, so you paste it into any session, then waits. Archiving can be undone |
| **reboot** (extended) | The page file. It grows under load and shrinks only on restart | Runs only with `-Reboot`. It asks first, waits 5 minutes, and `shutdown /a` cancels it |

## CLI

```powershell
.\Fix-Machine.ps1 -ListOnly                 # scan, change nothing (add -Json for machine-readable output)
.\Fix-Machine.ps1 -DryRun                   # what every stage would free
.\Fix-Machine.ps1                           # stages until unblocked, asks before each one
.\Fix-Machine.ps1 -Yes                      # same, without prompts
.\Fix-Machine.ps1 -Stage temp,pkgcache -Yes # only these stages
.\Fix-Machine.ps1 -All -Reboot              # every stage, then offer the restart
.\Fix-Machine.ps1 -Watch 300                # re-scan every 5 min; beeps and says what to run when BLOCKED
.\Fix-Machine.ps1 -TargetGB 15 -MaxCommitPct 75   # stricter targets
.\Fix-Machine.ps1 -InstallAlias             # adds `relief` to your PowerShell profile
```

After `-InstallAlias`, `relief -ListOnly`, `relief -DryRun` and the other commands work from any folder.

Each run writes a JSON record (start scan, every stage, end scan, state) to `%LOCALAPPDATA%\machine-relief\logs\`.

## Known behaviour

- **OneDrive frees space in the background.** Right after the `onedrive` stage, `FreeAfterGB` barely moves. Re-scan a few minutes later.
- **Open Outlook files stay local.** `.pst` files that Outlook has open, such as `Documents\archive.pst` (8.5 GB), cannot go online-only. They are counted in the `onedrive` estimate anyway. Move live PSTs out of OneDrive to stop that.
- **The `sessions` stage replaces your clipboard** with `/archive-idle`.
- **No CLI can archive desktop sessions.** That is why the `sessions` stage hands off to the `/archive-idle` skill inside the app.
