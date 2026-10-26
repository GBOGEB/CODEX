# Machine relief

`Fix-Machine.ps1` is a PowerShell 7 tool that keeps the owner's Windows work PC able to run several Claude Code sessions at once. It works like the ABACUS stack tools (`tools/stack`): **scan** first, then **fix stage by stage until unblocked**, **report**, and offer an **extended final step** when the earlier stages are not enough.

It was written on 2026-10-22/23, after C: filled up repeatedly while about 30 sessions were open. On a full disk, sessions crash and git can truncate tracked files.

| File | What it does |
|---|---|
| `Relief-Tools.cmd` | Double-click menu for everything below |
| `Fix-Machine.ps1` | Scan, run the stages, report, log |
| `Assert-FreeSpace.ps1` | Read-only preflight guard: disk, commit charge, fsmonitor daemons. Has a one-line `-Hook` mode for a Claude Code `SessionStart` hook |
| `tests/Test-ReliefGuard.ps1` | Plain PowerShell test of the guard's thresholds and hook output; CI runs it (`.github/workflows/relief-guard.yml`) |
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
| `fsmonitor` | Memory commit held by `git fsmonitor--daemon run` processes, one per worktree | git restarts a daemon on the next git command in that worktree. The census comes from `Assert-FreeSpace.ps1 -Json`, which matches the command line, so other `git.exe` processes are never stopped |
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

## Session preflight guard

`Assert-FreeSpace.ps1` checks the machine before a session starts. It changes nothing.

| Verdict | When | Exit |
|---|---|---|
| **PASS** | none of the conditions below | 0 |
| **WARN** | commit ≥ `-WarnCommitPct` (80 %), or more than `-MaxFsmonitor` (20) fsmonitor daemons | 0 |
| **BLOCKED** | C: free < `-MinFreeGB` (5), or commit ≥ `-MaxCommitPct` (90 %) | 2 |
| **UNREADABLE** | disk or commit state cannot be read, or `-WarnCommitPct` > `-MaxCommitPct` | 3 |

The fsmonitor census is advisory: if it cannot be read, the line says `fsmonitor n/a` and the verdict ignores it.

```powershell
.\Assert-FreeSpace.ps1                    # one line, plus a warning when BLOCKED
.\Assert-FreeSpace.ps1 -Json              # receipt codex.relief.disk_preflight.v2 (includes fsmonitor PIDs)
.\Assert-FreeSpace.ps1 -Hook              # one line for a SessionStart hook
.\Assert-FreeSpace.ps1 -WarnCommitPct 75 -MaxCommitPct 85 -MaxFsmonitor 10
```

Example `-Hook` line:

```text
RELIEF_GUARD WARN: C: 11.6 GiB free (min 5) | commit 82.0% (warn 80, block 90) | fsmonitor 27 (1.07 GiB, warn >20) | next: archive idle sessions (/archive-idle); Fix-Machine.ps1 -Stage fsmonitor -Yes | 104 ms
```

**Speed.** The guard reads nothing through CIM, because `Win32_OperatingSystem` takes 0.6–1.2 s under load. Free space comes from `System.IO.DriveInfo`. Commit charge comes from `GlobalMemoryStatusEx`, and the fsmonitor command lines from `NtQueryInformationProcess`, both through a P/Invoke type built with `Reflection.Emit` (no `Add-Type` compile). On 2026-10-26, at 80–83 % commit, the script body took 93–138 ms (one cold outlier of 227 ms). The trailing `| N ms` in the line is that figure. **`pwsh` startup adds 1.7–2.6 s under load** (the whole hook took 0.6–0.85 s in a calmer moment at 05:30), and Windows PowerShell 5.1 starts in 4–6 s, so give the hook a timeout of at least 10 s.

### Installing it as a Claude Code hook (owner applies)

`SessionStart` hooks cannot block a session. The guard therefore uses the hook channels like this: PASS and WARN print one line on stdout with exit 0, and Claude Code adds it to the session context. BLOCKED prints one line on stderr with exit 2, which Claude Code shows to you. UNREADABLE prints on stderr with exit 3, a non-blocking hook error.

Merge this into `~/.claude/settings.json`, pointing at a checkout of CODEX `main` (not a worktree that gets removed):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -NoProfile -NonInteractive -File \"C:/Users/gbonthuy/Documents/Codex/2026-10-19/upd/work/CODEX/tools/relief/Assert-FreeSpace.ps1\" -Hook",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Use forward slashes in the path; the hook command may run through Git Bash. Check it by hand first: run the same command and confirm it prints one `RELIEF_GUARD` line and exits 0 or 2.

## fsmonitor daemons

`core.fsmonitor=true` is set in the **system** gitconfig (`C:\Program Files\Git\etc\gitconfig`), so every worktree that runs a git command starts its own `git fsmonitor--daemon`, and it stays alive. On 2026-10-26, 51–90 daemons held 2.3–3 GB. Stopping them (the `fsmonitor` stage) took commit from 88 % to 80–82 %, but they respawned within about 20 minutes as sessions kept running git.

The stage is relief, not a fix. For a lasting fix the owner should pick one of:

- **Turn it off system-wide** (admin shell): `git config --system core.fsmonitor false`. Repos that want it can still set `core.fsmonitor=true` locally.
- **Prune stale worktrees**, so fewer daemons can start: `git worktree list`, then `git worktree remove <path>` for merged branches, and `git worktree prune`. In pipeline-automation-hub, `tools/workstation/Invoke-WorkspaceAudit.ps1` lists candidates.

Neither is done by these tools.

## Lessons from 2026-10-26

- **The page file can fill C: in minutes.** Page-file growth took C: from 3.2 GB to 0.25 GB free in about 15 minutes during a worker wave.
- **The `onedrive` stage needs OneDrive running.** `attrib +U` only marks files; the OneDrive client dehydrates them. With OneDrive stopped, nothing is freed.
- **A restart alone is not enough.** After the owner's restart, commit was 52 %. It climbed back to 88 % within about 20 minutes as the sessions came back. Archive idle sessions and stop the fsmonitor daemons as well.
- **The fsmonitor daemons were the biggest single reclaimable item:** 2.3–3 GB of commit.

## Known behaviour

- **OneDrive frees space in the background.** Right after the `onedrive` stage, `FreeAfterGB` barely moves. Re-scan a few minutes later.
- **Open Outlook files stay local.** `.pst` files that Outlook has open, such as `Documents\archive.pst` (8.5 GB), cannot go online-only. They are counted in the `onedrive` estimate anyway. Move live PSTs out of OneDrive to stop that.
- **The `sessions` stage replaces your clipboard** with `/archive-idle`.
- **No CLI can archive desktop sessions.** That is why the `sessions` stage hands off to the `/archive-idle` skill inside the app.
