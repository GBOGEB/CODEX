# AHT check-control repair / MIP — 2026-09-15

Role: canonical contract and PR-head renderer. Contract owner: CODEX; DOW statistics owner: ABACUS; final QPS disposition owner: cryoplant.

## Define and measure
Reproduced on ABACUS base 779fac31791592d1fa34bf40aab47a537d7a1c1d: zero successful and zero failed checks returned SUPPORTED with failure_rate=0.0. The method also had no cancellation, timeout, pending or review parameters. This is a governance/validator false-green defect, not evidence of product correctness.

## Analyse and improve
Repair -> no-results evaluation -> false SUPPORTED observed -> shared fail-closed contract + real AHT integration + child consumer -> adversarial local retest -> scoped result only; hosted and downstream Control remain open.

The fixed threshold is the existing default of 1 blocking completed result. failure, cancelled, timed_out, action_required, startup_failure and stale count toward it. A higher notification threshold never authorizes a green result with residual blockers. queued/in_progress/waiting/requested/pending stay separate. Skipped, neutral, unknown and unobserved reviews cannot clear a gate. No denominator produces null rates, not zero.

Status meanings: THRESHOLD_BREACHED alerts; HOLD retains blockers below threshold; PENDING waits; UNKNOWN lacks complete proof; CHECKS_CLEAR covers observed checks only. None grants release acceptance. CI run/check counts are DERIVED from SOURCE-SUPPORTED GitHub observations, not an AHT bootstrap significance claim. Excel remains numerical SSOT; controlled engineering 70/90 and negotiation 0/20 are historical baselines only and receive zero credit from this wave.

## MIP
- Modernize: replace the false-green decision and stale W104 approach with the current AHT bridge and versioned consumer contract.
- Innovate: test the bounded hypothesis that explicit unknown/pending states and external SHA/hash bindings reject false clearance; use adversarial fixtures, not statistical PCA claims.
- Perpetuate: DEFER until exact-head hosted tests, child disposition and two distinct execution instances/fresh-head repeat are observed. Local test success is not PERPETUATED.

## PR-head use
scripts/render_aht_pr_head.py validates snapshot repository, externally expected full head SHA, canonical JSON SHA256 and one-hour freshness before replacing only the marked top-of-body statistics block. Publish the resulting body using the normal PR update action; refresh and compare the live PR head immediately before publishing. Never substitute old W104 head metrics for the new PR head.

The publisher is an explicit review/monitor operation, not a new autonomous write workflow. No workflow permissions are widened. Existing AHT.py naming resolves here to the real ABACUS aht_statistics_bridge.py, not a newly invented duplicate AHT module.

## Local reproduction
python -m unittest discover -s tests -p 'test_qps_aht_control.py' -v
