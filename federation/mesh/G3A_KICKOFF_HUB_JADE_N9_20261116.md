<!-- markdownlint-disable MD013 MD060 -->
# G3A kickoff record — Hub JADE N+9 / TOP21 parent→child stack

Status: **PROPOSAL (not launched).** This is a bounded-mission kickoff record in the
`G3A` namespace defined by ABACUS `docs/ci/G3A_GOVERNED_THREE_ADVANCE.md`. It is the
"next ambitious slice" / "bounded next three advances" composite from
[`SEMANTIC_ALIAS_CONVERGENCE_P0007.md`](SEMANTIC_ALIAS_CONVERGENCE_P0007.md). It is not a
CLOSE action, background dispatch, merge, waiver, review or ruleset change. Global semantic
authority stays with CODEX draft PR #1059; no new SSOT or scheduler is introduced.

Evidence basis: the weekly MIP handover read at 2026-11-16 ~07:20 UTC (7 created-at days
2026-11-09..15). Frozen accepted rate **0/65**, live weighted rate **NULL**. Disposition at that
readback: `MERGE_ADMISSION_HOLD / NO_SCALE / NO_MERGE`. That disposition is inherited, not re-measured.

## Kickoff inputs

| Field | Value |
| --- | --- |
| `mission_id` | `G3A-HUB-JADE-N9-20261116` |
| source repository | `GBOGEB/pipeline-automation-hub` (read-only observer of ABACUS #2746/#2590 and CODEX required checks) |
| `start_n` | `0` — no accepted `g3a_n` checkpoint exists yet in this namespace (historical N+k horizons counted pulses and are not reinterpreted) |
| `target_n` | `3` (A1, A2, A3), stop early on a material blocker |
| objective | Move parent #1154 then stacked child #1155 from exact-head RED to owner-admitted, then take one scheduled CONTROL pulse |
| authorized expected HEAD SHA | **UNRESOLVED.** Handover heads were `859e5312…` (#1154), `63c55fd0…` (#1155) and master `9f4b9799…`; hub master has since advanced. The verifier must re-resolve full 40-char SHAs at launch and reject a mismatch. |
| per-path ownership | #1154 lane: JADE offline browser fixed-source baseline. #1155 lane: N11 `source_repos==21` roster and digest. Disjoint files; one integrator. |
| vetoes | Independent review, security gate, owner admission. No auto-merge, no waiver, no fabricated approval. |
| budgets | Workers: 1 integrator, no scale-up from one pulse. Time: owner sets at launch. |
| receipt destination | `mission-control/v2/handoff/closeout/` in the Hub, as a draft PR (do not merge unless green) |

## Checkpoints

| Gate | DMAIC/MIP | Action | DoD | DoV (exact SHA, native run/job/attempt) | Stop condition |
| --- | --- | --- | --- | --- | --- |
| **A1 / N+1** | Define + Measure | `READ` then `RED` | Re-resolve #1154/#1155 heads, effective required contexts and open review threads (5 on #1154). Attribute the first-red of #1154 run `43809756062` and #1155 run `43809756348` with owner. | Source-bound diagnosis naming repo + path/contract + step + predicate + context. UNKNOWN is never PASS. | Heads or required contexts cannot be resolved. |
| **A2 / N+2** | Analyze + Improve | `RED` repair | Repair #1154 (fixed planning-source baseline) in its own PR. Then rebase #1155 on the admitted parent and repair the 21-source roster. | Two exact-head positive receipts plus tamper negatives; 21/21 roster; privacy masks; FPC PASS; zero open threads; eligible independent approval. Matched numerators/denominators reported. | Parent not admitted by the owner, or review unavailable. |
| **A3 / N+3** | Control + Perpetuate | `RECEIPT` / `WATCH` | Qualify the integrated source: negative controls, recurrence, rollback and drift plan, handover. | One existing scheduled Monday census succeeds with the post-integration source; no new cron. Run IDs, artifact digest and checkout SHA bound. | Child activation not merged, or the pulse is not comparable. |

`ADVANCE` is only credited per gate when its DoV is met. Missing, stale, skipped or failing proof does
not increment N. Queued jobs are never counted as success.

## Independent lane (not credited to N)

Read-only audit of ABACUS #2590 (title `DO NOT MERGE`, merged 2026-11-12, `dfdf4d7b…`) against the
merge-time effective ruleset, and the open H08 RED-canary lane (`h08_canary.py attempt` is an owner action). This
lane may inform A3 but must not change protections, merge or mark a failure as PASS.

## Returned evidence (end of mission)

`mission_id`, `start_n`, `target_n`, `actual_n`, `attempted`, `accepted_checkpoints`, exact SHAs, per-step
action moniker, test and metric numerator/denominator, time and proof digest, first material blocker, next
linked action, explicit admission boundary. Missing external data is reported UNKNOWN.

## Machine-readable stub

```json
{
  "schema": "g3a.kickoff/v0-proposal",
  "mission_id": "G3A-HUB-JADE-N9-20261116",
  "status": "PROPOSAL_NOT_LAUNCHED",
  "start_n": 0,
  "target_n": 3,
  "actual_n": null,
  "expected_head_sha": {"hub_master": null, "hub_1154": null, "hub_1155": null},
  "expected_head_sha_note": "resolve full 40-char SHAs at launch; verifier rejects mismatch",
  "gates": ["A1", "A2", "A3"],
  "dispatch_authority": "NONE",
  "merge_authority": "NONE"
}
```

## Open items before launch

1. Owner confirms the mission and supplies the budgets and exact expected SHAs.
2. Verify the stub fields against `ABACUS/scripts/g3a_bounded_mission.py` input format before wiring (not done here).
3. SEM-07 (ABACUS namespaced wave/pulse/3P*/G3A crosswalk) is still OPEN in the P0007 doc; this record does not close it.
