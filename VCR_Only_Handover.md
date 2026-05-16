# VCR-Only Extract (Cross-Referenced)
This extract mirrors the full artefact pack but filters for the VCR scope. Section references (e.g., §2.1) map to headings in `Full_VCR_Handover.md`.

## Requirements (see §1)
| Req ID | Class | Requirement | Verification | Deliverables | Source | Full Ref |
| --- | --- | --- | --- | --- | --- | --- |
| RTM.001 | C | All serviceable joints shall be /FS (VCR-compatible); no PTFE or elastomer seals in wetted helium service. | Visual inspection + BOM review | P&IDs<br>Line class sheet | MASTER_PATCH §1-§8 | §1 |
| RTM.002 | C | Each /FS remake shall use a new metal gasket with batch traceability and tamper evidence. | Maintenance checklist | Maintenance log<br>Tamper-seal log | MASTER_PATCH §4 & §8 | §1 |
| RTM.003 | C | /FS orientation shall be panel-female and module-male; deviations logged. | Field inspection | Orientation checklist | MASTER_PATCH §2 | §1 |
| RTM.003b | C | Small pneumatic/solenoid pilots shall be fail-open so loss of motive air does not obstruct manual isolation flow. | Functional test | Valve FAT/SAT records | MASTER_PATCH §8 | §1 |
| RTM.004 | A | Leak acceptance shall meet Addendum Table 6 values using EN 13185 / ISO 20485 helium mass-spectrometer methods. | Helium MS leak test | Leak reports | Addendum Table 6; MASTER_PATCH §3 & §8 | §1 |
| RTM.005 | C | DBB plus eductor purge shall achieve residual air ≤0.05 % before breaking the joint. | Procedure witness | Purge log<br>Analyzer log | MASTER_PATCH §3 | §1 |
| RTM.006 | A | QINFRA.S/QRB.S shall be protected at 1.3 bar(a) with PSV capacity ≥200 g/s @ 300 K routed to WCS.LP recovery. | Sizing calculations + certificates | PSV certification dossier | MASTER_PATCH §6 | §1 |
| RTM.007 | C | Provide BD/PSV populations and setpoints as defined above with certified orifice capacity. | Manifest review + certs | BOM_Master.csv<br>Cert pack | MASTER_PATCH §6 | §1 |
| RTM.008 | C | Implement tamper-evident ties and scan-based remake counting for every /FS connection. | Inspection + system audit | Tamper log<br>Maintenance system report | MASTER_PATCH §4 | §1 |
| RTM.009 | A | Install dual helium analyzers (GAP.WCS and GAP.QRB) measuring H₂O and N₂ with ±1 ppm accuracy and ≤±1 ppm/year drift; maintain calibration certificates. | Calibration verification | Analyzer calibration certificates | Addendum analyzer clause; BOM_Master.csv | §1 |

## Quality Controls (see §2)
### ITP snapshot (see §2.1)
| Step | H/W | Acceptance Criteria | Record | Full Ref |
| --- | --- | --- | --- | --- |
| Face-seal orientation check | W | Panel female / module male confirmed | Checklist | §2.1 |
| DBB purge cycle | H | Residual air ≤0.05% and He loss logged | Log sheet | §2.1 |
| Gasket replacement | W | New metal gasket per batch record | Maintenance log | §2.1 |
| Helium leak test | H | Leakage ≤ Table 6 limit | Leak report | §2.1 |
| Tamper seal installation | W | Seal ID recorded and scanned | Photo + scan log | §2.1 |
| PSV/BD certification | H | Setpoint & orifice capacity validated | Cert dossier | §2.1 |
| Analyzer calibration | W | ±1 ppm accuracy / drift verified | Calibration certificate | §2.1 |

### DBB purge focus (see §2.2)
- Residual air target: <=0.05% before breaking any /FS joint.
- Records: purge log, analyzer ppm, helium loss estimate, gasket batch, tamper seal ID, technicians/supervisors.
- Tooling: Venturi eductor or recovery hose; analyzer proof logged in CIS.

### Helium leak testing focus (see §2.3)
- Method: EN 13185 / ISO 20485 helium MS (sniffer/hood or inboard ports).
- Acceptance: Table 6 leak limits (<=1e-9 mbar·L/s unless specified otherwise).
- Records: Tag, joint type, leak rate, instrument ID, personnel, QA archive link to RTM.004.

## BOM elements (see §3)
| Tag | Area | Description | Qty | Full Ref |
| --- | --- | --- | --- | --- |
| BD.QCELL | QCELL | Bursting disc | 60 | §3 |
| BD.QPLANT.HP | WCS.HP | Bursting disc (HP) | 2 | §3 |
| BD.QPLANT.TS | QRB.D/QRB.E | Bursting disc (thermal shield) | 3 | §3 |
| BD.QPLANT.LP | WCS.LP | Bursting disc (LP auxiliaries) | 0 | §3 |
| PSV.QCELL | QCELL | Safety valve population | 180 | §3 |
| PSV.QPLANT.HP | WCS.HP | Safety valve (HP) | 6 | §3 |
| PSV.QPLANT.TS | QRB.D/QRB.E | Safety valve (thermal shield) | 6 | §3 |
| PSV.QPLANT.LP | WCS.LP | Safety valve (LP header) | 4 | §3 |
| PSV.QPLANT.VB | Various | Vacuum breaker | 4 | §3 |
| PSV.QPLANT.S | QINFRA.S | Safety valve (S-line header) | 4 | §3 |
| VAL.ONOFF | WCS/QRB | On/Off valves | 180 | §3 |
| FSU.GASKET.ALL | ALL | Metal gasket kit | >500 | §3 |
| GAP.WCS | WCS | Gas analyzer panel | 1 | §3 |
| GAP.QRB | QRB | Gas analyzer panel | 1 | §3 |
| EDC.QINFRA | UHP Network | Venturi eductor set | 6 | §3 |
| SOL.FAILOPEN | WCS/QRB | Fail-open pilot solenoids | 60 | §3 |

## Vendor hooks (see §4)
- `/FS` fittings & gaskets: Swagelok, Parker Veriflo, FITOK — EUR 2-15 per gasket; EUR 20-120 per body (finish dependent).
- PSVs: Leser, Herose, Advance Valve — DN25-DN50 cryogenic PSVs EUR 400-1,200.
- Bursting discs: REMBE, OsecoElfab, Fike Europe — discs EUR 250-600; holders EUR 400-900.
- Venturi purge hardware: SMC ZH, Piab piINLINE — EUR 20-150.
- Fail-open pilots: ASCO, Bürkert — EUR 100-550 (three-way NO valves).
- Online He analyzers: Michell, Edgetech/PST — dual-channel packages mid four- to low five-figure EUR.

## ADR/OCD tie-ins (see §§5-6)
- ADR-001 enforces /FS policy, DBB purge discipline, tamper tracking, and PSV/BD populations tied to WCS.LP recovery.
- OCD scenarios: warm start-up (analyzers + PSV readiness), maintenance outage (DBB purge + leak test), emergency depressurization/LOOP (S-line directs 200 g/s @ 300 K to WCS.LP with CIS logging).

# ADDENDUM — Multi-Format Output Triage Logic

Apply this triage model in addition to the baseline VCR-only handover defined in §§1-6 of this document.

The leak-rate dashboard is one engineering topic, but it must generate several outputs with different purpose, audience, and density.

## 1. Output Triage Principle

One source topic shall generate multiple coordinated artefacts:

```text
Same engineering truth
Different audience
Different density
Different format
Same traceability
```

The source of truth remains:

```text
Markdown + YAML + JSON data + Python calculation engine
```

The generated outputs are:

```text
HTML dashboard
Markdown handover
PDF handover
RTM table
JSON/YAML traceability
GitHub Pages static portal
```

Do not let any generated output become an independent source of truth.

---

## 2. Audience / Density Mapping

Create output views for the following audiences:

| Output                   | Audience                      | Density | Purpose                                  |
| ------------------------ | ----------------------------- | ------: | ---------------------------------------- |
| `index.html`             | Technical peer / reviewer     |  Medium | Navigation portal                        |
| `dashboard.html`         | Engineer / decision-maker     |     Low | Interactive visual-first leak-rate dashboard |
| `calculations.html`      | Cryogenic engineer            |    High | Formula proof and worked examples        |
| `handover.md`            | Coding agent / VS Code / Git  |    High | Source-readable handover                 |
| `handover.pdf`           | Formal reviewer / stakeholder |  Medium | Controlled issue pack                    |
| `rtm_traceability.html`  | QA / requirements reviewer    |    High | RTM and source mapping                   |
| `executive_summary.html` | Manager / non-specialist      |     Low | Decision summary and recommendation      |
| `developer_notes.md`     | Codex / future maintainer     |    High | Build logic and extension rules          |

---

## 3. Required View Modes

Implement the HTML shell with these modes:

```text
HTML Preview
Code-like Markdown
PDF / Print Mode
Expand All
Collapse All
Export PDF
```

The HTML should use:

```text
details / summary sections
sticky navigation
print CSS
badges for ACCEPT / REVIEW / RISK / TRACE
```

Use the structure and styling cues listed above as the visual and structural pattern for the HTML output; this extract does not reference a separate in-repo scaffold file.

---

## 4. Engineering Triage Object Types

Every extracted item must be classified into one of:

```text
Decision
Requirement
Assumption
Risk
Action
Interface
Evidence
Generated Artefact
Calculation
Plot
Validation Check
```

Each item shall carry:

```text
id
title
type
source
status
owner
density_level
audience
trace_reference
version_added
```

---

## 5. Status Badges

Use these status labels consistently:

```text
ACCEPT = mature enough for baseline
REVIEW = technically plausible but needs checking
RISK = unresolved, unsafe, contradictory, or assumption-heavy
TRACE = source-linked evidence item
TODO = required implementation work
NEXT = next recommended step
DONE = implemented baseline feature
```

---

## 6. Leak Dashboard Specific Triage

For this project, classify content as follows:

```text
Visual-first:
  dashboard plots
  log-log leak-rate comparison
  valve-class comparison
  cost versus leak-tightness plot
  fleet-size sensitivity

Calculation-first:
  unit conversion
  helium mass-loss equation
  sonic/choked-flow check
  Reynolds number estimate
  pressure and temperature sensitivity
  worked examples

Requirement-first:
  RTM-047 to RTM-051
  leak-rate table
  helium inventory table
  Slide 15 warm-valve concern
  EN 13185 leak-detection anchor

Decision-first:
  where 1e-9 is overkill
  where 1e-8 is justified
  where 1e-4 is acceptable only for valve-seat/internal leakage
  where 1e-3 is rejected boundary case

Reliability-first:
  MTBF
  MTTR
  MDT
  availability
  spare strategy
  critical valve consequence
```

---

## 7. Recursive DMAIC Layer

Apply this recursive loop to each output view:

```text
DEFINE: What is this view for?
MEASURE: What data does it contain?
ANALYZE: What engineering question does it answer?
IMPROVE: How does it improve understanding?
CONTROL: How is it versioned and kept traceable?
```

Each output file shall include a short `DMAIC View Note`.

---

## 8. Idempotency Rule

The build must be idempotent:

```text
same inputs
same assumptions
same code version
same templates
=
same generated outputs
```

Generate a manifest:

```text
OUTPUT_MANIFEST.json
```

Include:

```text
file path
file type
purpose
audience
density
hash
generated timestamp
source inputs
builder version
```

---

## 9. Release Structure

For this repository, place generated artefacts into the existing top-level folders rather than creating a separate `leak_rate_helium_dashboard/` subproject. Use this structure:

```text
CODEX/
├─ docs/
│  ├─ HUMAN.index.html
│  ├─ HUMAN.report.md
│  ├─ HUMAN.version_log.md
│  └─ leak_baseline/
│     └─ index.html
├─ outputs/
│  ├─ html/
│  │  ├─ index.html
│  │  ├─ 01_EXECUTIVE_SUMMARY.html
│  │  ├─ 02_LEAK_RATE_TRANSLATION.html
│  │  ├─ 03_MATHS_PROOF.html
│  │  ├─ 04_PLOTS_AND_VISUAL_EVIDENCE.html
│  │  ├─ 05_VALVE_CLASS_COMPARISON.html
│  │  ├─ 06_ENGINEERING_RATIONALE.html
│  │  ├─ 07_TRACEABILITY_MATRIX.html
│  │  ├─ 08_VERSION_HISTORY.html
│  │  └─ 09_BUILD_AND_RUNTIME_REPORT.html
│  └─ json/
│     └─ calculation_inputs_outputs.json
├─ traceability/
│  └─ TRACEABILITY_MATRIX.md
├─ OUTPUT_MANIFEST.json
├─ VERSION.json
├─ CHANGELOG.md
└─ ERROR_LOG.md
```

---

## 10. Baseline Commit Target

First commit target:

```text
v1.1.0-leak-rate-static-triage-baseline
```

Commit message:

```text
feat: add leak-rate helium dashboard triage baseline
```

Baseline success means:

```text
An engineer can open index.html,
navigate by audience and density,
inspect leak-rate calculations,
view interactive plots,
trace every number to assumptions or RTM anchors,
and understand which valve leak class is justified, excessive, or risky.
```
