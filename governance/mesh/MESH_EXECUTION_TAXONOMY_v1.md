# Global Mesh Execution Taxonomy v1

This taxonomy makes the scheduler-facing state model human-readable. Long names are canonical; two-letter keys are compact aliases for transport and dashboards.

| Layer | Key | Canonical name | Short type / what it does | Operational meaning |
|---|---|---|---|---|
| Intent & Control | CG | Current Gate | Target transition | The execution transition the repo/lane is currently trying to achieve. |
| Intent & Control | WD | Work Disposition | Decision state | What to do with the current work/result: proceed, repair, accept, reject, defer, hold. |
| Preconditions | RR | Repository Readiness | Can repo proceed? | Whether repository structure, configuration, tooling and local state are ready for intended execution. |
| Preconditions | DR | Dependency Readiness | Are dependencies ready? | Whether required upstream/downstream/cross-repo dependencies are available and acceptable. |
| Preconditions | SR | Semantic Readiness | Does meaning align? | Whether schemas, contracts, terminology, identifiers and expectations are aligned enough to execute safely. |
| Preconditions | HK | Integration Handshake | Are endpoints connected? | Whether required hooks, bridges, interfaces or exchange endpoints actually connect and agree. |
| Execution | EX | Execution / Runtime | Did it actually run? | Whether executable work ran, including whether >0 meaningful steps executed. |
| Execution | FE | Federation Exchange | Did it cross the boundary? | Whether data, commands, artifacts or receipts propagated across repo/node/lane boundaries. |
| Verification & Evidence | QH | Quality Health | Was the run acceptable? | Whether tests, validators, QA/QC or acceptance checks judge the produced result acceptable. |
| Verification & Evidence | KR | Knowledge Receipt | Can we prove it? | Whether durable, source-bound evidence exists for what ran, against which SHA, with what result. |
| Verification & Evidence | CR | Critical Risk | What can still hurt us? | Material residual risk that remains visible even when execution or validation appears successful. |
| Progress & Blocking | PB | Progress / Burndown | How much remains? | Measures completed versus remaining defined work and whether the backlog is converging. |
| Progress & Blocking | BG | Blocking Gate | What stops transition? | The smallest material condition preventing the target gate from being crossed. |

## Critical distinctions

- **CG = target execution transition**; **BG = thing preventing that transition**.
- **EX = something actually ran**; **QH = whether that run was acceptable**; **KR = whether durable evidence proves that it ran and passed**.
- **RR = local repo readiness**; **DR = readiness of dependencies outside the local repo**.
- **SR = semantic compatibility**; **HK = actual connectivity/handshake**. A contract can align semantically while its runtime integration is still disconnected.
- **FE = successful boundary crossing** is not equivalent to **KR = durable proof**. A result may propagate without a governed receipt.

## Execution flow

```text
CG  Target transition
 |
 +--> RR  Can repo proceed?
 +--> DR  Are dependencies ready?
 +--> SR  Does meaning align?
 +--> HK  Are endpoints connected?
             |
             v
          EX  Did it actually run?
             |
             v
          FE  Did it cross the boundary?
             |
             v
          QH  Was the run acceptable?
             |
             v
          KR  Can we prove it?
             |
             +--> CR  What can still hurt us?
             +--> PB  How much remains?
             +--> WD  What do we do with it?
             +--> BG  What stops the next transition?
                         |
                         +------> next CG
```

## Scheduler boundary

This taxonomy is **not a replacement scheduler**. It is the shared observability/control-state contract consumed by existing orchestration and scheduling engines.

Existing execution mechanisms remain responsible for choosing and dispatching work. The mesh contract standardizes the state they consume and emit. In particular, ABACUS already contains a federated execution scheduler with governance, deployment, runtime, remediation and reconciliation domains, plus recursive coordination and semantic prioritization. CODEX also contains work-conserving scheduler implementations for narrower execution lanes.

Therefore the architecture boundary is:

```text
repo/runtime telemetry
        |
        v
mesh execution taxonomy + status contract
(CG/RR/CR/SR/DR/PB/FE/QH/HK/BG/KR/EX/WD)
        |
        v
existing orchestration / scheduler engines
        |
        v
worker / runner / agent execution
        |
        +---- receipts and state ----> taxonomy/status emitter
```

A dedicated global scheduler should only be introduced if existing orchestrators cannot consume the shared status contract, perform dependency-aware ranking, or coordinate the required mesh-wide concurrency. Until such a gap is demonstrated, the correct implementation is to **adapt the existing orchestrators to consume this contract**, not create another scheduler layer.
