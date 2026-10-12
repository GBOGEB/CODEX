# CODE PURPLE — Recursive .self / pay_it_forward (candidate v0.1)

> **Status:** proposal in CODEX PR #984. **Authority:** CODEX GLOB/mesh closure control; this document is **not** a new scheduler, SSOT, security review or model-training claim. `authority_transfer=false`; `formal_credit_delta=0`; `engineering_credit_delta=0`.

## 1. Two spatial scales, three temporal states

- **Level 0 / overview:** Global input → census + method select → execute → evidence + admission → controlled output → self-return/forward-propagation.
- **Level 1 / zoom:** exact repo/PR/actor, process phases, Docker/mesh interfaces, check outcomes, first completed material blocker, feedback and receipt.
- **Time:** `N-1` (bound prior state) → `N` (actual observed run) → `N+1` (candidate next run, admissible only with evidence change). `N-2` is a useful prior-control comparison, **not** a mandatory extra execution.

The figure is a **lineage/process graph**, not a neural network and not a Sankey quantity chart unless actual magnitudes are bound to edges. Node weight may represent independently measured impact/degree, never arbitrary popularity. Return/up edges have different semantics from forward/down edges.

## 2. SIPOC with a process-neutral .self loop

`SIPOC` retains its five standard roles: Supplier / Input / Process / Output / Customer. The *additional* `SIPIC` view (term proposed here, not asserted as an external standard) foregrounds the **Iteration interface** through which `Output[N]` can become `Input[N+1]`. It does not rename or discard the canonical SIPOC Output.

- **S**: repo/domain authority, producer, previous iteration, receipt source.
- **I**: controlled source/pin, PR diff, test environment, previous accepted outputs, policy and constraints.
- **P**: a selected, plug-in process adapter.
- **O**: artefacts, observations, typed failures, immutable receipts, proposed controls, next-candidate output.
- **C**: original requester, authoritative child, downstream node, **same node (.self)**.
- **SIPIC iteration port (extra):** `input_next := reconcile(output_current, validated_delta, current_constraints)`.

Two **separate** self edges:
1. `SELF_REENTRY` (violet, dotted, upward/back): failed or incomplete bounded verification returns to the *same* owner/actor with first-red and changed evidence.
2. `PAY_IT_FORWARD` (teal, dashed, lateral/outward): a **proven, portable** method/guard/fixture/recipe is offered as a candidate to another consumer; consumer independently opts in and proves its own local compatibility. No source- or domain-authority transfer.

A third connection `CONTINUE_NEXT` (blue solid, down/forward) advances the ordinary process only when the relevant gate is met. `BLOCKED` (amber) carries a wait/reentry reason; `REPAIR` (rose) carries a scoped red.

### Iteration algebra

```text
Observation_N       = run(ProcessAdapter_N, Input_N, exact_environment_N)
Census_N            = reconcile(Observation_N, receipts_N, Census_N_minus_1)
Delta_N             = material_diff(Census_N, Census_N_minus_1)
Decision_N          = mesh_closure_control(first_BG, EX, QH, KR, DR, SR, DoV)
Input_N_plus_1      = verified(Output_N) + accepted(Delta_N) + current constraints
ProcessAdapter_N+1  = ProcessAdapter_N + approved configuration/guard changes only
```

An actual *model-weight* update is **not** implied. The governable improvement is a changed policy/config, tested code, cache, regression fixture, REX record, action choice, or safer operating envelope. The controller does not invent success or silently change security policy, acceptance thresholds or human attestations.

## 3. Method adapters (not competing governance owners)

| Adapter | Native steps | Trigger/use | Return |
|---|---|---|---|
| DMAIC | Define → Measure → Analyze → Improve → Control | General measured process-improvement lifecycle | Baseline, causal hypothesis, measured outcome, control plan |
| 3PR | Refresh → Probe → Rank | Observe present state/priority and first real blocker | Ranked admissible actions |
| MIP | Modernize → Innovate → Perpetuate | Only observed structural or recurrence gap | Fixed mechanism, improved measurable behavior, reusable prevention guard |
| 3PC | Prepare → Prove → Commit | Bounded transaction, child reentry, publication | Exact transaction receipt; HOLD until independent prove |
| 3P3 | Preserve/Pin → Propagate/Penetrate → Prove/Promote | Only after local DoV AND a measured cross-consumer generalisation gap | Single bounded consumer-specific propagation proof |
| DOW 12-cluster | Select + orchestrate relevant C1–C12 workers | Work requiring ABACUS processing/diagnostics; select by purpose and runtime availability | Scoped results, dependency state and derived analytics; no QPS promotion |

`3P*` is a selector/wildcard and **not** itself an executable gate. Method composition obeys the existing `federation/mesh/MESH_CLOSURE_CONTROLLER_v1.json` rule: 3PR → conditional MIP → conditional 3PC → conditional 3P3 → STOP. No ceremonial 3PC or 3P3. DMAIC can wrap one or more cycles. DOW is a worker plane rather than a rival authority.

## 4. The confidence/adaptation ladder

| Level | Name | What is established | Eligible next use |
|---|---|---|---|
| L0 | DECLARED | Configuration/script exists only | Discover/configure, not PASS |
| L1 | PREFLIGHT_EXECUTED | Reproducible parse/compile/Ruff/local checks and receipt | Scoped local repair |
| L2 | LOCAL_TESTED | Targeted smoke/testflight, explicit nonzero execution and result | Candidate local reuse |
| L3 | EXACT_HEAD_ADMITTED | Applicable CI terminal/green, review/security, zero unresolved material threads, exact SHA | Repo-native merge only |
| L4 | EXACT_MAIN_READBACK | Merged main SHA, postmerge checks, metrics and publication readback | Local Control/DoV when its actual terms are met |
| L5 | FORWARD_PROVEN | New consumer runs and binds independent parity/provenance checks and accepts reuse | Shared pattern, no transfer of child authority |

`SKIP`, `NEUTRAL`, pending, timed-out, zero-step or unavailable review are never upgraded to `PASS` by counting tests or confidence labels. Critical/S0/S1 and owner-only controls remain fail-closed.

## 5. Actual Code Purple iteration begun in PR #984

This table records **observed GitHub evidence**, not a simulation of executed CI:

| Temporal state | Observed work and bound state | Effect on next iteration |
|---|---|---|
| N−1 / baseline | CODEX main `4da26fdf7dce7d3500b773981c157df4cf265938`; no new Code Purple seed file in that baseline | Use existing GLOB/mesh/REX authority |
| N / first commit | New seed commit `ea37fa15ca1a9ccd504ca164204b8adabaf08837`; CODEX PR #984 opened Draft | Can now resolve method/admission vocabulary from a single structured seed |
| N / CI snapshot | 49 GitHub check records at the readback; `governance-adversary` and `render-regression` reported SUCCESS; `ruff` was NEUTRAL; numerous checks QUEUED/IN_PROGRESS | No merge credit; wait for current-head terminal checks before classification |
| N+1 / proposed | Extend the seed with process adapter, SIPOC/.self, pay-it-forward contract and navigable zoom viewer | New head **invalidates previous exact-head CI as merge evidence**; request fresh current-head readback |
| N+2 / gated future | A downstream repo independently consumes an accepted portability package | Count propagation only after an observed consumer execution/receipt, not by creating this document |

**Operational example of a *future* step change:** ABACUS #1857 identifies Python syntax/compile failure that TestPilot's `python_compile` can detect before push. For that change, an independently executed preflight would turn a late CI syntax red into a pre-push red. After local impact tests and merged exact-head proof, a standardized Python compile preflight could be offered to another participating repo. Do not claim reduced CI time without measuring it.

## 6. Pay-it-forward acceptance contract

A portable payload is a **candidate** until the following hold:

```yaml
edge_type: PAY_IT_FORWARD
from: repo/producer@exact_sha
to: repo/consumer@exact_sha
portable_asset: preflight|test_fixture|schema|repair_recipe|receipt_schema|dashboard
evidence:
  executed_steps: ">0"
  source_receipt_sha256: "<actual SHA-256>"
  source_status: PASS
privacy: SANITIZED
authority_transfer: false
consumer_acceptance: PENDING
required_next:
  - consumer validates its own source and local constraints
  - consumer runs independent parity/execution proof
  - consumer records new exact SHA and durable receipt
```

The payload never carries self-approval, implicit credentials, unreviewed security bypasses, private QPS engineering values, or inherited formal credit.

## 7. Visualization grammar

- **Primary process/downstream:** saturated blue, solid, visible arrowhead.
- **Repair to earlier step:** rose/red, solid, visible return arrowhead.
- **.self return/up/back:** violet, dotted, curved; same-node recurrence only if material delta.
- **Pay it forward/lateral:** teal dashed, independent consumer admission.
- **Completed/admitted:** dark green with mint fill.
- **Hold/external:** amber with explicit next trigger.
- **Authority/governance:** deep purple with **2.5–3 px contrasting borders**.
- **Unproven/candidate:** muted grey with visible state label.

Keep a *pinned* legend, a high-level viewport and a process-specific zoom view. The zoom rectangle must be an explanatory crop, not imply that a partial result is Global DoV.

## 8. Mandatory stop rules

1. When local bounded DoV is satisfied and no measured propagation gap exists: **STOP**.
2. If the first completed material red is attributable to a local fix: repair **only that root** and impacted retest.
3. If capacity, independent reviewer, owner setting, runner or physical ingress is missing: **HOLD/WATCH + REX + event-triggered next pulse**.
4. If the same observation would be recomputed without changed evidence: **do not repeat**.
5. Do not re-open closed QPS ranks 3–7 without controlled-source/pin/status change or regression; rank 8 still depends on CODEX publication and physical successor ingress.
6. Every acceptance or consumer use remains exact-SHA/receipt-bound; `authority_transfer=false` and zero formal credit by default.

## Navigation

- [Machine-readable seed](CODE_PURPLE_EXECUTION_SEED_20261012.yaml)
- [Interactive viewer](CODE_PURPLE_ITERATION_VIEWER.html)
- [Canonical mesh closure controller](MESH_CLOSURE_CONTROLLER_v1.json)
- [GLOB](../../GLOB.yaml)
- [MIP](../../MIP/README.md)
- [ABACUS TestPilot](https://github.com/GBOGEB/ABACUS/blob/main/docs/ci/TESTPILOT_PREFLIGHT.md)
- [ABACUS 12-cluster architecture](https://github.com/GBOGEB/ABACUS/blob/main/12CLUSTER_ARCHITECTURE_BOOK.md)
