# QPS and Triage Prompt Sequence

Purpose: adapt the chat-to-GitHub method for QPS and triage workstreams.

The core loop is:

```text
identify -> compress -> prune -> bridge -> prove -> record
```

For QPS and triage, the transferred object differs.

- QPS transfers offer, requirement, clarification, evidence and decision content.
- Triage transfers repo, PR, workflow, runtime, DoV and blocker content.

## 1. Object model

### QPS object types

```text
QPS_REQUIREMENT
QPS_OFFER_EVIDENCE
QPS_CLARIFICATION
QPS_NEGOTIATION_TOPIC
QPS_BT_DRIVER
QPS_PCA_FEATURE
QPS_DECISION_OBJECT
QPS_DEFERRED_RETURN
QPS_RISK
QPS_ACTION
```

### Triage object types

```text
TRIAGE_REPO
TRIAGE_PR
TRIAGE_WORKFLOW
TRIAGE_RUNTIME_PROBE
TRIAGE_DOV_GATE
TRIAGE_BLOCKER
TRIAGE_RECEIPT
TRIAGE_BRIDGE
TRIAGE_REPAIR
TRIAGE_ACTION
```

## 2. QPS prompt sequence

### QPS prompt 0: active work check

```text
Check whether there is already an active QPS PR or branch for this topic. Do not duplicate. Report repo, PR number, branch, title, draft state, workflow state and whether it matches this request.
```

Pass condition:

```text
One active QPS work object is named, or a new one is justified.
```

### QPS prompt 1: compress session into QPS objects

```text
Compress this session into QPS objects: requirements, offer evidence, clarification topics, negotiation topics, BT/PCA drivers, decisions, deferred returns, risks and actions. Separate source facts from inferred actions.
```

Pass condition:

```text
Each action can be linked to an offer, requirement, return package, SSOT row or decision object.
```

### QPS prompt 2: prune

```text
Prune QPS content into MUST keep, SHOULD keep and PARKED. MUST keep must be source-bound or directly actionable. PARK unsourced ideas and speculative improvements.
```

Pass condition:

```text
No unsourced claim is promoted to compliance or decision status.
```

### QPS prompt 3: bridge into repo artifacts

```text
Bridge the pruned QPS objects into repo artifacts. Prefer YAML, CSV or Markdown registry updates before generated Word, Excel, HTML or slides. Preserve requirement ID, offer reference, source locator, state, action owner and next evidence needed.
```

Pass condition:

```text
The resulting artifact is sortable, source-bound and reviewable.
```

### QPS prompt 4: prove

```text
Add the smallest proof for the QPS claim. This may be schema validation, row-count validation, source-locator validation, BT/PCA reproducibility, or generated-output parity.
```

Pass condition:

```text
A check exists that can fail when source binding, scoring or row structure is wrong.
```

### QPS prompt 5: return of experience

```text
Produce a QPS return-of-experience note: which evidence closed, which stayed DEFER, which rows changed state, what new questions were created, and what must be asked next.
```

Pass condition:

```text
The next QPS session can continue from explicit row IDs, states and next evidence needs.
```

## 3. Triage prompt sequence

### Triage prompt 0: active PR and repo check

```text
Check active triage PRs and branches across the relevant repos. Do not duplicate. Report repo, PR, branch, head SHA, workflow state and exact blocking gate.
```

Pass condition:

```text
The target repo and PR are explicit, and the first red or first missing proof is identified.
```

### Triage prompt 1: compress session into triage objects

```text
Compress this session into triage objects: repo, PR, workflow, runtime probe, DoV gate, blocker, receipt, bridge, repair and action. Separate observed facts from desired next steps.
```

Pass condition:

```text
Every claim has a repo, PR, SHA, workflow, file or receipt pointer where possible.
```

### Triage prompt 2: prune

```text
Prune triage into MUST fix, SHOULD improve and PARKED. MUST fix is limited to first red, missing receipt, missing runtime proof or exact DoV blocker.
```

Pass condition:

```text
Only one narrow repair target is promoted as the next execution step.
```

### Triage prompt 3: bridge

```text
Bridge triage evidence across repos. Bind exact source PR or receipt to DOW, KEB, child repo, or triage registry. Preserve repo, PR number, head SHA, workflow name, conclusion and disposition.
```

Pass condition:

```text
The bridge can distinguish ACCEPT, REJECT and DEFER without narrative guessing.
```

### Triage prompt 4: prove

```text
Add the smallest runtime proof for the blocker. Prefer a validator, probe, replay, fixture, smoke test or CI workflow. Rerun and capture workflow result.
```

Pass condition:

```text
A workflow, script or receipt proves the repair or records why it remains DEFER.
```

### Triage prompt 5: return of experience

```text
Produce a triage return-of-experience note: first red, repair attempted, result, new blocker, next repo/PR/SHA and whether DoV moved.
```

Pass condition:

```text
The next session can continue from the exact repo, PR, SHA and blocker.
```

## 4. QPS SSOT row template

```yaml
qps_item_id: QPS-ITEM-0001
object_type: QPS_REQUIREMENT
source_repo: CODEX
source_locator: TBD
requirement_id: TBD
offer_ref: TBD
state: DEFER
confidence: source_missing
bt_driver: null
pca_feature: null
decision_effect: none
next_evidence_needed: authoritative source locator or bidder return
lineage:
  chat_session: TBD
  originating_prompt: TBD
  created_by: chat_to_github_bridge
```

## 5. Triage SSOT row template

```yaml
triage_item_id: TRIAGE-ITEM-0001
object_type: TRIAGE_BLOCKER
repo: GBOGEB/CODEX
pr_number: null
head_sha: null
workflow: null
gate: null
state: DEFER
reason: evidence_missing
first_red: null
next_action: identify active PR and first blocking workflow
lineage:
  chat_session: TBD
  originating_prompt: TBD
  created_by: chat_to_github_bridge
```

## 6. Pickup prompt for QPS

```text
Pick up the active QPS PR or branch. First inspect current PRs, changed files, workflow results and source-bound rows. Continue only the next unchecked QPS wave. Do not create duplicate PRs. Preserve source locator, requirement ID, offer reference, state and next evidence needed.
```

## 7. Pickup prompt for triage

```text
Pick up the active triage PR or branch. First inspect current PRs, changed files, workflow results, head SHA and first red gate. Continue only the next unchecked triage wave. Do not create duplicate PRs. Preserve repo, PR, SHA, workflow, disposition and receipt lineage.
```

## 8. Uniform checks

Before commit:

```text
1. Is the repo owner clear?
2. Is the active PR clear?
3. Is the object SSOT, runtime proof, generated output, governance evidence or parked knowledge?
4. Is the next step low hanging fruit or first red?
5. Is there a validation path?
6. Is the source lineage preserved?
7. Did the PR body get updated?
```
