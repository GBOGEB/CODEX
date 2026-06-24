# Chat to GitHub Prompt Sequence

Purpose: provide a uniform method for moving knowledge from a chat session into GitHub with checks, pruning and bridge logic.

## Phase 0: identify active work

Prompt:

```text
Check whether there is already an active PR for this workstream today. Do not duplicate. Report repo, PR number, title, branch, draft state and whether the scope matches this request.
```

Expected reply:

```text
Active PR found or no matching PR found. If found, continue it. If not found, create a new branch and draft PR.
```

Check:

- active PR exists or not
- branch is known
- repo is known
- duplicate risk is resolved

## Phase 1: compress session into transferable knowledge

Prompt:

```text
Convert this session into structured handover: user intent, decisions, artifacts, open questions, implementation waves, next three moves and risks. Separate facts from inferred next steps.
```

Expected reply:

```text
A manifest with conversation pairs, artifact list, current PR state and next steps.
```

Check:

- every major user prompt is represented
- every agent decision is represented
- active PR and branch are named
- incomplete or blocked work is explicit

## Phase 2: prune

Prompt:

```text
Prune the handover into three layers: MUST keep, SHOULD keep, and PARKED. Preserve only actionable engineering facts in MUST keep. Put ideas without implementation path into PARKED.
```

Expected reply:

```text
A pruned action list that can be committed to the repo without chat noise.
```

Check:

- no generic narrative in implementation files
- no duplicate task descriptions
- no generated output treated as SSOT

## Phase 3: bridge into GitHub artifacts

Prompt:

```text
Map the pruned knowledge into repository artifacts. Create or update only the files needed for the next wave. Prefer small commits and keep the active PR draft until validation passes.
```

Expected reply:

```text
Files created or updated, with commit summaries and validation status.
```

Check:

- file paths are explicit
- scope is limited to next wave
- PR body is updated
- no duplicate PR is created

## Phase 4: runtime proof

Prompt:

```text
Add the smallest runtime proof for the current architecture claim. Add validation before rendering. Add CI once local commands exist.
```

Expected reply:

```text
Validator, sample data and CI gate exist. Workflow status is checked.
```

Check:

- validator exists
- sample SSOT exists
- CI runs on the correct paths
- validation result is reported

## Phase 5: return of experience

Prompt:

```text
Produce a return-of-experience note: what worked, what was blocked, what was learned, what should be standardized, and what should be pruned before the next session.
```

Expected reply:

```text
A short lessons-learned note and standardized next-session prompt.
```

Check:

- blocked tool calls are named without over-explaining
- next actions are ordered
- scope remains narrow

## Uniform pickup prompt

```text
Pick up active PR <repo>#<number> on branch <branch>. First inspect PR status, changed files and workflow results. Then continue only the next unchecked wave. Do not create a duplicate PR. Update the PR body and handover manifest after changes.
```

## Useful questions to ask

Ask these when the next step is ambiguous:

1. Which repository owns the source of truth for this artifact?
2. Is this architecture, runtime proof, generated output or governance evidence?
3. Is there an existing active PR or branch?
4. What is the smallest next file that proves the claim?
5. What validation should fail if the change is wrong?
6. Should this be SSOT, generated output or parked knowledge?
7. What must be preserved as stable identity?
8. What should be pruned before commit?
