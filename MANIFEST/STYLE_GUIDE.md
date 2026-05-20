# A6 Renderer Style Guide

This guide defines how renderer specifications should be written for deterministic implementation and linting.

## Language

- Use normative keywords: **MUST**, **MUST NOT**, **SHOULD**, **MAY**.
- Avoid ambiguous terms such as "better", "cleaner", or "nice looking".
- State measurable thresholds where possible.

## Theming

- Specify semantic color behavior per theme, not inversion behavior.
- Include explicit dark and light examples for warnings and status cards.
- Any contrast requirement must include numeric WCAG targets.

## Determinism

- Contracts must identify canonical inputs and generated outputs.
- Rendering instructions must be reproducible from the same inputs.
- Font requirements must include fallback stacks and availability rules.

## Traceability

- Every governance rule should be traceable to `RENDER_RULES.md`.
- Changelog updates should describe specification/governance changes unless executable behavior shipped in the same PR.
