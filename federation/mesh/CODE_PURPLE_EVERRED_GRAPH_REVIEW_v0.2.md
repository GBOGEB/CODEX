# CODE PURPLE / EVERRED — monochrome reader and traceability v0.2

Status: **read-only draft visualization**; CODEX GLOB and Mesh Closure Controller remain authoritative. This is not an independent scheduler, release authority, or live CI producer.

## Owner's four-page visual review — corrections

The supplied annotated PDF identifies a too-dense purple graph, no basic line/node legend, insufficient multi-level collapse, missing timestamped census and re-census, weak DMAIC/MIP evidence, missing recursive SIPOC, and unenumerated Mission Control crew roles (Reader, Deep Reader, Scout, Ambulance).

Required publication contract:

1. **Monochrome**: grayscale only; semantic distinctions use labels, shapes and stroke styles, not colors.
2. **Reading legend**: solid arrow (forward), heavy return (first-red repair), dotted return (\`.self\` re-entry), dashed lateral (\`pay_it_forward\`), stop mark (HOLD); rectangle (process), diamond (decision), double border (independent admission).
3. **Progressive disclosure**: overview -> eight lanes -> process/agent/task/receipt detail; full SVG may scroll, never silently shrink to an unreadable thumbnail.
4. **SIPOC / DMAIC / MIP**: each stage identifies supplier/input/process/output/customer. MIP is conditional for structural gap; DMAIC is the measured continuous-improvement wrapper. Neither is inferred executed because its name appears in a node.
5. **Timestamped source-bound census**: UTC \`observed_at\`, repository, full SHA, producer, run, attempt, job, receipt digest and scanner/config identity. N−10 = 11 successive heads, not necessarily 11 comparable metric observations.
6. **Offline re-census**: local JSON may append independently sourced receipts; invalid SHA/schema/unit, contradictory identity or non-finite values shall be rejected. Uploaded bytes alone do not authenticate a session.
7. **Crew is not capacity**: Reader, Deep Reader, Scout, Ambulance, Dispatcher, Repair, CI Proof, Runtime/LDAB, Independent Reviewer and REX Historian are proposed role types; their active count remains UNKNOWN until dispatch/job/capacity proof exists.
8. **Distinct measurement units**: files, contract checks, debugger sessions/steps, ports, findings, covered/eligible lines or branches, worker job completions, accepted repairs and admitted integrations are never totaled as one success KPI.
9. **Two-pass determinism**: identical producer inputs yield byte-identical normalized receipts; 3PR/3P3/W84 recommendations still need actual observed before/after samples and bounded autonomous scope.
10. **Governed release**: native current-head CI, external code/security review, protected main and exact-public-file/readback remain non-compensating requirements.

## Canonical method hierarchy

CODE PURPLE / CODEX global controller -> 3PR refresh/probe/rank -> EVERRED root recovery when repeated CI failure -> MIP only if structural gap -> 3PC only if bounded transaction -> 3P3 only if independent consumer propagation gap -> STOP when no material evidence change. \`3P*\` is selector, not executable gate. Proposed NEVERGREEN is an adversarial false-green guard only.

QPS is a downstream engineering and quality consumer of CODE PURPLE / EVERRED evidence, not a separate orchestration or merge authority. QPS requirement semantics, independent verification and engineering acceptance remain subject to their own non-compensating gates; a reader or census receipt cannot confer QPS approval.

The PDF's pages 1–4 map to (1) evidence verification / crew, (2) CODE PURPLE / DMAIC / MIP, (3) EVERRED / recursive SIPOC and (4) overview-to-collapsed lane/agent montage respectively.

## Source references

- CODEX \`GLOB.yaml\`, \`federation/mesh/MESH_CLOSURE_CONTROLLER_v1.json\`
- \`federation/mesh/CODE_PURPLE_EXECUTION_SEED_20261012.yaml\`
- \`federation/mesh/CODE_PURPLE_EVERRED_CANONICAL_METHODS_v0.1.md\`
- ABACUS issue #1929 and draft PR #1932
- Companion Mermaid: \`CODE_PURPLE_EVERRED_MONOCHROME_FLOW_v0.2.mmd\`

This draft document does not verify the current runtime of CODEX/ABACUS, an active debugger port, or a recovered merge-admission state. No merge or authority transfer is granted.
