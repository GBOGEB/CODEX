# CODE PURPLE - Default-branch governance MIP/DMAIC V1

STATUS: DRAFT / OWNER-ACTION REQUIRED / NO SECURITY WAIVER. The read-only code in this PR cannot edit GitHub settings or authorize a merge. CODEX currently has no repository rulesets; ABACUS has an Active empty ruleset (#24494381), and both main branches last reported protected=false.

## 1. Coherent five-stage engineering model

| Stage | Process | Tools already installed | Acceptance evidence |
|---|---|---|---|
| 0 Governance preconfig | Branch, owner, reviewer, publishing and rule inspection | GitHub rulesets / CODE PURPLE | SHA-bound baseline, UNKNOWN separate |
| 1 Local preflight | Fast fail before PR | ABACUS pre-commit/TestPilot, Ruff | Executed pre-commit receipt |
| 2 Testflight | Behaviour, regression, environments | Pytest, coverage, UBI9, RHEL8/9, Docker | JUnit, covered/eligible, exact SHA |
| 3 Security | Code/dependency risks | Bandit, CodeQL, OSV, Semgrep | Scanner JSON and independent disposition |
| 4 EVERRED repair | Diagnose first-red and root queue | BD/DAB/LDAB, LLDB/DAP | Executed causal/debug evidence and disjoint repair |
| 5 Admission | Security + verified CI + reviewer + protection | GitHub rulesets / human reviewer | Governed merge or HOLD |

MIP selects only the relevant path through the stages. DMAIC measures effect across N to N+1. A tool being configured does not count as executed, and bot comments are findings rather than approvals.

## 2. Portfolio groups

The last owner inventory returned 90 repositories (83 public, seven private), with 11 size-zero candidates. The default branches are main (65), master (23), trunk (1) and dev (1). Target the actual default branch, never blindly main.

G1: critical CODEX, ABACUS and engineering/integration repositories: reviewed PR, eligible non-author approval, last-push approval, stale-review dismissal, resolved comments, no force push or deletion, verified applicable CI.

G2: other active repositories: inventory existing publishing, then apply per-repo protections and only stable relevant test contexts. Never overwrite unrelated existing rules.

G3: empty, archived, forked, experimental, or private-entitlement uncertainties: exception review with owner and resolution, not silent exclusions.

## 3. Required owner administration

CODEX: https://github.com/GBOGEB/CODEX/settings/rules . Create branch ruleset CODE_PURPLE_MAIN_ADMISSION_V1, target default branch, set Active, use the reviewed recipe at governance/code_purple/BRANCH_RULESET_G1_V1.json where supported.

ABACUS: https://github.com/GBOGEB/ABACUS/rules/24494381 . EDIT this ruleset (it was active but had zero rules); do not create a duplicate.

Both: first confirm a real non-author reviewer and any scheduled direct-main publishers, and migrate publishers to PR/artifact routes before imposing review checks. Do not give routine bot/admin bypass. Add mandatory status check contexts only after confirming repeated real PR execution and a non-skipped evidence contract. A skipped check does not prove that a missing producer ran.

Admin changes require repository Administration WRITE capability, which is unavailable in the current read-only GitHub ruleset connector. No rules were changed by this PR.

## 4. Evidence producer and falsification

The script scripts/code_purple_ruleset_contract.py consumes a SHA-bound read-only snapshot JSON and writes a deterministic JSON receipt, without any GitHub network or mutation methods. It differentiates:
- NO_RULESET: create one (CODEX source case).
- ACTIVE_EMPTY_RULESET: update the exact existing ID (ABACUS source case).
- CONFIGURED_NOT_ADMITTED: all three protections present with protected=true; still hold for independent verification.
- PARTIAL_OR_CONFLICTING and CLASSIC_PROTECTION_UNKNOWN: inspect, never blindly overwrite.
- EXCEPTION_REVIEW and UNKNOWN: no false protected credit.

Its test fixture is explicitly SYNTHETIC. Do not use synthetic SHAs to assert live protection. The exact-head workflow runs scoped Ruff, negative unit tests, branch-aware coverage and deterministic two-pass output, with contents:read permissions and no schedule.

## 5. MIP/DMAIC control loop

DEFINE repository/owner/scope, MEASURE main SHA + protected + detailed active rulesets, ANALYZE root category, IMPROVE with reviewed admin action, CONTROL via new live readback and a deliberately noncompliant DRAFT PR that cannot merge. Do not attempt destructive force push or branch deletion probes.

Metrics stay disjoint: repos inventoried, rulesets configured, actual branch protection, eligible reviewer, executed CI, covered/eligible lines and branches, accepted repairs. Compare N to N+1 only with identical scope and measurement units. New workflow activity is not improvement.

NEXT DOV: effective protected=true and operative rules for CODEX/ABACUS, eligible independent reviewer, executed required checks on same SHA and blocked negative merge test; otherwise HOLD.
