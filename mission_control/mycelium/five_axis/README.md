# CODE PURPLE — five-axis growth frontier (source-owned CODEX read-only projection)

This additive CODEX MYCELIUM adapter **does not replace** \`mission_control/mycelium/control_manifest.yaml\`, ABACUS B0 or the existing MIP/DMAIC/SIPOC/BD root ledgers. No executor, network calls, token use, admission authority or QPS engineering truth is created.

## Scope and origin

Frozen readback (18 October 2026): CODEX main \`89f2a12329b2ff3ad395edce3ecb1d87936f1507\`; ABACUS main \`54c8143600ea17dc2e707261e216aceb5ff2adf5\`. The historical B0 cohort was \`9e0200190555736c74295ee74881e3c003e8a35c\`; do not compare its numerators with unmatched current main. Selected source evidence: ABACUS [#1860](https://github.com/GBOGEB/ABACUS/issues/1860), [#2247](https://github.com/GBOGEB/ABACUS/pull/2247), [#2256](https://github.com/GBOGEB/ABACUS/pull/2256), [#2255](https://github.com/GBOGEB/ABACUS/pull/2255), CODEX [#977](https://github.com/GBOGEB/CODEX/issues/977). Source references and typing live in \`W0_FIELD_OBSERVATIONS.json\`.

## Five independent denominators

| Axis | Eligibility | Required proof | Baseline |
| --- | --- | --- | --- |
| Source coverage | Same-scope eligible executable statements **and** branches | source/selection/config/coverage.json and matched deltas | Current main UNKNOWN; historical lines 35,571/52,497, reported against native B0 |
| Adversarial penetration | Unique planned detectable fault/oracle pairs | Native fault trips and non-culling JUnit IDs | Native comparator preflight 4/4; expanded execution 0/4, real penetration UNKNOWN |
| Cross-module integration | Eligible pinned producer/receiver pairs | Both-side exact-run/job/attempt/artifact/hash receipts | ABACUS census 1/1 native success; receiver population UNKNOWN |
| Platform/runner reach | Fixed OS×Python×dependency matrix cells | Terminal native JUnit + coverage + manifest per cell | W29 comparator setup 4/4, complete tests 0/4 |
| Causal defect detection | Deduplicated reproducible first-red fingerprints | Root discriminator, A→B→A, owner-accepted closure | 2 selected log-verified first-red groups, accepted closures UNKNOWN |

These values must **never be combined into a single pass percentage**. A measured 0/4 failed testflight means measured failed cells, not a zero coverage fraction. \`null\` means unmeasured.

## SIPOC

| Supplier | Input | Process | Output | Consumer |
| --- | --- | --- | --- | --- |
| ABACUS B0 | source SHA, same-epoch coverage | Match statement/branch denominator | source coverage receipt | ABACUS owner |
| Test/CI source owners | negative/reverse/mutation expectations + JUnit | Verify effective oracle trips | penetration receipt | review + MIP |
| ABACUS/CODEX/QPS owners | pinned sender+receiver evidence | Verify both sides, no authority leap | edge-coverage receipt | Mycelium federation |
| Actions runners | OS/Python, run/job/attempt, artifact | Four-cell matrix and stable repeats | platform proof | CI owner |
| Security/BD root owners | logs, first-red fingerprint, negative controls | Reproduce/disambiguate/repair/retest | causal candidate and separate closure | authorized owner |

## Ordered executable DAG; reference feedback can cycle

\`\`\`mermaid
flowchart LR
  O[Origin issue / proto problem] --> S[Exact source SHA]
  S --> C[Source and dependency census]
  C --> F{Five independent frontiers}
  F --> T1[Source coverage]
  F --> T2[Adversarial oracles]
  F --> T3[Cross-module handshake]
  F --> T4[OS/Python runner]
  F --> T5[Causal first-red]
  T1 --> J[Exact-run/job/attempt evidence join]
  T2 --> J
  T3 --> J
  T4 --> J
  T5 --> J
  J --> G{Independent required gates}
  G -->|RED / unverified| H[HOLD and root-owned next wave]
  G -->|Terminal + eligible approval| M[Serial owner admission]
  H -.->|Next-wave planning, not an executable back edge| C
\`\`\`

\`TRACES_TO\` means programme lineage, **not** scientifically established causation. \`BLOCKS\` and \`REQUIRES\` project downstream exposure, not automatic eligibility/credit. The executable dependency projection rejects cycles, broken endpoints, untraceable nodes and declared evidence masquerading as native proof.

## Waves and measurable acceptance

- **W1 — Define/measure:** frozen source-root graph, typed edges, five separate signal denominators, reach/pressure projection and SHA256-backed reproducible JSON.
- **W2 — Penetrate:** negative, reverse, forged-proof, cycle, stale-SHA and denominator-culling controls. Add new source-owner-independent test cases; do not edit canonical admission sources.
- **W3 — Reach:** four-native-cell read-only workflow; every cell proves exact checkout, test outcomes and all four hashed receipts. Runner success does not confer cross-repository consumer or governed-merge credit.

For a bounded local build: \`python mission_control/mycelium/five_axis/five_axis.py --input mission_control/mycelium/five_axis/W0_FIELD_OBSERVATIONS.json --out /tmp/five-axis --candidate-head 89f2a12329b2ff3ad395edce3ecb1d87936f1507\`. Add \`--verify-only\` for digest verification. Native workflow supplies exact PR head/run/attempt.

**Convergence:** compare at least three successive serial observations with identical population, configurations and eligible denominators. \`N+1=N\` for a single wave or queued runs proves nothing. Keep sampling until all five axes stabilize or a documented owner blocker/ceiling forces an alternate disjoint frontier. Formal acceptance remains HOLD.
