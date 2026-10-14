# CODE PURPLE — reusable high-contrast diagram contract

This visual contract follows the existing `docs/code_purple_rex_control.html` language. It is a design reference, not evidence of accepted REX, current telemetry, Crew launch, security waiver, or merge admission.

## Semantic roles and contrast

| Role | Node fill | Border | Text | Meaning |
|---|---|---|---|---|
| Evidence | `#123950` | `#74dcff` | `#f4f7ff` | Observations, source hashes, CI, JUnit and scans |
| Repair | `#123d31` | `#83ebca` | `#f4f7ff` | Bounded disjoint ownership |
| Verification | `#473519` | `#ffe097` | `#fff5df` | Focused, B0, full CI and DoV |
| Blocked | `#4e1c30` | `#ff97ab` | `#fff0f3` | RED or held admission |
| Authority | `#35264f` | `#dcc5ff` | `#fff5ff` | Owner/reviewer/governance decisions |

Keep text AA (contrast >=4.5:1) and large graphical outlines >=3:1. Colors never replace status words. White/purple on similarly valued purple surfaces is prohibited for separate roles.

## Readability controls

1. Render one compact sticky nav for major sections, and a second compact sticky legend across the entire main page, not just one section.
2. Show provenance, exact source identity, and independent authority at least once adjacent to the graph.
3. Provide semantic HTML headings, visible keyboard focus, skip link and reduced-motion support.
4. Keep diagram labels large, with mobile one-column fallback; desktop workflow is directional and repair return edges are explicit.
5. Separate static architecture from live census. A Mermaid preview, generated HTML, queued run or diagram does not establish execution or acceptance.
6. TOP7/14/21 are capacities over an approved ranked inventory, not numbers of runners or repositories.
7. Keep line coverage, branch coverage, diff coverage and repository rollout as separately named, source-bound metrics; unknown remains UNKNOWN.

## Source of truth and tests

- HTML reference: `docs/code_purple_convergence.html`
- Mermaid source: `docs/diagrams/code_purple_convergence.mmd`
- Static regression: `tests/test_code_purple_convergence_accessibility.py`
- Native producer gate: `.github/workflows/code-purple-rex-control.yml`

Use this contract for new CODE PURPLE diagrams. Any separately published dashboard should undergo native browser rendering and mobile sticky-scroll inspection in addition to these static tests.

`security_waiver=false` · `authority_transfer=false` · `formal_credit_delta=0`
