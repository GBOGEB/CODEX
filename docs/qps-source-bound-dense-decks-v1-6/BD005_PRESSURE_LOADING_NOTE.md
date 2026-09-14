# V16-BD-005 pressure loading — WCS LOOP transient

**Authority:** engineering pressure test; not design approval, safety acceptance or project DoV.

This pulse does not close BD-005. It converts the generic `transient model missing` blocker into explicit evidence predicates and separates two physically different transient problems.

## 1. Do not conflate the two LOOP transients

### WCS / compressor-room LOOP transient — BD-005 primary lane

Loss of off-site power leaves a source-working scenario with one HP/HCC package on ES02 backup, emergency PCW through PAB12, maintained ventilation/ODH monitoring and restricted occupancy. The working values are approximately 350 kW electrical backup, 350 kW emergency PCW, 17 kW residual heat, a 6 h stabilization/recovery window and a 2 h `OR LOSS` onset statement.

### LINAC / Line-S cryogenic-return transient — adjacent lane

D2.1 and the ABACUS Line-S model concern helium return/release, Line-S pressure accumulation, recovery-compressor capacity and HP acceptance. That evidence cannot be used to justify WCS room temperature, one-HP electrical margin or the 2 h / 6 h room-survival statements by analogy.

## 2. New first-reds exposed

### 17 kW is not yet a validated total room heat load

The WCS cooling IADR material gives the 17 kW number a plausible historical source: a pre-study air/room path per FSD575 at approximately 112 g/s / 72 Hz, with a dual-package example shown as `17 x 2 kW`. Current project SSOT surfaces also retain separate `14 + 17 kW` package air paths and a wider `50-81 kW` room-residual sensitivity. Therefore the LOOP slide's approximately 17 kW cannot yet be treated as the total one-package WCS-room heat input.

### 350 kW diesel does not automatically prove the maximum HP point

The Utilities interface table explicitly allocates 350 kW diesel backup to one HP compressor. Current LKT analytical lineage separately identifies the 72 Hz / approximately 112 g/s package maximum at approximately 357 kW, while approximately 350 kW is also used as a planning/nameplate screen. The exact LOOP frequency, flow and electrical point must therefore be frozen; auxiliaries and start/restart demand must also be allocated before electrical margin is claimed.

### 350 kW emergency PCW is a thermal allocation, not yet a hydraulic proof

The 350 kW emergency PCW allocation is source explicit. The WCS water-cooling IADR provides normal PCW temperature-rise/full-flow context, but the current evidence does not yet freeze the LOOP branch flow, pressure, supply/return temperatures, backup pump/fan state, valve state or electrical demand. The PAB12 P&ID proves the physical interface, not the credited degraded capacity.

### 2 h and 6 h remain temporal claims without a WCS transient derivation

No bound WCS-room model currently defines the physical variable that reaches `OR LOSS` at approximately 2 h. Likewise, the approximately 6 h statement lacks a measurable stabilization criterion and a bound room/equipment thermal inventory. These remain OPEN until a first-law transient with uncertainty derives them.

## 3. Required model boundary

The next executable WCS model shall bind:

- exact one-HP LOOP frequency, helium mass flow and electrical input;
- ES02 rating type, overload duration and backed auxiliary split;
- heat-path split through PCW, RCW/bypass, room and exhaust;
- emergency PAB12 flow, pressure, supply/return temperatures and valve state;
- HV03 LOOP airflow and electrical source;
- WCS room geometry/effective thermal mass, initial state and external condition;
- OEM/package limiting temperatures or justified thermal proxies.

It shall output room/equipment temperature versus time, emergency-PCW margin, the first governing limit, the state at 2 h and 6 h, and a defined stabilization/recovery time. Every non-source-controlled input remains typed with pedigree and uncertainty.

**BD-005 remains OPEN. BD-006 is unchanged. Global/project DoV remains `WITHHELD`.**
