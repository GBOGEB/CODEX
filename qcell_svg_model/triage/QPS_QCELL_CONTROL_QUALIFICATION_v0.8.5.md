# QPS × QCELL CONTROL qualification v0.8.5

## Purpose

This is the bounded CONTROL qualification gate for the QCELL SVG/HTML visual-engineering lane after P1A/P1B/P1C convergence.

Authority remains `VISUAL_SEMANTIC_ONLY`. CONTROL here means the visual lane is reproducible, semantically guarded, and fit for governed downstream consumption. It does **not** grant engineering, SAT, OPEX, negotiation, compliance, or release authority.

## Pre-qualification evidence

- C2 visual control: `CLOSED_PASS_EXACT_HEAD_REPEAT`.
- C3 proof and repeat: `CLOSED_PASS_EXACT_HEAD_REPEAT`.
- deterministic YAML + templates + renderer -> SVG/HTML path proven on distinct exact heads.
- generator-bound `qps-qcell-visual-receipt/1.0` implemented.
- large teaching arrows OFF by default.
- dotted endpoint guides ON by default.
- pressure overlay deferred/OFF.
- one canonical MAIN drawing retained.

## Final C1 review finding discovered before CONTROL

The final P1A Codex review found one additional concrete thermal-map defect after earlier repairs:

- the boundary labelled `300 K warm membrane` still used the full 77→300 K gradient rather than the authoritative single 300 K endpoint colour.

CONTROL is therefore correctly fail-closed until that defect is repaired and repeated.

## Repair in this qualification pulse

1. The 300 K membrane now uses the authoritative SSOT `T300` colour (`#cc0000`).
2. The 77→300 K gradient remains only in the legend where a range is intended.
3. The visual-control checker now explicitly rejects `stroke="url(#warm300)"` for the nominal 300 K membrane and requires the solid 300 K colour.
4. The checker no longer parses SVG through `xml.etree.ElementTree`; layer/group checks are performed with bounded static-text predicates, eliminating the code-scanning XML parser warning.
5. The checker shebang/import-order findings are removed.

## CONTROL qualification predicates

CONTROL may be recorded only if the exact qualification head satisfies all of the following:

- [ ] visual-control CI PASS on exact head;
- [ ] deterministic-render CI PASS on exact head;
- [ ] generated SVG/HTML equal tracked canonical artifacts;
- [ ] security/code-scanning has no new blocking finding in the qualification delta;
- [ ] Codex review finds no new concrete thermal/visual-semantic regression;
- [ ] C1 MAIN convergence can be formally closed;
- [ ] Local visual DoV can be recorded PASS;
- [ ] authority remains `VISUAL_SEMANTIC_ONLY`.

## Explicit exclusions

The following remain outside this CONTROL gate and are not blockers:

- BD-006 pressure diagnostic overlay;
- BD-007 hosted HTML / GitHub Pages;
- transient cooldown/warmup physics;
- engineering acceptance of cryogenic design values.

## Current disposition

`CONTROL_QUALIFICATION = PENDING_EXACT_HEAD_EVIDENCE`

`LOCAL_VISUAL_DOV = PENDING_QUALIFICATION_HEAD`

`GLOBAL_PROJECT_DOV = WITHHELD`
