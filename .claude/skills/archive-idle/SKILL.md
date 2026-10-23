---
name: archive-idle
description: Free RAM, page file and C: space by archiving idle Claude Code desktop sessions. Use when the user says "archive idle sessions", "too many sessions", "C: is full", "page file", or runs /archive-idle. Optional argument: "yesterday" (only sessions idle since before today) or "dry" (list only).
---

# Archive idle sessions

Each open desktop session keeps a process alive. On the owner's work PC, about 10 or more of them grow `C:\pagefile.sys` until C: fills up; that crashed sessions on 2026-10-22. Archiving stops a session's process. It is reversible: the session reopens from Sidebar > Archived.

`stop_session` does not help here: it only interrupts a running turn and leaves an idle session's process alive.

## Steps

1. **Measure** (PowerShell) with `tools/relief/Fix-Machine.ps1` from a checkout of CODEX `main`:
   ```powershell
   & "<codex-main>\tools\relief\Fix-Machine.ps1" -ListOnly
   ```
   On the owner's PC, `<codex-main>` is `C:\Users\gbonthuy\Documents\Codex\codex-tools`, a sparse worktree of `tools/` only. Update it with `git -C <codex-main> pull --ff-only`.

   Judge the load by **memory commit %** and free space. Ignore the Claude process count: the desktop app alone runs about 20 `claude.exe` helper processes.
2. **List** sessions with `mcp__ccd_session_mgmt__list_sessions` (limit 60). Split the list into:
   - running: `isRunning: true`. Never archive these.
   - idle: everything else. With the argument `yesterday`, keep only those whose `lastActivityAt` is before today.
3. **Show** the user the idle list, grouped as today and older, and say how many sessions are running.
   - With the argument `dry`, stop here.
   - If the user invoked `/archive-idle` themselves, that is their approval for the listed idle sessions.
   - Otherwise ask once before going on.
4. **Archive** each idle session with `mcp__ccd_session_mgmt__archive_session`, all calls in one message.
   - Archiving a parent also archives its finished side sessions, so "already archived" errors are expected. Skip them.
   - "Still has live work" (a background task or Remote Control client): leave the session and report it.
5. **Measure again** and report free GB, page file GB and commit % before and after. The page file only fully shrinks after a reboot (`Fix-Machine.ps1 -Reboot`, which asks first).

## Never

- Never archive this session (`self`) or one that is running.
- Never delete sessions. Use `delete_session` only when the user explicitly asks to delete.
