# CODEX W10 MYCELIUM first-red and annotated-green source-owner receiver

**Date:** 18 October 2026. **GitHub receiver:** `GBOGEB/CODEX` on original `main` .

**Canonical handover:** [Mission Control CP.CLOSE W10 PR #726](https://github.com/GBOGEB/pipeline-automation-hub/pull/726) · canonical source input `mission-control/v2/handoff/closeout/intakes/CP-W10-MYCELIUM-FEDERATION-20261018.json` and method [`CP_HANDOFF_RESUME_V1.json`](https://github.com/GBOGEB/pipeline-automation-hub/blob/master/mission-control/v2/handoff/CP_HANDOFF_RESUME_V1.json). This file is **an additive read-only receiver**, not a second producer, V2 seal, root register, workflow dispatcher or engineering acceptance.

**Owner:** CODEX semantic MYCELIUM, N7 test and OSV/security owner. The repository's `main` was observed at the time of branch creation as `0b313c2ec3fc48f1c6cf6920e7a5636c161746c3`; refresh on the next session. The restricted cryoplant-project main SHA and data are intentionally excluded from this public receiver.

**Required owner-scope continuation**

1. CODEX #1097 N7 diagnostics merged; exact historical PR source `d3f55c168a65bd287873d461bcc26ddaccbfbfaf`, run `39146937220`/attempt 1/job `117732579114`: 23/23 unit tests, 495/512 statements, 114/136 branches. This is diagnostic, not accepted root closure.
2. OSV on historical post-merge main `d4174eb97a48ee5bc0d463640a305dd63059fa12`, run `39147772131`/job `117735007297`, FAILED six known findings in four packages (three medium and three low). Newer main must be independently rescanned; preserve fail-on-vuln and avoid attributing causality to #1097 without comparison.
3. Receiver of MissionControl #725 annotated-GREEN: successful check-run with >=1 annotation is NOT failure-level annotation; severity UNKNOWN on denied 401/403/404/429 and never assumed zero.
4. No CODEX-authenticated launch, QPS engineering owner acceptance, cross-repo coverage or security waiver is granted by this handover.
5. CODEX governance #977/#1037 requires eligible review, effective checks, RED canary and latest main terminal qualification.

**Historical W9 source-bound baseline (not this repository's latest CI):** hub [run 39147416140](https://github.com/GBOGEB/pipeline-automation-hub/actions/runs/39147416140), 3 native jobs PASS, 77 tests per Python, 434/516 statements, 122/144 branches in hub-only modules; CODEX history 661/661 runs (261 successful, 400 failed), 160 detailed samples (100 red,60 green), canonical 19 CPQ items, 0 new accepted roots. Independent archive ZIP receipt: artifact `12143768528`, 135187 bytes, SHA256 `262131fdaba860aef00e28dd158bb4f8eed7b1da00c36010a69a0f83b584ba12` with 10 CRC-clean/7 manifest-verified generated files. **Do not credit these metrics to this receiver repository.**

**Read / resume:** `CP.RESUME(source="GITHUB_FIRST",mode="VERIFY_REFRESH_EXECUTE",horizon="G3P:N_TO_N_PLUS_3")`. First refresh this repository's exact source head, canonical hub PR #726 and its CP.CLOSE native manifest, W10 child #725, latest CODEX OSV and ABACUS gates; then request an authorized source-owned return with explicit UNKNOWNs. No committed nine-artifact source exists until native generator/byte parity and approved PR are verified.

**P0 stops:** Missing effective branch-required statuses or eligible independent review; OSV/Safety RED; unavailable authenticated source; inaccurate cross-repo coverage or private QPS evidence; any attempt to infer causal closure, authority transfer or security waiver.

**Disposition:** `MERGE_ADMISSION=HOLD`, `SECURITY_WAIVER=false`, `QPS_ENGINEERING_ACCEPTANCE=WITHHELD`, `FORMAL_CAUSAL_ROOT_CLOSURES=0`. No original chat export supplied: full verbatim fidelity, global prompt count and worker capacity remain UNKNOWN. See owner [issue](https://github.com/GBOGEB/CODEX/issues/1088).
