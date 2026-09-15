# QPS × QCELL convergence status v0.8.1

## Contraction result

The visual-engineering backlog is now compressed from a flat list of ten BDs into three active convergence lanes plus one deferred expansion lane.

### Active core

1. **C1 — MAIN convergence**
   - absorbs BD-001 + BD-002
   - canonical MAIN + large-arrow regression
2. **C2 — visual control**
   - absorbs BD-003 + BD-004
   - text collisions + layer state
3. **C3 — proof and repeat**
   - absorbs BD-005 + BD-008 + BD-009
   - deterministic rebuild + typed receipt + distinct-SHA repeat

### Deferred / non-blocking

4. **C4 — expansion**
   - absorbs BD-006 + BD-007
   - pressure diagnostic overlay + hosted HTML

`QSVG-BD-010 CONTROL promotion` remains WITHHELD and depends on C1+C2+C3 closure.

## Why this is the correct contraction

The previous BD list mixed root defects, downstream proof steps, and optional expansion. The contracted topology makes the causal order explicit:

`MAIN geometry/flow convergence → interaction/collision control → deterministic evidence/repeat → optional pressure/hosting expansion`

This prevents pressure/hosting work from consuming effort before the MAIN visual is stable.

## Immediate execution — QSVG-P1A

Build `v0.7.7 canonical MAIN` from the strongest user-edited sheet lessons:

- **Sheet 2:** grouped visual regions and reduced clutter
- **Sheet 3:** small/right-side flow legend treatment
- **Sheet 4:** endpoint-placement lessons
- **Sheet 1:** historical baseline only; do not restore big-arrow dominance

### MAIN invariant

The drawing stays single and layered.

Three regions should read clearly even with all layers visible:

1. **thermal body**
2. **compact flow/header legend**
3. **parasitic loads + annotations**

### Flow rule

- A/B/D/E remain visible.
- Large teaching arrows are OFF by default.
- Dotted endpoint guides are ON by default.
- Stream colours remain temperature-linked.
- The temperature bar remains the de-facto heat map and should be generated from the same value→colour mapping used by masses and streams.

## QSVG-P1B after MAIN

Render three canonical states from the same drawing and SSOT:

1. `THERMAL_ONLY`
2. `THERMAL_PLUS_PARASITICS`
3. `FULL_MAIN`

For each state, record:

- visible layer IDs
- bounding boxes of labels/cards
- collisions/overlaps
- SVG normalized hash
- HTML normalized hash

A major collision is any overlap that obscures an engineering value, stream tag, thermal boundary, or legend label.

## QSVG-P1C proof

Emit a typed receipt:

```text
schema=qps-qcell-visual-receipt/1.0
producer_repo=GBOGEB/CODEX
producer_sha=<exact head>
ssot_schema=<version>
authority=VISUAL_SEMANTIC_ONLY
main_state=ACCEPT|REJECT
collision_state=PASS|REJECT
render_determinism=PASS|REJECT
svg_sha256=<normalized hash>
html_sha256=<normalized hash>
```

Repeat on a distinct SHA without changing the SSOT semantics. CONTROL is considered only if normalized outputs and semantic predicates repeat.

## DoD / DoV ladder

### PR #683 DoD

- triage manifest committed
- authority boundary explicit
- contracted BD register committed
- execution sequence explicit
- no fabricated PASS for G5-G10

### Local visual DoV

Requires:

- C1 closed
- C2 closed
- C3 closed

### Federation DoV

Requires one downstream consumer to accept the typed visual receipt while retaining `VISUAL_SEMANTIC_ONLY` authority.

### Global/project DoV

Remains **WITHHELD**. Visual acceptance is not engineering acceptance.

## Expected burn-down

| Point | Core lanes open | Expected state |
|---|---:|---|
| now | 3 | IMPROVE |
| after P1A | 2 | MAIN frozen |
| after P1B | 1 | visual controls stable |
| after P1C | 0 | CONTROL candidate |

The next actual build target is therefore **QSVG-P1A / v0.7.7 canonical MAIN**.
