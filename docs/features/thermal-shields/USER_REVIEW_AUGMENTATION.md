# Thermal Shields Feature - User Review Augmentation

Source augmentation: user review supplied after full-deck scaffold.

## Review directives retained as requirements

1. High-value photographs are primary evidence assets, not OCR substitutes.
2. HTML primary visual shall render a square 1:1 high-fidelity image card with `object-fit: contain`; no crop of engineering evidence.
3. Low-quality OCR may be inserted only as a secondary preview/inlay/sidecar.
4. CAD drawings shall be rearranged where needed using explicit alignment rules: align top, align middle, align center, equal caption baselines.
5. Slide headings and subheadings shall have exact and equal placement across cards and slide sections.
6. Cards shall use separate title bands when card title differs from the source heading.
7. Bullet-box patterns may begin with a card heading followed by bullets; the heading itself shall not be treated as a bullet.
8. Hidden diagram borders and clean visual blending remain required.
9. Wave planning shall be updated after every five implementation waves.
10. Content shall be pruned only when it reduces duplication or OCR noise; engineering evidence and decision logic shall be kept.

## Prune / keep rules

| Class | Action | Reason |
|---|---|---|
| Photographs of actual implementation | Keep at highest fidelity | Evidence asset |
| CAD drawings / simulations | Keep, align into cards | Technical basis |
| OCR text | Prune to preview / collapsible sidecar | Avoid false authority |
| Duplicate slide text | Consolidate in manifest | Reduce noise |
| Titles / subtitles | Normalize placement, do not alter meaning | Deck consistency |
| Labels / arrows / callouts | Keep as overlay model | Engineering traceability |

## Wave replanning delta

- Wave 01-05 remain foundation waves: scaffold, HQ images, OCR sidecar, alignment engine, heading lock.
- Wave 06 becomes the first consolidation wave after the five-wave checkpoint.
- Wave 07-10 now emphasize card semantics, CAD alignment, vector overlays, and responsive square rendering.
- Wave 11 becomes the second replan checkpoint, including user review reconciliation and content pruning audit.
- Wave 12-15 map repository integration: ABACUS governance, CODEX automation, fidelity testing, acceptance baseline.

## Repository roles

### CODEX / GBC

- Owns GitHub-facing automation contract.
- Owns parser and renderer CLI stubs.
- Owns style schema and reusable deck-to-HTML implementation pattern.

### ABACUS / GBA

- Owns governance evidence, RTM, maturity scoring, DMAIC trace, and dashboards.
- Owns feature documentation as part of the cryogenic engineering analysis system.

## Next wave directive

Proceed with Wave 06 as a consolidation checkpoint before adding more rendering complexity. Wave 06 shall verify repository paths, style contract, wave plan, image-fidelity policy, and acceptance gates in both CODEX and ABACUS.
