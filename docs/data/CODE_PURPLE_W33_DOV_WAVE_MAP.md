# CODE PURPLE W33 — federation DOV, disjoint worker and evidence return map

Status: **READ-ONLY CANDIDATE / MERGE_ADMISSION=HOLD**. This is a source-bound engineering wave map, not a worker launch, owner approval or accepted REX. It extends the [existing central Convergence Map](../code_purple_convergence.html) and [versioned W32 ledger](../data/code_purple_convergence_control_w32.json), not a competing dashboard.

## 1. Roll-up contract — separate denominators, no blended readiness

| DOV / depth | Population and unit | KPI | Acceptance requirement | Last observed |
|---|---|---|---|---|
| Global / 3-repo ordinary queue | GitHub `is:issue` across ABACUS/CODEX/cryoplant-project, PRs excluded | open/closed and 7/21/90-day transitions | Search with incomplete_results=false and recorded query/time; this is **not** deduplicated BD/root count | 106 open / 373 closed, observed 18 Oct; previous subset 105 / 373 |
| ABACUS / canonical main | Same SHA + coverage configuration, statements and branches eligible | (covered statements+branches)/(eligible statements+branches); raw and fixed-population deltas separately | Terminal exact-main B0 + artifact digest + JUnit identity + stable denominator | Last green 35,571/52,497=67.758% at `9e0200190555736c74295ee74881e3c003e8a35c`; latest-main UNKNOWN |
| ABACUS / PR | Current exact head, broad and changed-line *separately* | broad%, changed-line%, no-new-debt | Native coverage tools, changed-source denominator, independent same-head report | 12 Oct baselines broad 36.92% and diff 51%; current UNKNOWN |
| Section / source family | DOCX/XLSX/PPTX/PDF/HTML/HTM; individual faults, branch+statement opportunity | fault-oracle detection and per-family pass/eligible, not case count alone | Reproducible negative/reverse test identity and matched branch instrumentation | W32 native 15/15 PASS in [RED B0 39161409879](https://github.com/GBOGEB/ABACUS/actions/runs/39161409879); coverage delta UNKNOWN |
| Cluster / disjoint first-red | Native run+job+attempt+fingerprint; deduplicate manifestations by root | unique roots open/closed; recurrence; first-red displacement | Source-root discrimination and owner disposition | 2 blockers in W32 B0: NumPy and G3CS skip, closures UNKNOWN |
| Regional / runners | Fixed OS/Python/dependency matrix; executed job IDs not plan count | terminal green/planned cells; queue latency p95; execution p95 | Exact-head native per-cell JUnit+coverage/artifact SHA256 | W32 CI matrix RED; quantified matrix reach by fixed population UNKNOWN |
| Federation / receiving edges | pinned ABACUS→CODEX and QPS domain receipt pairings | paired accepted / eligible directed edges | Both-side authenticated run/job/attempt/artifact/hash + consumer validation | UNKNOWN |
| Governed admission | P0 effective protection, independent eligible approval, security, RED canary | noncompensating PASS/HOLD per gate | Server effective rules and rejected RED canary; serial governed admission | HOLD |

Never subtract 36.85% (11 Oct) from 67.758% (different baselines). Never convert a queued worker, DAB proposal, GitHub comment, ordinary merged PR or visual graph node to an authenticated Crew launch, REX or governed admission.

## 2. Coverage scale opportunities (hypotheses, NOT measured results)

**S1 · Binary-source integrity (ABACUS #2274):** 15 native selected cases PASS across six input suffixes. Next bounded 24–48-case candidate should exercise forged OOXML relationships, corrupt/truncated ZIP and PDF, path replacement, symlink race, parser degradation, hidden-versus-visible HTML, and idempotent canonical output. Require **same-source statement AND branch** before/after reports and no skipped/cut tests. Security-sensitive parser changes require their own source owner and independent review. Target exploratory floor: changed-line ≥80%, but do not import a scope-local percentage into global main coverage.

**S2 · B0 recovery (#2263/#2264/#2276/#2277):** two independent historical failures were NumPy contract pin and unmarked external-ZIP skip. Verify *latest* full main B0 and native ZIP receipt. Distinguish subsequent first-red movement from successful suite recovery; compare attempts as a causal chain, not independent closed roots.

**S3 · W29 temporal testflight (#2265, CODEX #1106):** fix existing comparator path at its source owner, then cover stale SHA, A→B→A, denominator shift, JUnit duplicate identity, timestamp reversal, changed-branch signatures, retry collision and invalid evidence hashes. Four unique native OS/Python cells must reach matched producer receipts; CODEX consumes read-only typed returns.

**S4 · Federation/REX perimeter (CODEX #977):** default-deny local ABACUS executor design with principal/ref/path allowlist, replay/idempotency, concurrent path leases and no remote mutation from CODEX. Before a worker count increases, produce real `run_id/job_id/run_attempt/head_sha`, file-path owner and returned REX digest, and verify consumer acknowledgment. Stage-only transport remains stage-only.

**S5 · Governance/security (ABACUS #1860):** preserve Safety exit-64 enforcement, A10 confidentiality, pending eligible human review, required status contexts and negative RED canary. A dashboard is an observation plane, never an enforcement tier.

## 3. Disjoint dispatch / push-pull-census control

| Stage | Local owner | Input | Append-only proof | Stop/continue condition |
|---|---|---|---|---|
| C0 inventory | ABACUS owner | exact current main & pending PR heads | unique `repo/head/run/attempt` and changed-path census | same-head re-read; no duplicated repairs |
| C1 partition | CODEX advisory | dependency graph / first-red fingerprints | no-overlapping write set, permit continuing read-only lanes | overlap ⇒ serial source owner |
| C2 implement | ABACUS local authorized runner | bounded allowlisted files with exact head | separate PR and commit full SHA | never execute without owner authorization |
| C3 qualify | source owner native CI | four matrix cells and canonical B0/security | JUnit IDs, sha256 receipts, terminal job URLs | nonterminal or RED ⇒ HOLD |
| C4 pull/consume | CODEX observer | source-signed export / immutable artifact | sender+consumer receipt pair and typed edge | unmatched SHA/denominator ⇒ UNKNOWN |
| C5 governance | human owner/admin | independent review, effective required checks, blocked RED canary | formal admission receipt | security waiver/authority transfer forbidden |
| C6 repeat | DMAIC/MIP | N-1/N/N+1 matched axes | slope, repeat variance, root recurrence, cost/proof | 3 consecutive matched flat deltas ⇒ pivot or stop only if target satisfied |

If observed queue nonterminal pressure ≥80%, prefer **one** incremental focused source-owned lane and read-only census. Avoid multiplying full B0 repeats until first-red sources change. This is an advisory rule, not a scheduler enablement.

## 4. Immediate next proof edges

1. Read terminal [CODEX #1109 exact-head W32 QA](https://github.com/GBOGEB/CODEX/actions/runs/39164366118) and repair any browser/ledger first-red before qualifying publication. Its [ordinary merge](https://github.com/GBOGEB/CODEX/pull/1109) at `0653007cf68fe20824beb937329f8b567ff27f35` is not a governed release.
2. Read current ABACUS main canonical B0 and branch protection; require matched refreshed coverage on the latest full SHA. W32 15/15 selected cases are valid but **B0 4,796 PASS / 2 FAIL / 2 SKIP** [on #2274's head](https://github.com/GBOGEB/ABACUS/actions/runs/39161409879).
3. Source-own and reconcile #2263/#2264/#2265/#2266/#2267/#2274 and successors; do not recreate closed/merged PRs for superseded defects. Distinguish normal merge from correctly admitted merge.
4. Only after ABACUS native producer and CODEX paired consumer pass, publish accepted REX and causal-root counters. Until then `root_open=null`, `root_closed=null`, `bd_open=null`, `bd_closed=null`.

Restoration: start [CODEX #977](https://github.com/GBOGEB/CODEX/issues/977) and [ABACUS #1860](https://github.com/GBOGEB/ABACUS/issues/1860), then read exact current HEAD and terminal workflow attempts; do not resume from this frozen note as if it were live authoritative CI.
