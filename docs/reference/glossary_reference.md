# HBHS-EP / CODEX / ABACUS Glossary Reference

## Hosted Operational Terminology Runtime

This reference provides a canonical quick-reference terminology layer for:

- CODEX
- ABACUS
- BRIDGE
- HBHS-EP
- MCP
- BASIC operational language

---

# Architecture

| Term | Definition |
|---|---|
| SSOT | Single Source of Truth. Canonical structured representation from which outputs are deterministically generated. |
| topology | Structural interaction map of repositories, waves, runtime systems, telemetry, and governance layers. |
| federation | Operationally synchronized specialized repositories exchanging telemetry, lineage, and runtime contracts. |
| bridge | Cross-repository continuity layer enabling telemetry, contracts, deployment lineage, and survivability exchange. |
| covariance | Nonlinear operational influence between waves, systems, repositories, telemetry, or governance structures. |
| lineage | Traceable historical and dependency path of artifacts, waves, decisions, telemetry, and outputs. |

---

# Governance

| Term | Definition |
|---|---|
| survivability | Long-term operational continuity under entropy, deployment drift, personnel rotation, and runtime evolution. |
| rebuildability | Ability to reconstruct runtime and operational state from canonical artifacts and repositories. |
| entropy | Accumulated operational disorder, drift, fragmentation, or deployment instability. |
| recursive_overgrowth | Excessive recursive sophistication exceeding operational usability or survivability value. |
| bounded_recursion | Recursive growth constrained by evidence, survivability, and operational utility. |

---

# Telemetry

| Term | Definition |
|---|---|
| telemetry | Runtime signals, metrics, convergence data, and operational measurements emitted by systems. |
| observability | Ability to inspect, interpret, and diagnose runtime behavior, convergence, and operational continuity. |
| dashboard_sprawl | Excessive proliferation of dashboards causing operational overload and usability degradation. |
| KPI | Key Performance Indicator used for convergence, survivability, or operational tracking. |

---

# Scientific

| Term | Definition |
|---|---|
| thermo_kernel | Core thermodynamic computational engine handling state properties, transitions, and convergence. |
| backend_compare | Comparative evaluation between computational property engines or scientific backends. |
| low_temperature_realism | Fidelity of thermodynamic behavior near cryogenic and helium-II operational regions. |
| exergy | Maximum useful work obtainable from a thermodynamic system relative to a reference environment. |
| NIST_alignment | Agreement between computational outputs and NIST reference thermodynamic data. |

---

# MCP

| Term | Definition |
|---|---|
| MCP | Model Context Protocol. Structured interoperability layer for models, runtime systems, agents, and external tools. |
| MCP_server | Runtime endpoint exposing governed capabilities, telemetry, or tools through MCP interfaces. |
| MCP_client | Consumer interacting with MCP-governed runtime services. |
| tool_contract | Defined operational interface specifying inputs, outputs, permissions, and telemetry expectations. |
| context_window | Operational memory and reasoning scope available to an active model runtime. |
| agent | Structured autonomous or semi-autonomous orchestration component operating under governance constraints. |

---

# CODE PURPLE Governed Execution Units (G3A taxonomy)

The machine-readable entries are maintained in `docs/reference/glossary.yaml#/glossary/execution_units`. This table is a human-readable projection; it is **not** a second SSOT.

| Moniker | Term | Unit | Acceptance boundary |
| --- | --- | --- | --- |
| `W` | Wave | Outcome-based delivery campaign; may include many pulses and parallel disjoint slices | Objective accepted, or explicit HOLD/DEFER with receipts |
| `P` | Pulse | One DMAIC/MIP observe, diagnose, act, verify and disposition loop | Source-bound result classified; no automatic merge credit |
| `S` | Slice | Independently owned path/task subset | Noncolliding evidence-backed change or diagnostic |
| `I` | Iteration | Generic repetition | Prefer **pulse** for metric-led work |
| `G3A` | Governed Three-Step Advancement | **3 sequential pulses** in a bounded wave, from evidence baseline N toward N+3 | Final evaluated/verified/accepted counts reported separately |
| `G3W` | Governed Three-Wave Delivery | **3 delivery waves** with wave-specific outcomes | Each wave accepted/dispositioned independently |
| `N` | Evidence baseline | Exact repo/head SHA, timestamp, policy/config identity, observed metrics and outstanding gates | A new verified snapshot is required after source drift |

**Rule:** A commit, drafted PR, green focused test, CI run or pulse ledger entry is neither a wave nor an independently admitted outcome. Three planned pulses do not constitute three successful advancements. When an exact-head check is pending, record `HOLD / NOT_YET_VERIFIED`.

**Command convention:** `G3A <mission> --from <pinned N> --goal <measurable DoV> --scope <owners/paths> --budget 3 --stop-on major-blocker --output receipts+metrics+first-red+next`. An operator supplies the starting goal and risk boundaries once; the executor selects each next *admissible* action using the previous pulse's actual evidence. Stop early on head/policy drift, P0/P1 security, missing permissions, owner collision, untrusted evidence or other material blockers. Never auto-approve, merge, waive or change rulesets.

Hierarchy: federation mission `M` → outcome wave `W` → sequential pulse `P` → optional parallel disjoint slice `S` → action `A` → immutable observation/receipt `R`. The receipt must preserve lineage of inputs, steps, SHAs, checks, outcomes and blockers. Canonical process and example are in `docs/automation/G3A_EXECUTION_CONTRACT.md`.

---

# BASIC Operational Verbs

| Verb | Meaning |
|---|---|
| initialize | Establish initial runtime, telemetry, or operational state. |
| normalize | Reduce variability or entropy toward stable governed form. |
| stabilize | Reduce operational volatility and improve survivability. |
| converge | Progress toward validated operational or scientific closure. |
| operationalize | Convert conceptual capability into survivable deployable form. |
| federate | Connect specialized systems through governed runtime exchange. |
| synchronize | Maintain temporal and operational consistency across systems. |
| harden | Improve resilience, survivability, and operational stability. |
| bridge | Connect repositories, runtimes, or telemetry domains. |
| deploy | Publish governed runtime capability into operational use. |
| render | Deterministically generate operational outputs from canonical structured sources. |
| trace | Maintain lineage and operational visibility of changes, telemetry, or artifacts. |
| validate | Confirm correctness against reference evidence or fixtures. |
| recurse | Iteratively elaborate systems or governance structures. |
| simplify | Reduce operational burden while preserving functionality. |
| govern | Apply operational rules, survivability constraints, and continuity enforcement. |

---

# A28 Progression Statistics

## Repository Maturity Progression

```text
CODEX
A10 ████████
A15 ███████████████
A20 ████████████████████
A25 ███████████████████████
A28 ██████████████████████████

ABACUS
A10 ██
A15 ████
A20 ████████
A25 ███████████
A28 █████████████████

BRIDGE
A18 █
A20 ███
A22 ██████
A24 █████████
A28 ███████████████
```

---

## Risk Reduction Trend

```text
Deployment Entropy
A20 ████████████████████
A22 ████████████████
A24 █████████████
A26 █████████
A28 ██████

Operator Overload
A20 ███████████████
A22 █████████████
A24 ████████████
A26 ████████
A28 █████
```

---

## PCA Operational Distribution

```text
PC1 Operational Survivability   ██████████████████████ 42%
PC2 Scientific Validity         ████████████           24%
PC3 Human Operability           █████████              18%
PC4 Recursive Complexity        █████                  10%
Residual Noise                  ██                      6%
```

---

# A28 Wave Summary

## Primary Objective

Reduce risk while increasing repository-specific operational depth.

## CODEX Focus

- hosted runtime stabilization
- dashboard simplification
- deployment continuity
- GitHub Pages survivability
- topology runtime usability

## ABACUS Focus

- scientific realism
- NIST convergence
- low-temperature topology
- backend stabilization
- thermo validation depth

## BRIDGE Focus

- runtime contract stability
- telemetry synchronization
- rollback continuity
- federation simplification
- survivability continuity
