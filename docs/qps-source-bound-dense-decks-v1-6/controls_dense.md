# QPS Controls — Dense Source-Bound Canonical Candidate v1.6

**Deck ID:** `QPS-CONTROLS-DENSE-v1.6`  
**Authority:** source-bound curation; candidate I/O and control statements remain typed  
**Primary source:** `QPS_Control_Core_TOPIC - Copy.pptx`  
**Cross-check source:** `QPS_naming_control_0304.pptx`

---

## CTRL-00 — Title / navigation / ownership

### Purpose

Create one dense QPS control-system deck that owns:

- QPS:CIS architecture;
- subsystem control hierarchy;
- MIT / MIS / MCS signal-path philosophy;
- WCS.HCC modular control structure;
- tender-level WCS and QINFRA candidate I/O;
- readiness / inhibit roll-up;
- control-development progression through L1/L2/FAT/SAT;
- explicit interface to Utilities without duplicating Utilities-owned LOOP engineering.

### Source ownership context

The control-core deck assigns:

| Stakeholder | Source-derived control role |
|---|---|
| ATS | QSYS / overall cryogenic ownership |
| QPS | QPS integration and WCS ownership context |
| CIS | MCS, MIT, MIS services / co-development |
| NFS | UBMS / BEPS / ODH / evacuation / fire / access-control facility context |
| Contractor | QPS:CIS detailed implementation |
| User | QPLANT / QCELL operational role |

### Source binding

- `QPS_Control_Core_TOPIC - Copy.pptx`, slides 2–3.

---

## CTRL-01 — WCS.HCC modular control + lifecycle progression

### Source hierarchy

```text
QSYS
  │
  ▼
QPS:CIS
  │
  ▼
WCS.HCC:CIS
  ├── HP1:CIS
  ├── HP2:CIS
  ├── HP3:CIS
  └── HP4:CIS
```

The source treats HP1–HP4 as repeated modular instances under the WCS.HCC control layer. Tender structure should therefore define the repeated signal/functional contract once and expand exact points during detailed design/FAT.

### Development progression

| Phase | Source activity | v1.6 control intent |
|---|---|---|
| L1 | functional design | architecture, modes, interfaces, cause/effect principles |
| L2 | detailed logic | complete PLC sequences, alarms, I/O, permissives, detailed cause/effect |
| FAT | factory test / logic | verify implemented logic, package interfaces, simulated I/O |
| SAT | system acceptance / functional demonstration | demonstrate integrated behaviour at site |

The broader QPS lifecycle model may contain additional LCM phases; this slide preserves the source deck's local control-development sequence rather than replacing it.

### Source binding

- `QPS_Control_Core_TOPIC - Copy.pptx`, slides 4–6.

---

## CTRL-02 — QPS:CIS hierarchy, locations and terminal points

### Hierarchy view

```text
                         || MCS.Broker_QSYS
                         || normal data / broker
QPS:CIS
  |
  +-- QPLANT
  |     +-- {WCS_CCB.CR}  WCS:CIS
  |     +-- {QRB_AUB.CB}  QRB:CIS
  |
  +-- QINFRA
        +-- {WSH_CCB.SA}  WSH:CIS
        +-- {QSN_CCB.SA}  QSN:CIS
        +-- {QRB_AUB.CB}  TP for QI.S / QI.U / QI.W

QCELL:CS / QVE:CS  <--> MIS <--> QPS:CIS
                    interlocks only
```

### Meaning of `||`

- interface marker;
- terminal point;
- scope boundary;
- use at room / branch handover only;
- **do not use as an internal hierarchy separator**.

### Location grammar retained

- `{WCS_CCB.CR}` — WCS compressor room;
- `{QRB_AUB.CB}` — QRB cold-box location and warm-line terminal-point context;
- `{WSH_CCB.SA}` — WSH storage area;
- `{QSN_CCB.SA}` — QSN storage area.

### Source binding

- `QPS_Control_Core_TOPIC - Copy.pptx`, slides 7–10 and 23.
- cross-check: `QPS_naming_control_0304.pptx`, slides 21–24 and 34–36.

---

## CTRL-03 — Tree versus links / support-system control interfaces

### Structural rule

```text
TREE                                 LINKS
QPS:CIS                              WCS || HV03
├── QPLANT                           WCS || HV06
│   ├── WCS:CIS                      WCS || PAB12
│   └── QRB:CIS                      WCS || QJB10
└── QINFRA                           WCS.HCC || ES02 / LOOP
    ├── WSH:CIS                      QRB || HV02 / PAB12
    └── QSN:CIS                      QPS:CIS || MCS / MIS / MIT / UBMS
```

A utility or facility service is not made a child SBS item merely because its state affects operation. The tree preserves ownership/decomposition; links preserve support, utility, signal and interface relations.

### Source support-system map

The control source explicitly associates QPS/QPLANT/WCS/QRB with support systems including HV02, HV03, HV06, PAB12, PGB20, QJB10, QJB30, ES02 and LOOP.

### Source binding

- `QPS_Control_Core_TOPIC - Copy.pptx`, slides 11–12.

---

## CTRL-04 — Tender-level WCS + QINFRA I/O candidate matrices

### WCS candidate I/O — refined source version

| Signal group | Path | Tender intent | Classification state |
|---|---|---|---|
| Cooling-water available | MIS / MIT | permissive + monitor | candidate; exact trip class to freeze |
| HVAC healthy / airflow proven | MIS | startup permissive | candidate; mode/occupancy consequence to freeze |
| Instrument air available | MIS / MIT | support utility status | candidate |
| Compressor run / ready / fault | MIT | HMI + sequence | candidate |
| Pressure / temperature / flow | MIT | process telemetry | candidate |
| Common trip / ESD chain | MIS | hard interlock | candidate structure |
| Alarm summary to MCS | Broker / MIT | remote operator view | candidate |
| HP1–HP4 modular points | repeated package structure | expansion in L2 / FAT | pattern candidate |

### QINFRA warm-line candidate I/O

| Signal group | Path | Tender intent | Classification state |
|---|---|---|---|
| S/U/W header P-T at TP | MIT | monitoring | candidate |
| Isolation-valve command + feedback | MCS_QINFRA_3lines | line control | candidate |
| branch high/low pressure alarm | MIT / MCS | operations alarm | candidate |
| ODH / support non-trip alarms | MIS slow | warning / permissive | candidate; safety ownership to freeze |
| hard trip / safe isolation | MIS | interlock | candidate |
| accessory status | MCS_QINFRA_3lines | ancillary control | candidate |
| operator summary to MCS | Broker / MIT | remote overview | candidate |

### Boundary

The source itself states that exact point count, marshalling and PLC allocation remain to be frozen in the detailed I/O list. v1.6 therefore labels this material `TENDER_CANDIDATE`, not final I/O authority.

### Source binding

- `QPS_Control_Core_TOPIC - Copy.pptx`, slides 13–16 and 24.

---

## CTRL-05 — MIT / MIS / MCS signal-path philosophy

### Normal information path

```text
Field / package PLC
       │
       ▼
     QPS:CIS
       │
      MIT
       │
       ▼
 MCS broker / backbone
       │
       ├── operator / supervisory views
       └── support-system / UBMS information exchange
```

Normal process information includes temperature, pressure, flow, status, alarms and HMI mirror information.

### Interlock path

```text
QCELL:CS / QVE:CS
       │
      MIS
hardwired / governed interlock path
       │
       ▼
     QPS:CIS
```

The source states that QPS:CIS interlocks are routed via MIS and separates this from MIT/MCS normal data exchange.

### Broker wording control

Source material contains phrases such as direct OPC UA / PROFINET and a preferred broker path during 2 K operation. These should remain `SOURCE_WORDING_REQUIRES_PROTOCOL_FREEZE` until the contractual control-interface requirement fixes the exact transport, redundancy and autonomy obligations.

### Loss-of-MCS principle

The knowledge-system baseline treats QPLANT/QPS local control as autonomous on MCS loss. Any curated slide must clearly separate:

- process-control autonomy;
- supervisory/data-exchange loss;
- safety-interlock path;
- stale/last-value HMI behaviour.

### Source binding

- `QPS_Control_Core_TOPIC - Copy.pptx`, slides 17–23.
- cross-check: `QPS_naming_control_0304.pptx`, slides 35–36.

---

## CTRL-06 — Readiness / inhibition hierarchy

### Source concept

Readiness is built bottom-up through child/subsystem control systems. A parent is not `READY` simply because communication exists; the required underlying functional conditions for the active mode must be satisfied.

```text
lowest equipment / LCC
       ↓
skid / package
       ↓
subsystem
       ↓
WCS or QRB
       ↓
QPLANT / QINFRA
       ↓
QPS:CIS readiness / operating permission
```

### State grammar for curation

| State | Meaning |
|---|---|
| GREEN | no active inhibit for the requested mode; operation permitted |
| AMBER | degraded / conditional / restricted mode |
| RED | active inhibit / blocked requested mode |
| GREY | unavailable / not applicable / option suppressed for this mode |

### Source examples requiring mode-aware logic

- PVPS is required for 2 K operation but not necessarily for other modes.
- HCC availability depends on required compressor count/load.
- ORS / dryer / gas analysis are presented as generally required in the WCS source logic.
- turbine-string degradation may be load-dependent and remains source-TBD.
- HV03/HV02 failure may affect occupancy/heat-management rather than always cause the same fast QPS trip.
- HV06 is described in source material as desirable/available but not necessarily operation-blocking by design.

### Control rule

Do not convert these examples into a single universal Boolean. The canonical implementation should use a mode-conditioned inhibit matrix.

---

## CTRL-07 — Signal classification matrix

A source-bound control deck needs a classification layer so visual readiness does not blur distinct control consequences.

| Class | Definition | Typical examples |
|---|---|---|
| MONITOR | information only | P/T/F, package status |
| WARNING | operator attention; no direct inhibit | non-trip support alarms |
| SLOW_INTERLOCK / PERMISSIVE | controlled inhibit / permissive logic | cooling/HVAC/IA availability where mode requires |
| HARD_TRIP | immediate safe-state path via MIS | ESD/common trip/safe isolation |
| MODE_INHIBIT | prevents one requested operating mode only | PVPS unavailable for 2 K |
| OCCUPANCY_CONSTRAINT | affects personnel access/room operation rather than cryogenic process directly | HVAC/ODH combination |

### Required next artefact

A cause/effect + mode/inhibit matrix shall bind every candidate I/O row to one of these classes before CONTROL promotion.

---

## CTRL-08 — Utilities / LOOP reference boundary

The Controls deck does **not** own the thermal/electrical LOOP calculation.

Controls owns only the consequences:

```text
Utilities-defined LOOP state
        │
        ├── utility-availability inputs
        ├── degraded-mode selection
        ├── mode inhibit / permissives
        ├── operator alarm state
        ├── occupancy constraints
        └── controlled shutdown / recovery sequencing
```

Physical cooling capacity, residual heat, backup-power capacity, ODH/ventilation assumptions and recovery time stay canonical in the Utilities deck and their engineering source documents.

---

## CTRL-09 — L1/L2/FAT/SAT verification path

### Evidence progression

```text
L1 functional architecture
  ↓
mode definitions + interface classes + top-level cause/effect
  ↓
L2 detailed control design
  ↓
I/O list + sequence logic + detailed cause/effect + alarm/interlock matrix
  ↓
FAT
  ↓
logic, simulation, package communication, fail-state demonstrations
  ↓
SAT
  ↓
site-integrated functional demonstration and interface acceptance
```

### Minimum trace

Every safety-critical or operation-critical signal should resolve through:

`source requirement → interface/ICD → I/O ID → logic/cause-effect → FAT case → SAT case → acceptance evidence`

No visual `GREEN` state is acceptance evidence by itself.

---

## CTRL-10 — Validation / source-lineage register

| ID | Open control question | Closure evidence | State |
|---|---|---|---|
| CVAL-01 | Freeze exact MIT/MIS/MCS boundaries and protocols. | ICD + control architecture + cybersecurity/network design | OPEN |
| CVAL-02 | Freeze exact WCS and QINFRA I/O point count/marshalling. | detailed I/O list | OPEN |
| CVAL-03 | Bind every support-system status to monitor/warning/permissive/trip/mode/occupancy class. | cause/effect + mode matrix | OPEN |
| CVAL-04 | Confirm QPS autonomous behaviour and HMI handling on MCS/broker loss. | control philosophy + FAT/SAT test | OPEN |
| CVAL-05 | Freeze QINFRA S/U/W accessory control authority and terminal-point signals. | ICD/P&ID/control architecture | OPEN |
| CVAL-06 | Resolve turbine-string degraded-mode source TBD. | process capacity / operating mode analysis | OPEN |
| CVAL-07 | Confirm HV03/HV02/HV06 mode-specific consequences. | Utilities + ODH/safety + controls cause/effect | OPEN |
| CVAL-08 | Expand HP1–HP4 repeated tender pattern to detailed L2/FAT implementation. | vendor/contractor control design | OPEN |

### Source-control state

`SOURCE_FILENAME_AND_SLIDE_BOUND_DIGEST_PENDING`

### Promotion path

```text
source PPTX + slide number
       ↓
source SHA256 + stable slide render
       ↓
extracted text / tables / diagrams
       ↓
curated object mapping
       ↓
KEEP / MERGE / DROP / REFERENCE record
       ↓
content-loss review
       ↓
controls reviewer acceptance
```
