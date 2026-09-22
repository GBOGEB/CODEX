# CODEX BD Queue — Current

Status date: 2026-09-22
Repository: `GBOGEB/CODEX`
3PR/MIP implementation baseline: `cbfe949cca3439aef32fd8446f372bdddf6fda73`
Serialization parent after independent KEB concurrency: `b342fba6f73769454875f7793c067654d490da5c`
Wave: full 3PR + MIP, CONTROL proof pending

## Queue rule

Every open issue must be in exactly one state:

- `FIX_PR`: repository change required; issue is bound to one authoritative repair PR.
- `PROVE`: repair is merged; closure waits for an explicit exact-head/default-branch execution receipt.
- `EXTERNAL_GATE`: repository code is not the first red; retain the exact owner/local action and re-entry proof.
- `PARENT_CONTROL`: umbrella/control issue; do not manufacture duplicate implementation debt.

Merge alone is not a proof receipt. Hosted/synthetic proof cannot compensate for physical production evidence, and dynamic Pages success cannot compensate for explicit Pages source-mode proof.

## Active BD queue

| Rank | Issue | State | Current binding | Burn-down predicate |
|---:|---|---|---|---|
| 1 | #811 Bandit scan/report separation | PROVE | PR #819 merged at `471577d52947172900f6bce5db190b8ddc3a8f29`; raw Bandit JSON is authoritative and SARIF conversion/validation/publication are non-compensating | main-bound Bandit run `35733656932` completes SUCCESS; then close with receipt |
| 2 | #812 update-docs idempotence/policy fallback | PROVE | PR #822 merged at `cbfe949cca3439aef32fd8446f372bdddf6fda73`; stable `automation/update-docs` branch and policy fallback landed | main-bound Update Documentation run `35734083493` completes SUCCESS and fallback log contains no command-substitution noise; then close with receipt |
| 3 | #500 TRIAGE conversion gate | EXTERNAL_GATE | physical/local Windows + governed evidence-vault production builder remains first red | real evidence verification + approved builder A/B + retained `ROUNDTRIP_RECEIPT.json` / ZERO_DELTA proof, then CODEX cluster-facing binding |
| 4 | #753 QPS v6 publication lane | EXTERNAL_GATE | last explicit audit still recorded legacy Pages source; dynamic Pages success is non-compensating | owner sets Pages Source = GitHub Actions; rerun unchanged source-mode/single-writer proof; bind release-specific deployment receipt |
| 5 | #324 QPS program-focus KEB coverage | PARENT_CONTROL | cross-domain semantic/evidence umbrella | split implementation only from a concrete current bounded defect; child disposition remains authoritative |
| 6 | #319 DMAIC / capacity / queue control | PARENT_CONTROL | live process-control surface | maintain measured checkpoints; do not turn operational metrics into duplicate implementation debt |

## Full 3PR burn-down executed

### Refresh
- Refresh exposed current-main recurrence rather than relying on the 2026-09-21 snapshot.
- Three bounded repository-local families were selected under #319:
  - #810 zero-job workflow registration debt;
  - #811 Bandit SARIF formatter false-red;
  - #812 update-docs owner-policy/idempotence failure.

### Probe
- Four workflow paths reproduced jobs=0 registration failures before #813.
- Bandit reproduced a scan-complete / SARIF-formatter `IndexError` failure.
- update-docs reproduced successful generation followed by owner-policy PR-creation failure and timestamp branch proliferation.

### Rank
1. P1 registration debt: four zero-job failures per push.
2. P2 Bandit reporting false-red: one false security/tooling red per cohort.
3. P3 docs automation: recurring branch/PR policy noise and branch proliferation.

## MIP outcome

### Modernize
- PR #813: parser-safe controlled workflows + registration recurrence guard.
- PR #815/#819: pinned direct Bandit JSON scan + repository-owned SARIF conversion with optional reporting isolated from scan truth.
- PR #816/#822: deterministic docs metadata + reusable branch + non-failing owner-policy fallback + clean fallback quoting.

### Innovate
- Added `tools/validators/workflow_registration_guard.py` and `.github/workflows/workflow-registration-guard.yml`.
- Added repository-owned `tools/security/bandit_json_to_sarif.py`.
- Separated security scan truth from optional SARIF publication truth.
- Converted docs publishing from timestamp-per-run branches to one reusable `automation/update-docs` branch.

### Perpetuate / control evidence
- Workflow Registration Guard run `35732498866` = SUCCESS on #813 exact head.
- Bandit exact-head functional run `35732318735` = SUCCESS after #815.
- update-docs post-merge run `35732566525` = SUCCESS and preserved owner-policy fallback.
- #819 and #822 are merged hardening fix-forwards; their distinct main-bound proof runs remain queued and therefore keep #811/#812 in PROVE.

## Burned / repaired in this wave

- #810 CLOSED via PR #813, merge `edf2c7b65a39159562a926f4f2572bf3002bf5bb`.
- PR #815 merged `5e2c6a9b3ea61c8d143e605534fd6b4042120679`; #811 reopened after post-merge review found a real non-compensation gap.
- Duplicate PR #818 closed; PR #819 became the sole #811 authority and merged `471577d52947172900f6bce5db190b8ddc3a8f29`.
- PR #816 merged `aff0999d15475966abbeebdf7f70c10575de3be1`; #812 reopened after post-merge logs exposed Bash command-substitution noise.
- PR #822 merged `cbfe949cca3439aef32fd8446f372bdddf6fda73` and removed that fallback quoting defect.
- #500 was accidentally/non-evidentially closed during the wave and was explicitly reopened; control correction is issue comment `5777325617`.

## Newly exposed but not selected for another repair wave

Registration repair converted the former filename-only / jobs=0 ghosts into real runner-executed failures:
- W05 QPS Roundtrip Regeneration Zero-Delta: current first-red is stale harness invocation.
- QPS Roundtrip Zero-Delta: current first-red is stale harness invocation.
- W70 QPS Zero-Delta Diagnostic: same legacy family.

Observed W05/QPS error: `Invoke-QpsControlledRoundtrip.ps1` no longer accepts `-CreateOfficeReviewCopy`; the current workstation harness also requires `EvidenceRoot` and `ReleaseId`.

Canonical hosted synthetic proof already exists as W69 and succeeds. Therefore do not copy the workstation harness back into hosted workflows and do not treat these legacy wrappers as #500 production evidence. If deliberately selected later, the bounded objective is consolidation/retirement onto W69 semantics, not another parallel synthetic implementation.

## Residual branch hygiene

- New recurrence is stopped by the stable `automation/update-docs` branch.
- One pre-fix timestamp branch from this day remains: `auto/update-docs-20260922-125356`.
- Many older timestamp branches also exist.
- The connected GitHub interface used in this session exposes no branch-delete/ref-delete action, so no cleanup is claimed. Treat historical branch cleanup as separate bounded hygiene debt if selected.

## Non-compensation / invariants

- #500 requires physical/local production evidence. W69 or any hosted synthetic workflow cannot close it.
- #753 requires explicit Pages source-mode = workflow evidence. Dynamic/legacy deployment success cannot close it.
- Bandit formatter/converter failure is not a security finding.
- #811 closes on proof of the hardened scan/report separation, not merely on merge.
- #812 closes on proof of the clean policy-fallback path, not merely on merge.
- KEB parent findings remain candidate-only; child disposition remains authoritative.
- No issue-count reduction grants QPS engineering/compliance/negotiation/release/project maturity credit.
- `authority_transfer = false`
- `formal_credit_delta = 0`

## Next execution order

1. Consume run `35733656932`. If SUCCESS, add receipt to #811 and close it. If red, repair only the first material red under #811.
2. Consume run `35734083493`. If SUCCESS and logs contain no command-substitution errors, add receipt to #812 and close it. If red/noisy, repair only #812.
3. Re-census #500 for a genuine physical/local production return.
4. Re-census #753 for explicit Pages source-mode = workflow evidence.
5. Preserve #324/#319 as control surfaces.
6. Only after the two PROVE items clear, consider the legacy W05/W70/QPS hosted synthetic consolidation candidate.

## Stop condition

The current wave is serialized correctly when every open issue is one of:
1. PROVE with an exact pending run,
2. EXTERNAL_GATE with a named external action and unchanged re-entry proof, or
3. PARENT_CONTROL with no unbound concrete defect.

No speculative local implementation is authorized from this queue.
