# QPS Utilities — Dense Source-Bound Canonical Candidate v1.6

**Deck ID:** `QPS-UTILITIES-DENSE-v1.6`  
**Authority:** source-bound curation; no silent design promotion  
**Primary sources:** `QPS_Suporting_Sytems.pptx`, `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`

---

## UTIL-00 — Title / navigation / status

### Purpose

Create one dense engineering deck for QPS support utilities with explicit ownership of:

- cooling-water demand and interfaces;
- HVAC / room heat extraction;
- RCW / heat recovery;
- electrical and diesel support;
- instrument air / nitrogen support;
- LOOP support-system dependency;
- open assumptions and validation actions.

### Navigation

`Scope → Utility capacity → HCC heat flow → HVAC/PCW/RCW → LOOP → auxiliary utilities → responsibilities → validation → source lineage`

### Source binding

- `QPS_Suporting_Sytems.pptx`, slides 1–4: agenda/style/context.
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`, slides 51–60: later support-system context and canonical-candidate interface data.

---

## UTIL-01 — QPS utility context and ownership

```text
QSYS
  │
  ▼
 QPS
  │
  ├── QPLANT
  │    ├── WCS ──||── HV03 / HV06 / PAB12 / QJB10 / ES02 / LOOP
  │    └── QRB ──||── HV02 / PAB12 / QJB10 / ES02
  │
  └── QINFRA
       ├── WSH
       ├── QSN
       └── S / U / W warm-line branches
```

`||` is an interface / terminal-point / scope-boundary marker, not a hierarchy separator.

### Source role split

| Actor | Source-derived role | v1.6 curation note |
|---|---|---|
| ATS | overall cryogenic/QSYS ownership | system authority context |
| QPS | integration of cooling/support systems | integration owner |
| NFS | HVAC / facility support-system design | room and facility-side interfaces |
| Contractor | detailed engineering, installation, QPS-side distribution from interfaces | exact contractual allocation remains contract/ICD controlled |
| User | operational requirements through QCELL/QVE | demand/interface source |

### Source binding

- `QPS_Suporting_Sytems.pptx`, slides 7–10.
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`, slides 51–52.

---

## UTIL-02 — Facility utility capacity / allocation surface

### Later appendix source table

The later support-system appendix provides the following utility surface. Values are preserved as source statements and are **not silently normalized** against other working slides.

| Utility | Installed / design capacity in source | Source breakdown / allocation | Curation state |
|---|---:|---|---|
| Cooling Water (PCW) | 1300 kW | 1199 kW WCS HP; 57 kW PVPS; 44 kW QRB | `SOURCE_EXPLICIT` |
| Emergency PCW | 350 kW* | dedicated LOOP event; PAB12 backup logic | `SOURCE_EXPLICIT / LOOP_BOUND` |
| Electricity | 1526 kW | 1397 kW WCS; 129 kW QRB | `SOURCE_EXPLICIT` |
| Diesel Backup | 350 kW* | LOOP: 400 V 3-phase for one HP compressor | `SOURCE_EXPLICIT / LOOP_BOUND` |
| HVAC | 124 kW | 114 kW WCS (HV03); 10 kW QRB (HV02) | `SOURCE_EXPLICIT` |
| Heat Recovery | 850 kW | RCW, TP2:HV06 | `SOURCE_EXPLICIT` |
| Instrument Air | 60 m³/h | 10 m³/h WCS; 50 m³/h QRB; PS05.QJB10 | `SOURCE_EXPLICIT` |
| Gaseous Nitrogen | 375 LPM | source also lists 50 LPM WCS and 50 LPM QRB | `SOURCE_EXPLICIT_WITH_UNRESOLVED_ALLOCATION` |

`*` source annotation retained.

### Evidence note

The slide itself points to `NA.AA_BMA003 - Interface List CRYO - ACC NF.xlsx` and SCK CEN/48341616 as the underlying utility-interface reference. v1.6 records that pointer but does not claim the referenced workbook was ingested here.

### Required reconciliation, not automatic correction

- PCW total and WCS-HCC figures differ in precision/definition across working slides (`~1200 kW`, `~1256 kW`, and `1199 kW WCS HP`). Keep all three tied to their source context until the interface list / load basis resolves the definitions.
- HVAC `124 kW` facility capacity is not automatically equivalent to the `~120 kW room heat` working estimate.
- Gaseous-nitrogen total and listed subsystem allocations are not arithmetically complete in the source slide. Preserve as an explicit review item rather than inventing the missing allocation.

### Source binding

- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`, slides 53–54.

---

## UTIL-03 — HCC cooling and heat-flow architecture

### HCC thermal paths retained from the working deck

```text
HP compressor skid ×4
        │
        ├── HX1 ──> PCW / PS01.PAB12
        │           primary compressor-oil cooling
        │
        ├── HX2 ──> RCW / HV06
        │           heat recovery / secondary oil cooling
        │
        ├── HX3 ──> PCW
        │           helium aftercooling
        │
        ├── HX4 ──> room bypass / exhaust-air path
        │
        └── Q5  ──> WCS_CCB.CR room / HV03
                    residual room heat
```

### Working-deck heat figures

| Quantity | Source surface | Status |
|---|---:|---|
| HCC PCW load | ≈1200 kW | working summary |
| HCC PCW alternate displayed figure | ≈1256 kW, with 1199 kW HX1 noted | source surface requiring definition check |
| RCW / heat recovery | ≈850 kW | repeated source value |
| room heat load | ≈120 kW | working equipment/room estimate |

### Interface temperatures / environmental values

| Interface / parameter | Source value | Status |
|---|---:|---|
| room design range | 5–40 °C | source explicit |
| typical design room temperature | ~16 °C | source working value |
| wet-bulb design | 23 °C | source explicit |
| HV06 RCW | 30/55 °C | source explicit |
| PS01.PGB20 chilled water | 7 °C | source explicit; role/diversity still to freeze |
| PS01.PAB12 adiabatic heat sink | 27 °C | source explicit |
| chilled-water sizing expression | load × 1.15 | source design expression |

### WIP kept visible

The source discusses helium sensible cooling to approximately `281–283 K` versus the current `300 K` basis and chilled-water diversity/parallel use. These remain `WIP / VALIDATION_REQUIRED`; they are not promoted to design requirements by this deck.

### Source binding

- `QPS_Suporting_Sytems.pptx`, slides 11–18.
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`, slides 55–60.

---

## UTIL-04 — LOOP operational dependency

### Source-defined scenario chain

```text
Loss of off-site power
        │
        ▼
ES02 diesel / backup envelope
        │
        ├── one HCC / HP compressor support basis
        └── PAB12 fans / pump support
        │
        ▼
Reduced cooling + ventilation condition
        │
        ├── HV03 ventilation maintained / degraded-condition management
        ├── PGB20 availability reduced or unavailable depending facility mode
        ├── ODH monitoring remains active
        └── occupancy/access restrictions apply
        │
        ▼
stabilize / recover / controlled loss-management
```

### Working source values

- 350 kW electrical backup basis for a single HP compressor.
- 350 kW emergency-PCW basis appears in the later utility table.
- approximately 17 kW residual heat is shown in the working LOOP slides.
- approximately 6 h recovery window is shown as a working scenario.
- approximately 2 h onset concern is also shown in working material.

### Governance classification

These values are retained as `SOURCE_WORKING_SCENARIO`. They must not be silently converted into guaranteed autonomy, safety limits, or contractual acceptance criteria without the relevant calculation / requirement / interface evidence.

### Occupancy / ODH distinction

The source ties HVAC loss/degradation to room occupation and ODH rather than treating every HVAC condition as an immediate QPS hard trip. Controls must therefore reference a classified inhibit/permissive matrix rather than assume that every support-system failure is an ESD.

### Source binding

- `QPS_Suporting_Sytems.pptx`, slides 19–21.
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`, slides 53–60 for support capacities and architecture.

---

## UTIL-05 — Support-system interface legend

| ID | Meaning from source | QPS relevance |
|---|---|---|
| HV02 | QRB_AUB.CB room HVAC | QRB room support |
| HV03 | WCS_CCB.CR room HVAC | WCS ventilation / room heat / occupancy |
| HV06 | RCW for HCC oil HX2 | heat recovery |
| PAB12 | PCW / PS01 | primary cooling / emergency support logic |
| PGB20 | chilled water 7 °C, currently associated with HVAC in later appendix | diversity / partial cooling candidate |
| QJB10 | instrument air / PS05 | support utility |
| QJB30 | gaseous nitrogen / PS05 | auxiliary utility |
| ES02 | electrical supply + diesel backup | normal + LOOP support |
| LOOP | WCS.HCC.HP1 support configuration in source legend | operational scenario / dependency |

### Rule

The utility deck owns the physical/support-system meaning. Controls owns the signal classification and inhibit consequence. Do not duplicate one into the other as independent truths.

---

## UTIL-06 — Responsibility and terminal-point control

### Required source hierarchy

- room-level terminal points belong in the ICD / P&ID interface set;
- contractor distribution responsibility begins/ends at the contractually defined handover, not at an inferred diagram edge;
- support systems remain **links** to the QPS hierarchy, not child SBS nodes merely because they provide a utility;
- TP1/requester and TP2/provider terminology must remain aligned with the governing interface documentation before publication.

### Minimum interface attributes to carry forward

```yaml
utility_interface:
  provider_system:
  requester_system:
  terminal_point:
  building_room:
  normal_capacity:
  degraded_capacity:
  LOOP_capacity:
  temperature_or_pressure_basis:
  control_signal_class:
  owner:
  source_document:
  source_slide:
  validation_state:
```

---

## UTIL-07 — Validation / assumption register

| ID | Open question | Required closure evidence | State |
|---|---|---|---|
| UVAL-01 | Is PGB20 7 °C chilled water a baseline QPS cooling path, diversity path, or HVAC-only facility utility? | ICD/P&ID/load balance + owner disposition | OPEN |
| UVAL-02 | Reconcile 1199 / ~1200 / ~1256 kW HCC/PCW figures and definitions. | source load calculation + interface list | OPEN |
| UVAL-03 | Confirm HX1/HX2/HX3 allocation and which values are per-skid vs total. | equipment heat-balance / vendor data | OPEN |
| UVAL-04 | Confirm helium sensible cooling 281–283 K proposal versus 300 K baseline. | process calculation / ADR | OPEN-WIP |
| UVAL-05 | Establish HV03 failure consequence: hard trip, slow inhibit, occupancy constraint, or mode-specific combination. | controls cause/effect + safety/ODH basis | OPEN |
| UVAL-06 | Validate 6 h recovery and ~2 h onset against actual thermal/recovery model. | transient analysis + recovery capacity | OPEN |
| UVAL-07 | Confirm ES02 allocation and single-HCC operating envelope under LOOP. | electrical load list + operating procedure | OPEN |
| UVAL-08 | Resolve gaseous-N2 total versus listed WCS/QRB allocations. | interface list / utility balance | OPEN |
| UVAL-09 | Freeze room-level TP identifiers for each utility. | ICD / P&ID | OPEN |

---

## UTIL-08 — Source-lineage / curation decision

### Current source control level

`SOURCE_FILENAME_AND_SLIDE_BOUND_DIGEST_PENDING`

The deck is now bound to actual source deck names and slide ranges. It is **not yet** cryptographically source-controlled because the PPTX bytes and per-slide render hashes are not stored in this package.

### Promotion conditions

For each promoted slide/object:

```text
source PPTX
  → SHA256
  → exact slide number
  → stable source image/render
  → extracted text/table/diagram inventory
  → source vs curated comparison
  → KEEP / MERGE / DROP / REFERENCE decision
  → reviewer acceptance
```

No material source statement may disappear without an explicit disposition.
