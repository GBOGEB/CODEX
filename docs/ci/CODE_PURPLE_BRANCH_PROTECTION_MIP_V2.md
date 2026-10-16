# CODE PURPLE branch protection MIP V2 — owner-side execution
Status: PROPOSED / NO ADMIN WRITES / NO ADMISSION CREDIT.
Source: CODEX #1042. This adds evidence verification to the original read-only classifier, not an alternate ruleset SSOT.

## First improvement: mandatory checks
Capture the live repository default branch exact SHA, branch protected field, active detailed rulesets (including required_status_checks context and integration_id), PR head SHA, REST check-runs/check suites and workflow definitions on the same PR head. Translate each workflow to an explicit read-only entry: job_contexts, events, pr_target_branches, path_filters, job_conditional. All absent or ambiguous event triggers and skipped producers are UNKNOWN / NOT PROVEN. Path-filtered workflows cannot be universally required on every PR unless a separate unconditional aggregate producer guarantees the context.

Generate a JSON snapshot with schema `code-purple.protection-evidence.v2`, then:
`python scripts/code_purple_ruleset_evidence_v2.py --snapshot observed.json --output receipt.json`.
The script never fetches or changes GitHub and cannot validate the honesty of a supplied snapshot. Archive API URLs, observation UTC, response digests, SHAs and all identities alongside the snapshot. A same-name context from a wrong app is not a PASS. Unrelated / previously successful SHA checks are not PASS. Green skipped jobs never establish real test execution. This V2 conservative contract treats skipped as NOT PROVEN.

## Second improvement: genuine negative admission
1. First have an authorized owner configure an ACTIVE ruleset on CODEX main (or on another explicitly chosen target) with at least one required, guaranteed-to-run check context, and verify the new ruleset readback. Until then, STOP: the target has no enforceable negative probe.
2. Use a temporary non-draft PR targeting the protected branch. Isolate its changes to an innocuous non-executable probe file. Do NOT alter the production check or weaken any security controls.
3. Trigger the legitimate required check with a deliberately failing bounded regression OR withhold its required producer through a separately approved *test* workflow; capture check-run conclusion, exact SHA, app ID, and GitHub merge box's exact rule-specific blocking reason. Prefer a failing check; missing check proof can be ambiguous.
4. Capture a server-side ruleset readback and REST PR mergeable / mergeable_state at the same exact head, plus the native GitHub merge-blocking UI receipt. If review, merge conflicts, draft status or other independent gates could alone block the PR, the test is inconclusive. A failed GitHub check and a blocked UI without rule-specific evidence is not proof of causal enforcement.
5. Record independently reviewed screenshots or full trusted API response with a separately substantiated `blocking_reason="required_status_checks"` and `blocking_reason_source="LIVE_GITHUB_READBACK"` only when that *specific reason* is genuinely visible. These optional fields are derived evidence annotations, not native GitHub REST properties; never fabricate them merely to make the V2 test pass. Run the read-only V2 classifier on the collected snapshot.
6. Keep the test PR unmerged. After the probe, restore the test context normally, close the temporary PR if no longer needed and retain immutable evidence. No force-push, branch deletion, destructive test or bypass. If any required status check becomes missing across normal PRs, stop and investigate instead of weakening policy.

## Acceptance thresholds
- Per-context expected GitHub integration ID, exact SHA, completed non-skipped job, and unconditional applicable PR workflow must agree.
- Required status ruleset active and effective: separate from check execution and separate from branch protected flag.
- Negative test: non-draft PR, exact match, unsatisfied required check, independently captured *check-specific* GitHub refusal, no competing explanation.
- Technical output may be PASS while governed admission remains HOLD pending independent review and operating policy.
- Owner security/administration action is separate. This PR must not merge automatically or grant a waiver.
