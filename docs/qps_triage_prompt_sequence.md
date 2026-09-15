# QPS and Triage Prompt Sequence

Purpose: adapt the chat-to-GitHub method for QPS and triage workstreams, including `/cryoplant-project`, DOW and KEB lanes.

The core loop is:

```text
identify -> compress -> prune -> bridge -> prove -> record
```

For QPS and triage, the transferred object differs.

- QPS transfers offer, requirement, clarification, evidence and decision content.
- Triage transfers repo, PR, workflow, runtime, DoV and blocker content.
- Cryoplant transfers source-bound engineering evidence, acceptance state, cost/BOM/RTM deltas and remaining blockers.
- DOW transfers decision/object/workflow state and downstream disposition authority.
- KEB transfers executable knowledge/evidence receipts, runtime proof and exact-source replay evidence.

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

### Cryoplant object types

```text
CRYO_REQUIREMENT
CRYO_OFFER_EVIDENCE
CRYO_RTM_ROW
CRYO_BOM_SOURCE
CRYO_MTO_SOURCE
CRYO_CALCULATION
CRYO_INTERFACE
CRYO_SAFETY_CASE
CRYO_COST_OBJECT
CRYO_ACCEPTANCE_STATE
CRYO_DEFERRED_BLOCKER
CRYO_ACTION
```

### DOW object types

```text
DOW_DECISION_OBJECT
DOW_WORKFLOW_STATE
DOW_DISPOSITION
DOW_ACCEPT_RECEIPT
DOW_REJECT_RECEIPT
DOW_DEFER_RECEIPT
DOW_CHILD_BINDING
DOW_GOVERNANCE_GATE
DOW_ACTION
```

### KEB object types

```text
KEB_KNOWLEDGE_ATOM
KEB_SOURCE_RECEIPT
KEB_RUNTIME_PROOF
KEB_REPLAY_EVIDENCE
KEB_EXACT_SHA_BINDING
KEB_VALIDATION_RESULT
KEB_DOWNSTREAM_CONSUMER
KEB_DEFER_REASON
KEB_ACTION
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

## 4. Cryoplant prompt sequence

### Cryoplant prompt 0: active work check

```text
Check active /cryoplant-project PRs and branches for this engineering topic. Do not duplicate. Report PR number, branch, head SHA, title, workflow state and exact blocker or evidence state.
```

Pass condition:

```text
The active cryoplant target is explicit and not mixed with an unrelated repair unless the PR already owns that wave.
```

### Cryoplant prompt 1: compress into engineering objects

```text
Compress this session into cryoplant objects: requirement, offer evidence, RTM row, BOM/MTO source, calculation, interface, safety case, cost object, acceptance state, deferred blocker and action. Separate source facts from inferred actions.
```

Pass condition:

```text
Every promoted engineering claim has a source locator, row ID, file digest, PR receipt or explicit DEFER reason.
```

### Cryoplant prompt 2: prune

```text
Prune cryoplant content into PASS-candidate, DEFER, BLOCKED and PARKED. Do not promote external-scope or owner-scope evidence to QPLANT compliance unless the source boundary proves it.
```

Pass condition:

```text
Formal engineering credit only moves when the source-bound evidence clears the defined gate.
```

### Cryoplant prompt 3: bridge

```text
Bridge cryoplant evidence to QPS, DOW and KEB. Preserve repo, PR, SHA, source file, digest, requirement/RTM row, state, downstream consumer and next evidence needed.
```

Pass condition:

```text
The same evidence object can be consumed by QPS ranking, DOW disposition and KEB replay without changing identity.
```

### Cryoplant prompt 4: prove

```text
Add the smallest proof for the cryoplant claim: source hash, row-count check, RTM link check, BOM/MTO denominator check, calculation replay, render parity or CI validation.
```

Pass condition:

```text
A failing source, row, digest or replay changes the state back to DEFER or FAIL.
```

### Cryoplant prompt 5: return of experience

```text
Produce a cryoplant return-of-experience note: what closed, what stayed DEFER, exact source identities recovered, remaining first red and next authoritative evidence required.
```

Pass condition:

```text
The next cryoplant session can continue from exact source identity, PR, SHA, row and blocker.
```

## 5. DOW prompt sequence

### DOW prompt 0: disposition boundary check

```text
Check the DOW consumer/decision object for this topic. Report source PR, child PR, head SHA, receipt, disposition state and whether DOW has authority to ACCEPT, REJECT or DEFER.
```

Pass condition:

```text
DOW authority is explicit and does not silently reinterpret upstream evidence.
```

### DOW prompt 1: compress into decision objects

```text
Compress this session into DOW decision objects: upstream evidence, downstream consumer, acceptance predicate, rejection predicate, defer reason, child binding and governance gate.
```

Pass condition:

```text
Each DOW state has a predicate and a linked upstream evidence object.
```

### DOW prompt 2: prune

```text
Prune DOW content into ACCEPT-ready, REJECT-ready and DEFER. DEFER must name the missing predicate or evidence source.
```

Pass condition:

```text
No DOW ACCEPT is recorded without a source-bound upstream proof.
```

### DOW prompt 3: bridge

```text
Bridge DOW decisions to KEB and child repositories. Preserve exact source PR, receipt, SHA, child target, disposition and reason.
```

Pass condition:

```text
The child can consume a DOW decision without guessing why the state is ACCEPT, REJECT or DEFER.
```

### DOW prompt 4: prove

```text
Add the smallest DOW proof: predicate table, receipt binding, child acceptance file, workflow check or disposition registry update.
```

Pass condition:

```text
The DOW state is reproducible from evidence rather than narrative.
```

### DOW prompt 5: return of experience

```text
Record DOW return-of-experience: accepted receipts, rejected receipts, deferred predicates, child bindings and next source needed.
```

Pass condition:

```text
The next DOW session can continue from exact receipt and predicate state.
```

## 6. KEB prompt sequence

### KEB prompt 0: receipt check

```text
Check the KEB evidence receipt for this topic. Report repo, PR, branch, SHA, source object, replay status, validation state and downstream consumer.
```

Pass condition:

```text
The KEB receipt is exact-SHA bound or explicitly DEFER_SOURCE_MISSING.
```

### KEB prompt 1: compress into knowledge atoms

```text
Compress this session into KEB atoms: source receipt, knowledge atom, runtime proof, replay evidence, exact-SHA binding, validation result, downstream consumer, defer reason and action.
```

Pass condition:

```text
Each atom has a stable identity and is replayable or explicitly deferred.
```

### KEB prompt 2: prune

```text
Prune KEB content into replayable, evidence-only, deferred and parked. Only replayable atoms can be promoted to runtime proof.
```

Pass condition:

```text
Knowledge is not promoted from text memory alone; it has a receipt or source binding.
```

### KEB prompt 3: bridge

```text
Bridge KEB receipts to DOW, QPS and cryoplant. Preserve source, SHA, proof type, validation result, disposition and downstream consumer.
```

Pass condition:

```text
DOW can consume KEB without re-performing source discovery.
```

### KEB prompt 4: prove

```text
Add the smallest KEB proof: schema validation, source hash check, replay script, runtime probe, receipt generator or CI check.
```

Pass condition:

```text
A KEB atom can be rechecked and produces the same receipt or a controlled failure.
```

### KEB prompt 5: return of experience

```text
Record KEB return-of-experience: atom created, receipt generated, replay status, downstream consumer, defer reason and next proof needed.
```

Pass condition:

```text
The next KEB session can continue from exact atom ID, receipt and replay state.
```

## 7. QPS SSOT row template

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

## 8. Triage SSOT row template

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

## 9. Cryoplant SSOT row template

```yaml
cryo_item_id: CRYO-ITEM-0001
object_type: CRYO_DEFERRED_BLOCKER
repo: GBOGEB/cryoplant-project
pr_number: null
head_sha: null
requirement_id: null
rtm_row: null
source_locator: null
source_digest: null
state: DEFER
reason: source_missing
next_evidence_needed: authoritative source identity and digest
lineage:
  chat_session: TBD
  originating_prompt: TBD
  created_by: chat_to_github_bridge
```

## 10. DOW SSOT row template

```yaml
dow_item_id: DOW-ITEM-0001
object_type: DOW_DISPOSITION
source_repo: null
source_pr: null
source_sha: null
receipt_id: null
child_repo: null
child_pr: null
disposition: DEFER
predicate: source_missing
reason: upstream proof not sufficient for ACCEPT or REJECT
next_action: recover or bind exact upstream receipt
lineage:
  chat_session: TBD
  originating_prompt: TBD
  created_by: chat_to_github_bridge
```

## 11. KEB SSOT row template

```yaml
keb_item_id: KEB-ITEM-0001
object_type: KEB_SOURCE_RECEIPT
source_repo: null
source_pr: null
source_sha: null
source_locator: null
source_digest: null
replay_status: DEFER
validation_result: DEFER_SOURCE_MISSING
downstream_consumer: null
next_action: create exact-SHA receipt or record controlled defer
lineage:
  chat_session: TBD
  originating_prompt: TBD
  created_by: chat_to_github_bridge
```

## 12. Pickup prompts

### QPS pickup

```text
Pick up the active QPS PR or branch. First inspect current PRs, changed files, workflow results and source-bound rows. Continue only the next unchecked QPS wave. Do not create duplicate PRs. Preserve source locator, requirement ID, offer reference, state and next evidence needed.
```

### Triage pickup

```text
Pick up the active triage PR or branch. First inspect current PRs, changed files, workflow results, head SHA and first red gate. Continue only the next unchecked triage wave. Do not create duplicate PRs. Preserve repo, PR, SHA, workflow, disposition and receipt lineage.
```

### Cryoplant pickup

```text
Pick up active /cryoplant-project work. First inspect open PRs, changed files, workflow results, head SHA, source locators and first engineering blocker. Continue only the next unchecked cryoplant wave. Do not create duplicate PRs. Preserve source identity, digest, RTM row, requirement ID, disposition and next evidence needed.
```

### DOW pickup

```text
Pick up active DOW work. First inspect upstream receipt, source PR/SHA, child binding and disposition predicate. Continue only the next unchecked DOW wave. Do not create duplicate PRs. Preserve ACCEPT/REJECT/DEFER reason and downstream consumer.
```

### KEB pickup

```text
Pick up active KEB work. First inspect source receipt, exact SHA, replay status, validation result and downstream consumer. Continue only the next unchecked KEB wave. Do not create duplicate PRs. Preserve atom ID, receipt ID, source digest and replay state.
```

## 13. Uniform checks

Before commit:

```text
1. Is the repo owner clear?
2. Is the active PR clear?
3. Is the object SSOT, runtime proof, generated output, governance evidence or parked knowledge?
4. Is the next step low hanging fruit, first red or first missing proof?
5. Is there a validation path?
6. Is the source lineage preserved?
7. Is the DOW/KEB/child bridge explicit where needed?
8. Did the PR body get updated?
```
