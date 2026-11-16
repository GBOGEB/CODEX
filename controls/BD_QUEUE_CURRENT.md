# CODEX BD Queue — Current

Status date: 2026-11-16  
Repository: `GBOGEB/CODEX`  
Current main at recensus: `b4c0a8a345722b4cecc3f7be67bb21f36f81e79f`  
Open PRs at recensus: **3** (#1317, #1318, #1321; none bound to a queue issue)  
Open issues at recensus: **14**  
State: **2 ACTIVE FIX ITEMS WITHOUT A BOUND REPAIR PR; 11 EXTERNAL / OWNER GATES; 1 PARENT CONTROL**

Recensus method: open issues read from the REST API at the main SHA above; state from each issue's `closure:` label (`active` -> FIX_PR, `external` / `owner-decision` / `needs-evidence` -> EXTERNAL_GATE, `control-surface` -> PARENT_CONTROL); binding = an open PR whose body names the issue. The previous recensus (2026-09-24) listed 4 issues; #319 and #324 have closed since.

## Queue rule

Every open issue must be in exactly one state:

- `FIX_PR`: repository change required and bound to one authoritative repair PR.
- `PROVE`: repair merged; closure waits for exact proof.
- `EXTERNAL_GATE`: repository code is not the first red; retain the exact external/local action and re-entry proof.
- `PARENT_CONTROL`: umbrella/control issue; do not manufacture duplicate implementation debt.

Merge alone is not proof. Hosted/synthetic proof cannot compensate for physical production evidence, and dynamic Pages success cannot compensate for explicit Pages source-mode proof.

## Current open queue

| Rank | Issue | State | Current binding | Re-entry predicate |
|---:|---|---|---|---|
| 1 | #1037 P0 post-merge CODE PURPLE reader | FIX_PR | **unbound**: no open repair PR | one bounded repair PR per first-red; protected admission restored and read back |
| 2 | #1283 P0 global alias convergence (P0007) | FIX_PR | **unbound**: no open repair PR | first additive, source-bound migration PR against the CODEX taxonomy and glossary |
| 3 | #991 CODE PURPLE #990 admission HOLD | EXTERNAL_GATE | owner decision: independent security reviewer | reviewer named and review recorded, then admission re-evaluated |
| 4 | #500 TRIAGE conversion gate | EXTERNAL_GATE | real Windows/local governed evidence-vault production builder is the first red | verified evidence vault + approved builder A/B + retained `ROUNDTRIP_RECEIPT.json` / ZERO_DELTA proof, then CODEX cluster-facing binding |
| 5 | #753 QPS v6 publication lane | EXTERNAL_GATE | owner sets Pages Source = GitHub Actions | source-mode/single-writer proof reruns, then a release-specific deployment receipt is bound |
| 6 | #1199 [U11] Mycelium CI red + federation return path | EXTERNAL_GATE | owner decision on replacing repository_dispatch | decision recorded; the first red is then bound to one repair PR |
| 7 | #977 MissionControl execution promotion | EXTERNAL_GATE | owner decision: authenticated crew dispatch | owner authorises; first dispatch receipt for the first ABACUS merge |
| 8 | #1088 MYCELIUM P-process typed reference | EXTERNAL_GATE | owner decision on qualifying the hub #701 candidate | qualification decision recorded with its source pin |
| 9 | #1200 [U13] Workstation C: free space | EXTERNAL_GATE | needs evidence from the workstation | relief run receipt + free-space guard in place |
| 10 | #1278 [U31] local-only worktree work | EXTERNAL_GATE | owner triage on the workstation | each worktree item pushed, archived or dropped |
| 11 | #1288 [U54] relief toolchain home | EXTERNAL_GATE | owner decision on where the relief tools live | toolchain restored at the decided home |
| 12 | #1286 [U37] Method Atlas v3 residuals | EXTERNAL_GATE | owner decision per residual | each residual started, merged into a wave or closed |
| 13 | #1198 [U7] planned waves that never started | EXTERNAL_GATE | owner decision per wave | each wave started, merged into another or closed |
| 14 | #879 MissionControl owner dispatch control | PARENT_CONTROL | control surface | maintain; do not create duplicate implementation debt |

## Closed local runtime-contract child

### #830 / PR #831 — CONTROL

PR #831 merged at:

`585ce63e8637477673680744139e76ee6d16965f`

Exact PR head:

`b78181f77717d8970ba877a4eda4de6880c82bbd`

Exact-head proof:
- W69 run `36004487563` / job `107649015564` = SUCCESS.
- Workflow Registration Guard `36004488011` = SUCCESS.
- CODEX Zero Delta Preflight `36004486167` = SUCCESS.
- W003 Governance Gate `36004485888` = SUCCESS.

Distinct merged-main readback at the merge SHA confirmed:
- canonical W69 exposes `workflow_call`, `pull_request`, and `workflow_dispatch`;
- registration guard covers W69;
- QPS/W05/W70 historical workflow paths remain but are manual-only delegates to W69;
- no legacy wrapper retains `CreateOfficeReviewCopy` or `Invoke-QpsControlledRoundtrip.ps1` invocation.

#830 is therefore closed CONTROL evidence, not an active queue item.

## Previous proof closure

#811 and #812 remain closed historical CONTROL evidence:

- #811 — Bandit hardened scan/report separation: closed after run `35733656932`.
- #812 — Update Documentation idempotence/policy fallback: closed after run `35734083493`, with no command-substitution error.

## Current disposition

- `FIX_PR = 2` (both unbound: the executable repo-local frontier is #1037 and #1283, and neither has a repair PR)
- `PROVE = 0`
- `EXTERNAL_GATE = 11` (10 owner decisions or owner-held evidence, 1 production-evidence gate)
- `PARENT_CONTROL = 1`
- reverse pressure from the open PR frontier on this queue = **0** (no open PR names a queue issue)

Next re-entry: bind one bounded repair PR to #1037 or #1283. Owner decisions on #991 and #1199 each unlock a FIX_PR.

Do not create a replacement coding wave merely to occupy WIP.

## External gates

### #500 — production zero-delta

Required path remains:

`Windows/local governed evidence vault -> real builder A/B -> retained ROUNDTRIP_RECEIPT.json / ZERO_DELTA proof -> CODEX cluster-facing binding`.

The hosted QPS zero-delta workflows remain synthetic and non-compensating.

### #753 — Pages publication

Required owner action remains:

`Settings -> Pages -> Build and deployment -> Source: GitHub Actions`

Then rerun the unchanged repository ownership/source-mode proof and bind a release-specific Pages deployment receipt.

## Parent controls

### #879

MissionControl owner dispatch control surface. Maintain; findings stay candidate-only until a child issue accepts them.

Closed since the 2026-09-24 recensus: #319 (DMAIC / queue control, completed 2026-11-15) and #324 (QPS KEB coverage umbrella, closed not planned 2026-11-15).

## Next execution order

1. Bind one bounded repair PR to #1037 (P0 CODE PURPLE first-reds) or #1283 (P0 alias convergence): these are the only repo-local FIX items.
2. Owner decisions that unlock repo work: #991 (security reviewer), then #1199 (Mycelium return path).
3. Re-enter #500 only on a real local Windows production receipt.
4. Re-enter #753 only after the owner Pages source setting changes and unchanged proof can run.
5. Workstation and parked-intent gates (#1200, #1278, #1288, #1286, #1198) re-enter on owner action only.

## Non-compensation

- `authority_transfer = false`
- `formal_credit_delta = 0`
- W69 synthetic success does not close #500.
- wrapper consolidation does not grant QPS engineering/compliance/negotiation/release credit.
