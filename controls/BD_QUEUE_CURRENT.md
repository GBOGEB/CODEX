# CODEX BD Queue — Current

Status date: 2026-09-24  
Repository: `GBOGEB/CODEX`  
Current main at recensus: `15970251cf9a484dfbe56118bd730808bfe7bb27`  
Open PRs at recensus: **1**  
Open issues at recensus: **5**  
State: **ONE BOUNDED FIX_PR + EXTERNAL/CONTROL FRONTIER**

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
| 1 | #830 legacy hosted QPS wrapper retirement | FIX_PR | PR #831; current wrappers contain stale controlled-roundtrip invocation while W69 is canonical hosted synthetic lane | exact-head W69 SUCCESS + registration/preflight/governance checks; merge; distinct main-bound W69/guard readback; then close #830 |
| 2 | #500 TRIAGE conversion gate | EXTERNAL_GATE | real Windows/local governed evidence-vault production builder is the first red | verified evidence vault + approved builder A/B + retained `ROUNDTRIP_RECEIPT.json` / ZERO_DELTA proof, then CODEX cluster-facing binding |
| 3 | #753 QPS v6 publication lane | EXTERNAL_GATE | repository single-writer code proof is established; owner setting remains outside repo code | owner sets Pages Source = GitHub Actions, unchanged source-mode/single-writer proof reruns, then bind release-specific deployment receipt |
| 4 | #324 QPS program-focus KEB coverage | PARENT_CONTROL | cross-domain semantic/evidence umbrella | split only from a concrete current bounded semantic/schema defect returned by a child |
| 5 | #319 DMAIC / capacity / queue control | PARENT_CONTROL | live process-control surface | maintain measured checkpoints; do not turn operational metrics into duplicate implementation debt |

## Current bounded repair

### #830 / PR #831 — retire stale hosted wrappers behind W69

The registration repair exposed runtime contract drift in:
- `.github/workflows/qps-roundtrip-zero-delta.yml`
- `.github/workflows/w05-qps-roundtrip-regeneration-zero-delta.yml`
- `.github/workflows/w70-qps-zero-delta-diagnostic.yml`

Those historical wrappers still call the workstation-oriented `Invoke-QpsControlledRoundtrip.ps1` contract with removed `-CreateOfficeReviewCopy` and without mandatory `EvidenceRoot` / `ReleaseId`.

PR #831 keeps the historical paths but converts them to manual-only compatibility delegates to canonical hosted synthetic W69, makes W69 reusable via `workflow_call`, and extends the registration guard to W69.

Do not use this repair to claim #500 production parity.

## Previous proof closure

#811 and #812 remain closed historical CONTROL evidence:

- #811 — Bandit hardened scan/report separation: closed after run `35733656932`.
- #812 — Update Documentation idempotence/policy fallback: closed after run `35734083493`, with no command-substitution error.

## Current disposition

- `FIX_PR = 1`
- `PROVE = 0`
- `EXTERNAL_GATE = 2`
- `PARENT_CONTROL = 2`
- current executable repo-local frontier = **#830 / PR #831 only**

Do not open a competing wrapper repair or duplicate W69.

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

### #324
Keep KEB semantic/evidence coverage here. Parent findings stay candidate-only until child ACCEPT/REJECT/DEFER.

### #319
Keep DMAIC/queue/process telemetry here. #830 is the single bounded child admitted from the runtime contract drift exposed after registration repair.

## Next execution order

1. Consume PR #831 exact-head W69, registration guard, preflight and governance checks.
2. Repair only the first material #830 red if any.
3. Merge only after the bounded exact-head predicates are green.
4. Require distinct main-bound readback before closing #830.
5. Re-enter #500 only on a real local Windows production receipt.
6. Re-enter #753 only after the owner Pages source setting changes and unchanged proof can run.
7. Preserve #324/#319 as controls.

## Non-compensation

- `authority_transfer = false`
- `formal_credit_delta = 0`
- W69 synthetic success does not close #500.
- wrapper consolidation does not grant QPS engineering/compliance/negotiation/release credit.
