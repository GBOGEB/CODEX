# QPS review-DMAIC -> CODEX MYCELIUM, non-admitting observation port

**Status:** public code-only candidate; QPS engineering source and receipts remain at their owner. **Owner:** CODEX presentation/projection only. **Authority transfer:** false. **GitHub dispatch, publication and engineering credit:** zero.

## Input/output contract and reuse

- Producer is the existing `GBOGEB/cryoplant-project` QPS review workitems -> `scripts/qps_review_dmaic.py` in draft PR [#2354](https://github.com/GBOGEB/cryoplant-project/pull/2354), not a new QPS parser or scheduler.
- MYCELIUM consumes an **explicitly supplied, externally pinned, sanitised** `qps.review-dmaic-score/1.0` JSON projection. The original restricted PPTX, reviewer comments, vendor PDF and data remain in QPS. No network fetch, copies, issue/PR creation or runner dispatch.
- Python implementation: `mission_control/mycelium/qps_dmaic_bridge.py`. It creates a local scratch `qps-dmaic-bridge-<source-digest>/` with `bridge.json`, a responsive six-panel `index.html` and `SHA256SUMS`. This is a **local review surface**, not an automatic public Pages source.
- An independent payload SHA-256 is required. Caller-supplied QPS and CODEX 40-character head pins are reference context, **not** authenticated repository reads. To claim GitHub provenance, separately bind native artifact/run/job/attempt evidence and fresh GitHub head readback; this adapter cannot do so.
- Output is `codepurple.qps.review-dmaic-bridge.v1`, `admission: DEFER`, `PAY_IT_FORWARD` candidate, `independent_consumer_proof: false`. Never rewrite QPS authority, ledger, golden thread or child disposition.

## Local Windows PowerShell launch (read-only)

Run from your CODEX checkout, with the QPS `score.json` produced by a separately source-pinned QPS run, kept **outside** the public CODEX repository:

```powershell
$Score = 'C:\PRIVATE\QPS\qps-review-dmaic-<digest>\score.json'
$ExpectedScoreSha = (Get-FileHash -Algorithm SHA256 $Score).Hash.ToLowerInvariant()
$CodexHead = (git rev-parse HEAD).Trim()
$QpsHead = '<40-character QPS PR head from independent GitHub readback>'
python mission_control/mycelium/qps_dmaic_bridge.py `
  --score $Score `
  --expected-payload-sha256 $ExpectedScoreSha `
  --expected-qps-head $QpsHead `
  --expected-codex-head $CodexHead `
  --out-dir "$env:TEMP\qps-mycelium-review"
```

Capturing the score hash in the same directory, from the same uncontrolled file, is **not** independent source authentication. Save the expected digest in a separate frozen QPS receipt/approved handover and compare it. The command never runs a QPS script or writes to GitHub.

## Six user-facing panels

Define (source identity and pin), Measure (counts and denominators), Analyse (candidate deltas versus true recurrence), Improve (no invented dispatch), Control (non-compensating native/owner holds), Federation (producer/consumer admission separation). Corporate palette: purple/violet/blush; 2-column grid on desktop, single-column on mobile. No third-party JS, no private source images, no vendor text.

## QA and admission

- Fail closed on schema drift, forged approval/CI, source/payload pin mismatch, malformed JSON, invalid counts, unchanged replay mislabelled as progress, private reviewer fields and output drift/alias.
- `tests/test_qps_dmaic_bridge.py` contains 52 synthetic contract/adversarial cases. Local pilot: 52/52 PASS, statement coverage 160/168 (95.2%), branches 50/52 (96.2%). The existing `missioncontrol-mycelium.yml` should collect and enforce >=52 tests, >=90% statements and >=90% branches on the **actual PR head**.
- Example browser QA must run at 1440x1000, 1280x800, 390x844, with zero page/console errors, zero overflow, six visible sections. A local browser check does not assert recipient Acrobat, engineering agreement or native QPS document fidelity.
- Missing or unverified raw QPS / SLD / P&ID / T-s sources -> `WITHHELD`; the bridge **cannot** prove 12 independent sources or 1x/4x/16x distinct-document throughput.
- QPS #2354 independent human APPROVED review remains a separate, required gate. CODEX bridge CI is not QPS CI; no merge, protection or waiver from this code.

## Follow-on lanes (not automatically executed)

1. QPS-owner private provenance lane: reuse [PUB-R07 #2353](https://github.com/GBOGEB/cryoplant-project/pull/2353) and W383 source pins; identify unique source bytes for SLD, mechanical P&ID and T-s, with an explicit privacy-safe 12-case native/owner readiness matrix. Serial repeats are not distinct-document scaling.
2. CODEX consumer lane: consume an approved, sanitised local QPS score and independently verify the producer receipt/commit/run/attempt. Keep external origin `UNAUTHENTICATED` until verified.
3. Independent review lane: source-owner native Acrobat/layer ON and OFF checks, geometric/vector correctness, remaining electrical RFIs, eligible reviewer approval; PUB-R07 48 OIDs unchanged until owner decision.

**Disposition:** `BRIDGE_CANDIDATE / LOCAL_QA_PASS / PUBLICATION_HOLD / ENGINEERING_HOLD / OWNER_GATE_UNCHANGED`.