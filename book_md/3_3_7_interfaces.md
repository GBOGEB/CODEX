     1.  []{#_Ref190799769 .anchor}Interfaces

326. or the event of a Loss of Offsite Power (LOOP) to the MINERVA
     facility, the Contractor shall assume the following utilities are
     available after a short interruption (few minutes):

-   Up to 350 kW of back-up power (supplied by a diesel generator)

-   Up to 350 kW of back-up cooling water.

The emergency cooling-water header is hydraulically common with the
normal WCS cooling-water header but may operate at reduced total flow
under emergency conditions.

327. The technical interface details of these backup systems shall be
     co-developed between the Contractor and SCK CEN during the Concept
     Design Phase and fully defined and documented by the Contractor.

-   Electrical Integration (Emergency Diesel Generator Interface)

    a.  The Contractor shall define the voltage level and switchboard
        configuration to which the diesel generator supplies power.

    b.  The Contractor shall specify the feeder cable rating, breaker
        and fuse characteristics, and the applicable earthing scheme in
        accordance with IEC and local electrical standards.

    c.  The Contractor shall confirm whether the emergency bus shall be
        radially fed, or whether it shall require an Automatic Transfer
        Switch with appropriate synchronization capability to
        re-establish supply post-LOOP.

-   Cooling Water Provisioning

    a.  The Contractor shall define the operating pressure, temperature,
        and flow rate of the cooling water available under
        generator-backed emergency operation.

    b.  b\) The Contractor shall propose the tie-in point, including
        line size, and shall confirm whether non-return valves or
        back-pressure controls are required to ensure stable flow during
        switchover.

        In the offer, the Applicant shall provide an enveloping
        preliminary design for the configuration, internal routing, and
        management of abnormal utility supplies (electrical and
        cooling-water) during a Loss of Offsite Power (LOOP) event. This
        shall include:

<!-- -->

-   A functional description of the proposed emergency bus and emergency
    cooling-water header

-   A list of critical loads expected to be maintained under LOOP
    conditions

-   Enveloping assumptions for internal distribution logic, including
    switching, prioritization, and load control schemes

-   Proposed interface boundary conditions with SCK CEN's emergency
    diesel generator and cooling-water header

    1.  []{#_Toc212194856 .anchor}Process Line interface

With reference to Table 11 and Table 12 the following applies:

328. The Contractor shall size and install QRB.A for SHe flows ≥ 50 g
     s⁻¹ at 3 bar(a) and T ≤ 4.5 K, including insulation, supports, and
     P&ID tagging.

329. The Contractor shall size and install QRB.S to accept up to 200 g
     s⁻¹ of warm helium to the VLP header under emergency vent
     conditions, meeting PED over-pressure rules.

330. The Contractor shall route WCS.HP/LP/VLP headers through designated
     wall sleeves, providing expansion compensation and removable spools
     for maintenance access.

331. The contractor shall finalize clear enveloping terminal point
     design and flow conditions (as per ICD) by no later than the end of
     L1 -- Conceptual design (details contained in ICD, and . Current
     sizing/flowrate indicative of scale (\~81 g/s for QDIST.D/E is
     based on dT=20 K of QDIST and QCELL Sizing values in this matrix
     are enveloping and indicative; -

332. Thee supply pressure of QRB.D (at present 13 bar, may be reduced if
     temperature of supply not doable at that pressure.

     Note: The current BSL constitutes a conservative 'available
     pressure' to 'remove' any pressure drop for TS out of the QCELL
     design considerations.

     In the offer the applicant shall clearly state the highest pressure
     of delivery. A pressure drop of 1 bar over the total system (\~300
     m including the TS-payload).

     In the offer the Applicant shall confirm exact mass-flow, pressure,
     and diameter and detail them in the Conceptual Design.

[]{#_Ref210725562 .anchor}Table 11 Interface ID between QRB and QDIST
(cold interfaces)

  ------------------------------------------------------------------------------
  **Line ID** **Purpose / Duty**    **Design   **Operating   **Notes**
                                    Flow       Envelope**    
                                    rate**                   
  ----------- --------------------- ---------- ------------- -------------------
  **QRB.A**   Supply of             50 g s⁻¹   3 bar(a), ≤   Cold helium to
              super-critical He                4.5 K         cryomodules
              (SHE) at 4.5 K to                              
              QCELL distribution                             

  **QRB.B**   2 K return / suction  50 g s⁻¹   ≤ 27 mbar(a), Managed by QRB cold
              from QCELLs                      2 K           compressor

  **QRB.D**   Thermal-shield supply 85 g s⁻¹   \~14 bar(a),  Matches return flow
                                               40 K,         of E

  **QRB.E**   Thermal-shield return 85 g s⁻¹   \~13 bar(a),  Returns to QRB
                                               60 K,         
  ------------------------------------------------------------------------------

  : []{#_Toc212194950 .anchor}Figure 7 Direct Drive

The QPLANT shall interface to the QLM at the cold end of the QRB. The
QPLANT shall contain the final vacuum barrier and the isolation
cryogenic valves.

The QLM contains the following cryogenic lines:

-   "A": Supply of supercritical helium.

-   "B": Return of very low pressure helium.

-   "D": Supply of gaseous helium to the TS.

-   "E": Return of gaseous helium from the TS.

> ![](media/image16.emf){width="4.191666666666666in" height="2.15in"}
>
> []{#_Ref184114765 .anchor}Figure 12 Preliminary arrangement of the
> pipes in the QLM -\
> see Table 12 for details

A preliminary arrangement of the distribution headers in the QDIST is
shown in Figure 12. The preliminary diameters of the pipes are indicated
in Table 12. The final arrangement and pipe diameters shall be defined
by SCK CEN in due time.

+--------------+-------------+-------------+-------------+-------------+
| Line/Pipe    | DN          | External    | Thickness   | Indicative  |
|              |             | diameter    | (mm)        | operating   |
|              | \(mm\)      | (mm)        |             | pressure    |
|              |             |             |             | (bar)       |
+==============+=============+=============+=============+=============+
| A            | 150         | 168.3       | 2.77        | \~0.03      |
+--------------+-------------+-------------+-------------+-------------+
| B            | 25          | 33.4        | 1.65        | ≥ 3         |
+--------------+-------------+-------------+-------------+-------------+
| D            | 40          | 48.26       | 1.65        | \~14        |
+--------------+-------------+-------------+-------------+-------------+
| E            | 40          | 48.26       | 1.65        | \~13        |
+--------------+-------------+-------------+-------------+-------------+
| Thermal      |             | \~350       | 3\*         | \-          |
| shield       |             |             |             |             |
+--------------+-------------+-------------+-------------+-------------+
| Vacuum       |             | \~500       | 4.5         | 10^-6^      |
| jacket       |             |             |             |             |
+--------------+-------------+-------------+-------------+-------------+

333. The welding connection between QRB and QLM shall be done by SCK
     CEN.

334. For the acceptance tests, the Contractor shall provide the
     necessary welded caps on pipes on the QRB side.

  --------------------------------------------------------------------------
  **Line ID**    **Purpose /    **Indicative   **Operating    **Notes**
                 Duty**         Flowrate**     Envelope**     
  -------------- -------------- -------------- -------------- --------------
  **QINFRA.U**   Warm GHe       \~10 g s⁻¹     ≤ 2 bar(a),    Occasional
                 utility /                     300 K          user demands
                 ad-hoc supply                                

  **QINFRA.W**   Warm return    \~5 g s⁻¹      \~1 bar(a),    Coupler (QPLR)
                 from QCELL     (nominal 2     300 K          exhaust
                 couplers to    g/s)                          
                 VLP stage                                    

  **QINFRA.S**   Safety vent to Up to 200 g    300 K          Emergency
                 VLP            s⁻¹ (Loop                     discharge path
                 compression    event)                        
  --------------------------------------------------------------------------

  : []{#_Ref192500058 .anchor}Table 8 Measuring Points for WCS

QINFRA.U and QINFRA.S are not participating in the cryogenic cycle and
nominal cryogenic heat sink demand from the user (QCELL), with QINFRA.W
the only warm line with active refrigeration participation that
represent the liquefaction load (\~4% supply of QRB.A, during nominal 2K
Operational Scenario).

  --------------------------------------------------------------------------------
  **Line ID**    **Purpose/Duty**    **Indicative   **Operating    **Notes**
                                     Flowrate**     Envelope**     
  -------------- ------------------- -------------- -------------- ---------------
  **WCS.HP**     High-pressure       \~350 g s⁻¹    15 bar(a)      Insulated
                 header from warm                                  hard-pipe,
                 compressors to QRB                                traverses
                                                                   Compressor Room
                                                                   → Cold-box Room

  **WCS.LP**     Low-pressure return \~300 g s⁻¹    1.05 bar(a)    Continuous
                 header to warm                                    purge maintains
                 compressors                                       ≥ 1 050 mbar(a)

  **WCS.VLP**    Very-low-pressure   \~50 g s⁻¹)    0.40--0.55     QRB.B Coldbox
                 header VLP                         bar(a)         passthrough +
                 compressors                                       Receives
                                                                   QINFRA.W and
                                                                   QINFRA.S flows
  --------------------------------------------------------------------------------

  : []{#_Ref212186204 .anchor}Figure 8 WSH with Contingent Part 2 (area
  covered in purple dotted line)

In the offer the applicant shall furnish the following deliverables and
form part of the Interface Control Document (ICD) and will form
technical baseline for offer and Conceptual Design Start (L1 in Project
Lifecycle).

i.  Terminal-point definition (quantified with)

ii. 3-D model representation

-   Extract or viewpoint showing each cryoline from first anchor to
    terminal flange

-   Clash-free routing through all penetrations and service corridors

    i.  Refined mass-flow & diameter table

<!-- -->

-   Confirmed operating envelope for every line family (pressure,
    temperature, allowable ΔP)

-   Instrument take-off points (PT, TT, FT) and required maintenance
    clearances (Concept Design Latest)

335. The following warm lines are distributed in the tunnel. The
     interface with the QPLANT will be in the cold box room, around the
     QRB. The final location and pipe requirement shall be defined
     during the design phase with SCK CEN.

-   Warm GHe supply (QINFRA.U): This line supplies helium to the
    cryogenic users (300 K -- 14 bar). It is high pressure (coming from
    the HP of the compression station), the interface pipe diameter is
    DN 25.

-   Safety Valves GHe recovery (QINFRA.S): to avoid loss of helium and
    to reduce anoxia risk, the safety devices shall be collected. The
    diameter of the pipe is DN 150.

-   Coupler return line (QINFRA.W): This line collects the helium gas at
    the outlet of the coupler cooling circuits (300 K and 1.1 bar). It
    shall be connected directly to the LP pressure of warm compressors
    at 1.05 bar. The selected diameter of this line is DN 25.

[]{#_Toc201310423 .anchor}Table 15 Warm lines at room temperature

+--------------------+------+-------------+----------+---------------+
| Pipe               | DN   | External    | T        | Indicative    |
|                    |      | diameter    | hickness | operating     |
|                    | \(   | (mm)        | (mm)     | pressure      |
|                    | mm\) |             |          | (bar)         |
+====================+======+=============+==========+===============+
| Warm GHe supply    | 25   | 33.4        | 1.65     | \~ 14         |
| (U)                |      |             |          |               |
+--------------------+------+-------------+----------+---------------+
| Safety Valves GHe  | 150  | 168.3       | 2.77     | \~ 1.05-1.15  |
| return (S)         |      |             |          |               |
+--------------------+------+-------------+----------+---------------+
| Coupler return     | 25   | 33.4        | 1.65     | ∼ 1.1         |
| line (W)           |      |             |          |               |
+--------------------+------+-------------+----------+---------------+

: []{#_Ref184111599 .anchor}Table 10 Measuring points for gas helium
storages.

336. To cope with a return mass flow rate through the safety valves
     around 100 g/s (case of utility stop for more than 1 hour), the
     diameter line shall be at least DN 150.

In the LINAC tunnel, a line called "vent collector, Line V" could
recover the burst disk of the Cryogenic Cells (QCELL's) to vent helium
outside tunnel in case of major failure. This vent collector is out of
the present scope and does not have any interface with the QPLANT.

1.  []{#_Ref190781343 .anchor}Interfaces with the site

[]{#_Toc212194858 .anchor}Figure 2 gives an overview of the buildings on
site (details are given in \[AD1\]). The QCELLs are in the tunnel (LTU).
The QRB is in the cold box room and the WCS in the compressor room
(CCB). A transport distance of \~65 m applies.

337. The QPLANT shall be designed to meet the site constraints
     (buildings, rooms) given in AD1.

338. The Contractor shall provide the general assembly drawings with
     QPLANT components and 3D models. (\*.step files may be used).

     *In the offer, The Applicant shall quantify the number, size, and
     location of expected roof/wall penetrations*

     1.  Compressor room

339. The compressor room shall house the WCS. (ALL equipment via door
     entrance of 2.5 m)

340. The Contractor shall define the positioning of all equipment in
     this room in agreement with SCK CEN.

341. The compressor units may be installed and grouped on skids.

342. During the conceptual design phase, the Contractor shall evaluate
     the need for a crane in the compressor room and shall provide the
     necessary inputs in Conceptual Design Report (weight and
     dimensions)

343. The access for the installation of the large components could take
     place from the road by removal of the wall dismountable panels. SCK
     will oversee the dismountable panels dismounting and mounting.

     1.  The cold box room

344. The Cold Box Room shall host the Refrigerator Cold Box and
     associated warm panels, the electrical cabinets, the gas analyse
     and pumping (vacuum) system. The height of the ceiling is around
     6.5 meters.

345. During the Conceptual Design phase (LCP1), the Contractor shall
     evaluate the need for crane in the cold box room and shall provide
     the necessary inputs in the deliverable

346. The access for the installation of the large components could take
     place from the road by removal of the wall dismountable panels. SCK
     will oversee the dismountable panels dismounting and mounting.

347. The cold box room shall be connected to the compressor room by the
     different warm lines of the QPLANT.

348. These warm lines of about 60 meters long shall be installed on the
     roof or below the roof close to the ceiling of the buildings
     between compressor room and cold box room.

     *In the offer, the Applicant shall give enveloping coldbox (QRB)
     dimensions, lifting mass and clearances and road loads.*

     1.  Storage Area

349. The gas helium storages and potentially liquid nitrogen storage
     shall be installed in the storage area (next to the compressor
     room. The total helium inventory is detailed in §**Error! Reference
     source not found.** .

350. The positioning of the different storages shall consider the
     possibility of the fluid refilling by trailers.

     1.  Site environmental conditions

351. The following site operating conditions shall be considered for the
     design and operation of the QPLANT and auxiliary equipment:

     Winter design condition

     -   Dry-bulb temperature: −9.1 °C

     -   Relative humidity: 90 %

         Summer design condition

     -   Dry-bulb temperature: 33.4 °C

     -   Relative humidity: 39 %

         Technical-room ambient range

     -   Cold-box room temperature: 5 °C -- 40 °C (Range may be reduced
         for specific cold-box components upon Contractor's request)

     -   Compressor room temperature: 5 °C -- 40 °C

     -   Relative humidity: Not controlled

         Environmental design loads

     -   Wind speed: 49 m s⁻¹ (≈ 176 km h⁻¹), 3 s gust at 25 m height
         (NBN 460)

     -   Rainfall: 54 mm in 1 h (100-year return)

     -   Snow load: 0.50 kN m⁻² (100-year return)

         Site altitude & coordinates

     -   Elevation: 27 m a.s.l.

     -   Location: 51° 13′ 50″ N 5° 05′ 24″ E

         1.  []{#_Toc212194859 .anchor}Interface with support systems
             (utilities)

             1.  Electrical Interface Provisioning

The SCK CEN site shall provide a dedicated 400 V\~, 50 Hz, 3-phase +
Neutral (TN-S) electrical supply at the following interface terminal
points (dedicated to user location inside WCS):

WCS (Warm Compressor Station, CCB Building):

-   HP Compressors (four (4) individual)

-   PVPS (Pressure-Volume Protection System)

-   ORS Electrical Heater

-   Analyzer

-   WCS UPS and Controls

-   QRB (Cold Box Room, AUB Building):

-   Cold compressors CC1, CC2, CC3

-   QRB Controls

-   QRB Varia (auxiliary loads and other installed systems)

352. The Contractor shall provide the complete Low Voltage (LV)
     distribution system for QPLANT, including LV cabinets,
     switchboards, and protection devices.

353. The Contractor shall route, install, and connect all electrical
     cabling, cable trays, and interfaces for the compressor room, cold
     box room, and warm helium storage area 'except for the dedicated
     supply as per above.

354. All electrical design files---including one-line diagrams, layout
     plans, and protection studies---shall be submitted for SCK CEN
     approval. Grounding interfaces shall be connected to SCK
     CEN-provided terminals in each area.

355. The Contractor shall ensure all QPLANT equipment is connected to
     the respective building grounding network, fully compliant with IEC
     60364 and IEC 61000 EMC requirements.

356. All helium piping, water, air lines, and LV cabling entering each
     building shall pass through a single shared feedthrough and be
     connected to equipotential bonding systems to mitigate EMI risks.
     EMC best practices and shall apply.

357. The Contractor shall define the required UPS backup scope and loads
     (HMI, PLCs, network, digital I/O) to ensure full operational
     redundancy in the event of utility loss. SCK CEN will provide
     central UPS backup infrastructure.

358. The Contractor shall submit a risk-based signal classification and
     UPS demand report, listing all sensors, transmitters, and I/O
     requiring backup, subject to SCK CEN approval to finalize UPS
     system dimensioning.

359. Where high voltage (HV) or high-power systems exist, embedded
     controls shall be powered using a dedicated and segregated
     low-voltage AC feed. These feeds shall be galvanically isolated
     from the HV main circuits.

     In the Offer, the Applicant shall:

-   Provide the total and per-building load assessments (normal and peak
    demand) to define final terminal point loads.

-   Submit Single Line Diagram (One Line Diagrams) aligned to the
    'spatial split' (2 rooms in 2 different buildings and terminal point
    logic described above.

-   Include a UPS backup proposal, risk analysis, and critical signal
    identification.

-   Confirm EMC and equipotential bonding compliance per IEC 61000 and
    AD 7.

-   Declare isolation strategies for embedded electronics in HV
    environments and list any required auxiliary supplies.

    1.  Interfaces with the Water-Cooling Loop (NA.PS01.PAB12)

Cooling water (mixture with 40 % of propylene glycol) in the compressor
room for the warm compressors and in the cold box room for rotating
machines (turbines, cold compressors, pumping system) will be provided
by SCK CEN site at one point (supply and return) in each building at the
dedicated technical rooms (Compressor Room and Cold Box Room).

The nominal cooling water temperature supply is 27°C (+/- 2°C) with an
expected temperature difference around 10°C (T~return~-T~supply~). The
Maximum supply temperature is 29 °C.

.

360. The Contractor shall assume a maximum supply of cooling water XXX

361. The Contractor shall provide the cooling water expected consumption
     at the end of the Conceptual Design phase.

362. The Contractor shall distribute the cooling water inside the
     dedicated technical rooms to the different QPLANT users. The scheme
     of the cooling water distribution in the buildings shall be subject
     to approval by SCK CEN.

363. The Contractor shall install all necessary instrumentation and
     additional control elements to measure/control temperature,
     pressure and mass flow rate of the cooling water loops.

364. The Contractor shall provide local drains considering that the
     draining of cooling water is a glycol type waste and therefore
     needs to be connected to the SCK CEN PS03 system.

     1.  Interfaces with Instrument Air System (NA.PS05.XXX)

365. Instrument air in the compressor room and in the cold box room will
     be provided by SCK CEN site at one point in each of the dedicated
     technical rooms. Instrument air pressure will be around 9 bar with
     a dew point lower than -40 °C. For the QPLANT, a maximum of 50
     Nm3/h of compressed air will be available.

366. The Contractor shall provide the compressed air needs at the end of
     the Conceptual Design phase.

367. The Contractor shall distribute the compressed air inside the
     dedicated technical rooms to the different QPLANT users. The scheme
     of the compressed air distribution shall be submitted to SCK CEN's
     approval.

     1.  Interfaces with HVAC (NA.HV02/3)

*In the offer, the Applicant shall specify the terminal point(s) of the
HP compressors to the HVAC system including duct cross-section, air-flow
rate, and interface flange type.*

368. The Contractor shall provide a quantitative analysis of heat
     dissipation to the HVAC system covering:

     a.  Heat load to (compressor and cold box) room and cooling air (in
         kW) for steady state (24 and 30 QCELL) operational and standby
         scenarios.

     b.  Validation of SCK CEN provided exhaust routing to designated
         HVAC intake points during commissioning and acceptance testing.

369. The Contractor shall ensure the integration of the HP compressor
     exhaust ducting with the Compressor Room HVAC system (WCS in CCB).
     SCK CEN provides extraction from defined scope boundary.

370. The total heat dissipated by the WCS to the surrounding air shall
     not exceed 120 kW under any steady-state operating condition
     (including HVAC load from HP compressor ducts).

     In the offer, the Applicant shall furnish interface (HP compressor
     exhaust outlet/terminal points) quantitative data (heat
     dissipation, flow rates, pressure drop, ...)

     In the offer, The Applicant shall quantify flow rates, temperatures
     (maximum, nominal, minimum), and provide outlet dimensions and
     fixed interface and terminal point definition. The allowable
     pressure drop from the compressor to the outside shall be
     specified.

     1.  **Heat recovery**

The heat produced by the LP/HP compressor is to be partially recovered
to supply a heating system only operating when there is a need for hot
water.

371. At least 65 % of the compression power dissipated as heat by the LP
     and HP compressors shall be recoverable via the site hot water
     network (40/50°C) described in 3.7.3.4.

     The heat-recovery function shall operate only when a hot-water
     demand signal is present.

372. The Contractor shall demonstrate, by heat-balance calculations,
     that the recovered-water temperature and the percentage of heat
     recovered meet the 65 % target when the cooling-water supply
     temperature is 27 °C.

     In the offer, the applicant shall quantify the expected heat
     recovery per operating scenario)

     1.  []{#_Toc200492407 .anchor}Interfaces with the Vacuum System

373. The exhaust of the vacuum system(s) from the QPLANT process rooms
     shall be collected and vented outside the building. The location of
     these exhausts shall be subject to approval by SCK CEN.

374. The Contractor shall provide the necessary helium to be used during
     the installation, commissioning phases and acceptance testing
     including leak tests and conditioning of the QPLANT circuits.

     1.  []{#_Toc200492411 .anchor}Interface with LHe (ad-hoc) user and
         associated helium recovery

         1.  Recovery and purification system for ad-hoc user

375. The QPLANT shall include a recovery header for helium gas at room
     temperature and atmospheric pressure collecting safety valves and
     potentially for future external user.

376. Envisaged future external user amounts (future external helium
     users liquid supply by dewar and gaseous return) will be about 200
     litres for initial cooldown and 50 litres/day while the relevant
     experimental setup is operational).

377. This recovery header shall be connected to the LP of the warm
     compressors.

378. The pressure and mass flow through the recovery header shall be
     permanently measured.

379. The possibility to connect in the future to a recovery gas bag and
     external purification system shall exist. The Contractor shall make
     recommendation on required external purification system, or as a
     minimum specify the limits (in terms of impurities) to avoid
     negative impact on the main QPLANT function.

     1.  General

This section defines the physical and functional interface between the
Cryoplant (QPLANT) and an external or ad-hoc user consuming liquid
helium (LHe) and returning gaseous helium (GHe) to the plant recovery
network. The interface is located at QRB.EUR (External User Recovery).

The objective of this interface is to enable safe withdrawal of LHe for
experimental use while ensuring that all boil-off helium is recovered
under controlled pressure, maintaining gas purity and system stability.

2.  Functional Description

The external user shall withdraw liquid helium from a 500 L user-owned
Dewar, transferring it in batch mode to the experiment. The helium
boiled off from the experiment shall be routed back to the QPLANT
recovery network via the dedicated LP return header (QRB.LP).

Typical operating parameters:

  -----------------------------------------------------------------------------
  **Condition**     **Liquid   **Equivalent   **Return Rate**  **Notes**
                    He**       Gas**                           
  ----------------- ---------- -------------- ---------------- ----------------
  Cooldown          200 L      ≈ 149 Nm³      ≈ 0.31 g/s       one-time, short
  (startup)                                                    duration

  Steady operation  50 L / day ≈ 37 Nm³ / day ≈ 0.08 g/s       continuous
  (typical)                                                    boil-off

  High transient (3 ≈ 150 Nm³  ≈ 0.24 g/s     representative   Representative
  × normal)         / day                     upset            upset
  -----------------------------------------------------------------------------

  : []{#_Ref210826960 .anchor}Figure 9 Reference Architecture of the
  Cryogenic Control System

For a 30-day campaign (1 per calendar year), total returned helium ≈ 1
100 -- 1 200 Nm³, equivalent to ≈ 200 kg He.

-   Return pressure: maintained ≥ 1.00 bar(a), nominal 1.05 bar(a).

-   Helium purity for acceptance: O₂ ≤ 1 ppm, N₂ ≤ 5 ppm, dew point ≤
    --80 °C.

-   SCK CEN is fully responsible for Dewar logistics, batch filling, and
    maintaining helium purity

380. QPLANT shall accept helium gas into the recovery network only when
     purity is within specification. If gas analysis indicates
     contamination above limits, the recovery valve shall remain closed,
     and helium shall be vented at the user side.

-   No purification or gas clean-up by QPLANT is foreseen for this
    interface.

![](media/image17.emf)

381. The Contractor shall provide a complete interface assembly at
     QRB.EUR consisting of a check valve, automated isolation valve,
     removable end cap, and gas-sampling take-off. All components shall
     be helium-tight and suitable for room temperature helium.

382. The external-user return circuit shall maintain stable suction
     pressure and flow during all operating conditions.\
     The Contractor shall design the return line to maintain 1.05 bar(a)
     ± 0.02 bar(a) for helium gas flows of 0.06 -- 0.08 g/s (steady) and
     up to 0.30 g/s for short-term transients. Pressure stability and
     flow compliance shall be verified by continuous logging during
     commissioning.

383. Safe isolation and purge capability shall be ensured for all
     operational and maintenance modes.\
     The Contractor shall install remotely operated emergency shut-off
     valves (ESD) on both the liquid-helium supply and gas-return lines,
     closing within 5 s of an emergency signal. Manual vent/purge ports
     shall be provided to allow drying and safe warm-up of the interface
     and user line.

384. Helium recovery shall only occur when the returned gas purity is
     within specification.\
     QPLANT shall accept gaseous helium only when purity meets O₂ ≤ 1
     ppm and N₂ ≤ 5 ppm.

385. The Contractor shall integrate an oxygen and dew-point analyzer at
     QRB.EUR to verify compliance and prevent any process contamination.
     If the gas is out of specification, the recovery valve shall remain
     closed, and the helium shall be vented on the user side.

     1.  []{#_Toc200492412 .anchor}Liquid Nitrogen (LN2)

386. If liquid nitrogen is used for the QPLANT precooling, the
     Contractor shall be responsible for the entire nitrogen equipment
     including liquid nitrogen tanks, heaters, .... If the liquid
     nitrogen is not used for the QPLANT precooling, SCK CEN shall
     procould provide gas helium for regeneration purpose.

387. During installation and commissioning, the Contractor shall be in
     charge to supply the necessary nitrogen linked to these activities.

     1.  []{#_Toc212194863 .anchor}Interfaces with (external) Control
         System

         1.  Interfaces with MCS

388. Where the system has an interface with MCS, the system shall comply
     to the MCS architecture, processes, and interfaces. Ref. SCK
     CEN/38585071.

389. The interface between QPLANT (Contractor) and Control System (ICS)
     shall comply to the Slow Fieldbus Control and Monitoring Interfaces
     type C as listed in MCS Interface Catalogue Ref. SCK CEN/48276492.

     1.  Interfaces with MIS

390. Where the system has an interface with MIS, the system shall comply
     to the MIS architecture, processes, and interfaces.

391. The interface between QPLANT (Contractor) and Interlock System
     (ICS) shall comply to the Slow control interface catalogue.

392. Where the system has a slow interlock interface, the slow interlock
     interface shall comply to the slow interlock interface document:
     Interfaces with MIT

393. Where the system has an interface with MIT, the system shall comply
     to the MIT architecture, processes, and interfaces.

394. The interface between QPLANT (Contractor) and SCK CEN Information
     Technology (ICS) shall comply to the MIT interfaces as listed in
     catalogue Ref. 

395. The QPLANT shall be physically connected to the MIT network in a
     redundant, fault tolerant way. At minimum 2 physical links will be
     foreseen, each link routed via a separate pathway. The physical
     connections need to be distributed over at minimum 2 separate
     physical endpoints on the QPLANT side.

396. The QPLANT shall be connected to the MIT IP network using a single
     logical routed connection (\"layer 3\"). At both sides, a single
     gateway IP will be configured as destination IP for packet
     forwarding.

397. Where the QPLANT:CIS or one of its components supports system
     logging, the contractor shall provide system logs remotely through
     at least one of the protocols mentioned in the MIT interface
     catalogue chapter \"System logging\".

398. Where the QPLANT:CIS support application logging, the System shall
     log remotely either by using a protocol defined in section
     \"Application logging\" of document \"MIT interface catalogue\") or
     alternatively adhere to the following:

-   Logs are provided in a data and file format that is machine
    readable, text based and non-proprietary. Examples of this include
    but are not limited to: CSV (Comma Separated Values), JSON
    (JavaScript Object Notation), GELF (Graylog Extended Log Format) or
    "Common Log Format."

-   The details of the used log format(s) are provided. This includes
    but is not limited to the message structure and the possible
    key/value pairs with their type, value, and description.

-   Logs can be encrypted during transport if the security
    classification of the data permits this, but in this case the
    decryption procedure and required secret(s) need to be provided.

399. The QPLANT:CIS shall support timing synchronization by at least one
     of the protocols mentioned in the MIT interface catalogue chapter
     \"Timing synchronization\".

400. Where the QPLANT:CIS requires remote access; Systems shall provide
     remote access through at least one of the protocols listed in the
     MIT interface catalogue chapter \"Remote access\".

401. The connection of the QPLANT:CIS with MIT, shall terminate on a
     patch panel.
