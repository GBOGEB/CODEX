# Artifact Product + Recursive Lineage Bridge

Status: Wave B reusable governance bridge

## Purpose

CODEX provides reusable contracts and validators for outward artifact behaviour. The bridge is deliberately broader than style SSOT validation: it governs functional Excel/HTML behaviour, recursive lineage, interaction QA and stale propagation that ABACUS can consume.

## Product-first lanes

The reusable lanes are:

1. Excel navigation and input/output interfaces;
2. Excel scenario/configuration interaction;
3. HTML navigation and scenario interaction;
4. HTML export/deep-link behaviour;
5. recursive lineage graph and stale propagation;
6. semantic crosswalk across Excel/HTML/PPTX/PDF/Markdown/evidence;
7. rendered readability/style behaviour;
8. browser and workbook QA receipts.

Presence of a palette, schema or manifest alone is not sufficient evidence of product readiness.

## Recursive lineage contract

Each artifact node should expose:
- `semantic_id` or node ID;
- producer/build-step ID;
- direct upstream IDs;
- direct downstream IDs where materialized;
- release/build/scenario ID;
- source commit;
- semantic hash;
- artifact hash when applicable;
- theme/style version;
- QA receipt IDs;
- freshness state.

Validators should compute transitive dependants so that a changed upstream node marks all affected descendants stale.

Expected states:
- `FRESH` — all bound upstream lineage matches current release;
- `STALE` — at least one governed upstream dependency changed;
- `UNBOUND` — lineage cannot be resolved;
- `DEFERRED` — intentionally not rebuilt, with reason;
- `FAILED_QA` — generated but not releasable.

## Excel functional contract

Reusable validation should check, where declared by the workbook contract:
- navigation/landing sheet exists;
- major sheets publish purpose + input/output descriptors;
- input cells/ranges are identified, unit-bound and validated;
- scenario/configuration selectors expose allowed values;
- output tables/cards have semantic IDs;
- baseline/scenario comparison is available where configured;
- reset-to-baseline behaviour is documented or testable;
- print/export surfaces are declared;
- evidence/source hyperlinks or semantic crosswalk references resolve;
- inputs, calculations and outputs have distinguishable rendered states.

Workbook readiness is a behaviour score, not a count of SSOT keys.

## HTML functional contract

Reusable browser validation should test declared capabilities:
- navigation and deep links;
- bounded input controls;
- scenario/configuration change propagation;
- compare-to-baseline;
- filters/search;
- reset;
- JSON/CSV export state;
- filtered-table export;
- artifact links;
- lineage/evidence drawer or equivalent;
- visible release/build/freshness state;
- responsive readability;
- no console errors;
- no unintended horizontal overflow.

The browser receipt should state which capabilities were actually exercised, not merely that Playwright ran.

## Cross-artifact semantic crosswalk

Use durable semantic IDs to join outward products:

```text
model/output semantic ID
  -> Excel table/cell/range
  -> HTML card/chart/row
  -> PPTX/PDF/Markdown claim
  -> evidence/source mapping
```

Location-only identifiers such as `Sheet1!G42` or page 17 may be recorded but are not sufficient as the primary lineage key.

## Style as functionality

Reusable style controls should validate rendered semantics:
- clear hierarchy;
- input/output distinction;
- evidence-class distinction;
- pass/watch/fail/deferred/stale states;
- readable tables at target density;
- unit labeling;
- accessible contrast;
- consistent chart title/legend/axis conventions.

Theme tokens are supporting implementation data. They are not the acceptance objective.

## Functional coverage metrics

Report at least:
- major sheets with purpose/I-O blocks / total major sheets;
- governed user inputs with validation + units / total governed inputs;
- decision outputs with semantic IDs / total decision outputs;
- HTML controls exercised by browser QA / declared controls;
- cross-artifact claims linked by semantic ID / declared claims;
- stale-propagation cases detected / injected cases;
- render/readability checks passed / checks run;
- recursive lineage depth and number of resolved nodes/edges.

## DMAIC

- **Define:** user decision/interaction and release boundary.
- **Measure:** functional coverage and lineage resolution.
- **Analyse:** non-credit-bearing PCA on interaction debt, lineage gaps, render debt, scenario-I/O gaps and test coverage.
- **Improve:** prioritize behaviour and traceability fixes before metadata expansion.
- **Control:** require repeated functional/browser/workbook receipts and stale-propagation tests across releases.

## BT ordering for product controls

1. broken/missing decision interaction;
2. broken scenario input/output/compare/export;
3. broken recursive lineage/stale propagation;
4. missing semantic crosswalk;
5. readability/style defects affecting use;
6. metadata-only completeness.

## Repo split

- **ABACUS:** outward Excel/HTML product design, dashboard/navigation, scenario I/O and release-facing crosswalks.
- **CODEX:** reusable schemas/validators/fixtures and cheap CI checks for product behaviour and lineage.
- **cryoplant-project:** controlled project-specific evidence bindings and engineering dispositions.

No parent tooling result promotes child engineering evidence without governed child disposition.

## Credit boundary

Product/readability/lineage maturity remains tooling maturity. It grants no DOW/KEB/PCA/BT/Table-10/Safety/compliance/engineering maturity or project-completion credit.
