# QSVG-P1C C3 proof-and-repeat closeout — v0.8.4

## Final disposition

`C3_PROOF_AND_REPEAT = CLOSED_PASS_EXACT_HEAD_REPEAT`

Authority remains `VISUAL_SEMANTIC_ONLY`. This evidence cannot grant engineering, SAT, OPEX, negotiation, compliance, or release authority.

## Contract implemented

The P1C evidence chain is:

`YAML SSOT + versioned renderer templates + deterministic renderer + visual-control predicates -> SVG + HTML -> typed receipt`

The canonical typed receipt schema is `qps-qcell-visual-receipt/1.0` and contains:

- producer repository;
- exact producer SHA;
- SSOT schema;
- authority;
- MAIN state;
- collision state;
- render-determinism state;
- SVG normalized hash;
- HTML normalized hash.

Receipt emission occurs only after:

1. exact PR-head checkout and SHA equality assertion;
2. fail-closed visual-control predicates PASS;
3. render A from SSOT PASS;
4. render B from SSOT PASS;
5. normalized A/B equality PASS;
6. equality with tracked canonical SVG/HTML PASS.

## Exact-head evidence A

- subject head: `0572dd36c52217d0b684c8656d88590442087a16`
- deterministic workflow run: `34858353937`
- job: `104023701991`
- result: **PASS**
- typed-receipt emission step: **PASS**
- artifact: `qcell-svg-determinism-0572dd36c52217d0b684c8656d88590442087a16`
- artifact id: `10354360435`
- artifact digest: `sha256:9cac7606061813665eed6747ce424cc5a1b6c203740e37830bea8260ace96417`

## Exact-head evidence B — distinct SHA

- subject head: `b14c21f5e4f4747d8d78369b162ad115da71e37b`
- deterministic workflow run: `34858456381`
- job: `104024058781`
- result: **PASS**
- exact subject checkout: **PASS**
- explicit subject-SHA equality assertion: **PASS**
- fail-closed visual predicates: **PASS**
- deterministic A/B render equality: **PASS**
- tracked-canonical equality: **PASS**
- contracted typed-receipt emission: **PASS**
- artifact: `qcell-svg-determinism-b14c21f5e4f4747d8d78369b162ad115da71e37b`
- artifact id: `10354435334`
- artifact digest: `sha256:947120f6fdb0be9bbb1e15d69618bd2fa9b52d83899899dfab6e30ddeaa5ae69`

The Repeat B commit changed only this lineage/closeout metadata and did not change SSOT, renderer templates, canonical SVG/HTML, collision boxes, or visual semantics.

## BD contraction

- `QSVG-BD-005` -> `CLOSED_PASS_EXACT_HEAD_REPEAT`
- `QSVG-BD-008` -> `CLOSED_TYPED_RECEIPT_GENERATOR_BOUND`
- `QSVG-BD-009` -> remains `CLOSED_PASS_STABLE_ARTIFACT_REPEAT`
- `C3_PROOF_AND_REPEAT` -> `CLOSED_PASS_EXACT_HEAD_REPEAT`

## Remaining decision boundary

C3 is closed locally. `QSVG-BD-010 CONTROL` remains WITHHELD until:

1. C1 MAIN convergence is formally closed by final visual-semantic review; and
2. the Local visual DoV decision is recorded.

Federation DoV remains separate and requires a downstream consumer to accept the typed visual receipt while preserving `VISUAL_SEMANTIC_ONLY` authority.
Global/project DoV remains withheld because visual acceptance is not engineering acceptance.

## Deferred/non-blocking

- BD-006 pressure diagnostic overlay.
- BD-007 hosted HTML.
