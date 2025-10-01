5.  []{#_Toc200492611 .anchor}Safety, Codes and Standards

    1.  []{#_Toc200492612 .anchor}Safety

<!-- -->

478. Burst disk outlets shall be routed to avoid cold burn or
     asphyxiation risks.

479. Emergency or rapid venting operations shall be executed via the
     S‑line (QINFRA.S) or by direct QCELL bursting disk exhaust (not
     part of QPLANT scope) venting to atmosphere as designed. Transfers
     of inventory to QINFRA shall be performed only in accordance with
     approved safety procedures, after verification that no personnel
     are present in affected areas, and with active monitoring and
     relief provisions in place.

480. For any 3^rd^ party (e.g. PED auditor) inspection or certification
     needed for requirements compliance, the Contractor shall bare the
     full cost and should preferentially use the SCK CEN nominated local
     representative unless logistically not possible.

481. The Contractor shall propose oxygen‑deficiency‑monitor (ODH)
     locations; final placement approved by SCK CEN. The Contractor
     shall recommend and guide SCK CEN to define the location of the
     oxygen deficiency detectors in the QPLANT buildings.

NOTE: SCK CEN is responsible for ODH sensors and linking to site alarm
and access control.

482. Redundant measurement channels and stand-by heaters shall be
     provided for all inaccessible components and for components whose
     failure would jeopardise operation or safety.

483. Cold helium volumes shall be protected by safety devices in
     accordance with EN 17527 (supplemented, where applicable, by
     API 520/521/580 for warm service). Any cold volume that can be
     isolated by valves, plus all insulation vacuum volumes, shall have
     dedicated safety devices.

484. Safety exhausts shall be collected where feasible or safely vented
     to the outside.

     1.  []{#_Toc212194892 .anchor}Hazard definitions and typical
         mitigation devices

  ---------------------------------------------------------------------------------------
  **Hazard         **Terminology**            **Typical detection **Notes (cryogenic
  category**                                  / protection        helium context)**
                                              device**            
  ---------------- -------------------------- ------------------- -----------------------
  Reduction of     Oxygen-Deficiency-Hazard   Fixed ODH monitor   Primary life-safety
  ambient O₂ below (ODH)                      (electro-chemical   hazard during helium
  safe                                        or paramagnetic     releases or continuous
  physiological                               cell)               Safety-Line venting.
  limits                                                          

  Complete         Asphyxiation / anoxia      --- (medical        Final consequence if
  deprivation of                              condition; not      ODH is not mitigated.
  oxygen to the                               detected by plant   
  body                                        instrumentation)    

  Local freezing   Cold burn (cryogenic       IR skin sensor, PPE Secondary hazard during
  of tissue due to frostbite)                 requirement,        liquid discharge or
  contact with                                duty-holder         cold-gas impingement.
  cryogens                                    training            
  ---------------------------------------------------------------------------------------

  : []{#_Ref211429607 .anchor}Figure 11 MIT Reference Architecture

2.  []{#_Toc212194893 .anchor}ODH Monitoring Architecture and
    Responsibilities

Free-Issue Equipment (FIE)

Fixed ODH monitors, compliant with EN 50104:2019 and rated to
performance class SIL-2, shall be supplied by SCK CEN. SCK CEN retains
responsibility for the certification and demonstration of SIL-2
compliance for the instrumentation forming part of the ODH safety
function.

1.  Contractor Responsibilities

<!-- -->

485. The contractor shall:

-   Install, cable, configure, and commission all ODH monitors provided
    by SCK CEN.

-   Ensure the electrical signal from each sensor is split and
    redundantly routed:

    a.  One signal path to SCK CEN systems (for SIL validation), and

    b.  One signal path to QPLANT:CIS (for local alarms and interlocks).

-   Integrate all alarm thresholds, zoning logic, and mitigation
    responses into QPLANT:CIS.

-   Perform functional testing of all ODH alarm chains during QPLANT
    acceptance.

-   Identify the optimal number and location of sensors required to
    cover the compressor room and coldbox room, based on helium
    Worst-Credible Scenario (WCS) leak analysis.

    1.  Interface Clarification

SCK CEN retains full functional authority over all ODH safety signal
paths. Integration of these signals into QPLANT:CIS must not interfere
with or compromise the SIL-2 certified safety loop. The signal
duplication is for plant alarm and interlock logic only.

486. The Contractor shall install, cable, configure, and commission the
     Free-Issue Equipment (ODH monitors), integrating them into the
     QPLANT control and safety systems.

487. The Contractor shall ensure the electrical signal from each sensor
     is split and redundantly routed:

-   One signal path to SCK CEN systems (for SIL validation), and

-   One signal path to QPLANT:CIS (for alarm integration and
    interlocks).

488. The Contractor shall implement the physical and logical integration
     of ODH signals into QPLANT:CIS, including alarm thresholds, zoning
     logic, and mitigation responses. Functional verification and
     end-to-end testing of all ODH alarm functions shall be demonstrated
     during QPLANT acceptance.

489. The Contractor shall install the owner-supplied ODH monitors at
     every access point and in each enclosed zone where a credible
     helium release could reduce ambient O₂ below 19.5 % (v/v) within 60
     seconds under WCS leak conditions. Sensor positioning, cabling, and
     functional tests fall under Contractor scope.

490. The Contractor shall provide all technical inputs required for SCK
     CEN to complete the final ODH configuration and SIL justification.
     At minimum, this includes:

-   Helium inventory (by zone),

-   Piping layout drawings and enclosure volumes,

-   Leak rate assumptions based on QPLANT operational scenarios,

-   Ventilation performance data,

-   Defined ODH zoning boundaries and access control criteria.

    In the offer the Applicant shall explicitly state explicitly whether
    the ODH system status (e.g. alarm thresholds reached, zone
    evacuation triggered) constitutes a functional input to QPLANT:CIS
    logic. If applicable, the Offer shall describe the intended system
    behaviour, logic dependencies, and impact on cryogenic system
    operation (e.g., automatic warm-up, valve interlocks, or shutdowns).

SCK CEN shall retain overall responsibility for the ODH system\'s
compliance with functional safety requirements. The signals from all ODH
sensors remain under SCK CEN ownership, and their duplication to
QPLANT:CIS shall not alter or interrupt their role in the certified
safety chain.

1.  **Control Systems and PLC safety**

<!-- -->

491. Internal interlocks: The QPLANT shall not rely on the MIS, unless
     the interlock must be propagated to or relies on other systems.

492. Interlock status to MCS: The QPLANT shall ensure that the status of
     each interlock is monitorable through the MCS control interface.

493. Personnel protection standards: When the system has personnel
     protection, the systems personnel protection shall be designed
     according to standards IEC 61508 (Functional Safety) or one of the
     sector-specific derived standards (IEC 62061, IEC 61511) or
     alternative (e.g. ISO 13849-1).

     1.  **Hard-Wired Safety-Interlock Instrumentation**

494. The Contractor shall design and implement fail-safe, hard-wired
     interlock circuits (i.e. dedicated relay or safety-PLC loops that
     remain fully functional in the event of a control-system failure)
     to prevent mechanical or thermal damage to the following critical
     equipment classes: compressors, turbines, pumps, and electrical
     heaters.

495. Electrical contacts associated with the hard-wired interlock
     sensors (flow, pressure, temperature, level, valve-end switches,
     etc.) shall be wired "positive-logic" (open = abnormal/trip) so
     that any loss of signal, power, or cable integrity forces the
     affected component to a safe state.

496. The Contractor's own risk assessment shall determine the final list
     of equipment, set points, and reaction times

-   the resulting safety-interlock list hall be submitted with the
    Detailed Design file.

-   Safety-significant or reliability-critical SSCs such as sensors and
    instrumentation, control and shut-off valves, pressure relief
    devices and bursting disks, actuators, regulators, and any
    components affecting operational safety or availability.

    1.  []{#_Toc200492614 .anchor}Codes and Standards

497. The Contractor shall provide an EU declaration of conformity for
     the QPLANT and CE mark all QPLANT components. Therefore, the
     Contractor shall at least:

     Identify all EU directives applicable to the QPLANT and ensure
     compliance with said EU directives. The directives listed below are
     identified by SCK CEN as a minimum requirement but does not exclude
     other directives from being applicable:

-   Low Voltage Directive 2014/35/EU

-   Machinery Directive 2006/42/EC

-   EMC Directive 2014/30/EU

-   Pressure Equipment Directive (2014/68/EU)

498. The contractor shall identify the applicable standards (harmonized
     or non‑harmonized), and technical specifications that support
     compliance with the essential requirements outlined in the EU
     directive(s).

     The Contractor shall Submit the technical file, at the latest
     before shipment to SCK CEN of QPLANT parts, to demonstrate
     conformity with the directive(s). The technical file shall include:

-   A general description of the QPLANT

-   An overall drawing of the product, as well as other drawings to
    cover specific aspects of the product, such as circuit diagrams. The
    drawings shall, where appropriate, be accompanied with descriptions
    and explanations to understand the product.

-   The HAZOP reports for QPLANT

-   The Interfaces with other SCK CEN systems:

    -   The description of the protective measures implemented to
        eliminate identified hazards or to reduce risks and, when
        appropriate, the indication of the residual risks associated
        with the QPLANT.

    -   The list of standards and other technical specifications used to
        show compliance with the essential requirements outlined in the
        EU directive(s).

    -   Instructions and other information for the safe use of the
        product covering at least, but not limited to, handling,
        shipping, installation, integration, operation, maintenance,
        de-commissioning, disposal, \... in English, and Dutch

    -   Where appropriate, copies of the EU declaration of conformity of
        components incorporated into the assembly.

    -   A copy of the QPLANT EU declaration of conformity in the
        original language, in English, and Dutch.

    -   A copy of the nameplate(s) with CE mark.

<!-- -->

-   The Contractor shall submit specific detailed parts of the technical
    file, when requested by SCK CEN, to demonstrate conformity with the
    directive(s) in English. The detailed parts of the technical file
    are:

    -   Full detailed drawings.

    -   Calculation notes,

    -   Test reports, certificates, \...

        1.  []{#_Toc212194895 .anchor}Electromagnetic interference

499. The Contractor shall propose a solution, subject to approval by SCK
     CEN, to minimize the effects of electromagnetic interference (EMI)
     as referenced in \[AD 7\]. The solution shall address shielding,
     cabling, signal routing, voltage level separation, and grounding
     strategy.

500. The EMI mitigation design shall ensure that all instrumentation and
     control signals operate within their specified accuracy limits
     under defined electromagnetic environments.

501. The proposed solution shall comply with the relevant sections of EN
     61000-6-2 (Immunity for industrial environments) and EN 61000-6-4
     (Emission for industrial environments), or an equivalent standard
     approved by SCK CEN.

     Verification shall be performed by means of:

-   A design review dossier including EMI layout drawings and shielding
    measures,

-   A wiring and installation checklist verified during site inspection,

-   And, where applicable, EMC type tests or certificates for sensitive
    components (e.g., sensors, analysers, PLCs).

502. To ease diagnostic and checking of measurement chains, knife-switch
     type terminal blocks or similar cabling interface shall be fitted
     for input and output signals connections with the QPLANT:CIS.

     1.  []{#_Toc212194896 .anchor}Pressure Equipment & Safety

  -------------------------------------------------------------------------
  **Ref**         **Standard**                 **Scope**
  --------------- ---------------------------- ----------------------------
  PED             2014/68/EU                   EU Pressure Equipment
                                               Directive

  ASME VIII‐1     Unfired pressure vessels     Design / certification

  EN 13445        Unfired pressure vessels     EU compliance

  API 520/521     Pressure relief sizing &     PSVs / BD
                  selection                    

  EN ISO 4126     Safety valves & RD devices   Proof‑test ≤ 5 y

  ISO 21013‑1/2   Cryogenic safety devices     LP & HP vessels
  -------------------------------------------------------------------------

  : []{#_Ref192519000 .anchor}Table 12 Preliminary pipe diameters for
  the QLM

2.  []{#_Toc200492636 .anchor}Functional Safety & Control

  -----------------------------------------------------------------------
  **Ref**            Standard                       Scope
  ------------------ ------------------------------ ---------------------
  IEC 61508          Functional safety (E/E/PE      SIL assignment
                     systems)                       

  IEC 61511          SIS for process industry       SIS lifecycle

  IEC 60204‑1 /      Electrical equipment &         Control cabinet
  61439              switchgear                     

  IEC 60300‑3‑3      RCM assessment                 Links to DMAIC
                                                    Control
  -----------------------------------------------------------------------

  : []{#_Toc212194970 .anchor}Table 13 Interface ID between QRB and
  QINFRA (warm interfaces)

3.  []{#_Toc200492637 .anchor}Asset & Maintenance Management

  ------------------------------------------------------------------------
  Ref              Standard                       Scope
  ---------------- ------------------------------ ------------------------
  ISO 55000        Asset management lifecycle     40‑y RCM plan

  ISO 14224        Reliability & maintenance data MTBF reporting

  IEC 60300‑3‑12   Life‑cycle costing             CAPEX/OPEX modelling
  ------------------------------------------------------------------------

  : []{#_Toc212194971 .anchor}Table 14 Internal QPLANT Distribution
  Lines (crossing multiple rooms)

4.  []{#_Toc200492638 .anchor}Cleanliness & Purity

  -----------------------------------------------------------------------
  Ref                Standard                        Scope
  ------------------ ------------------------------- --------------------
  ISO 8573‑1 Class 0 Oil‑free compressor             Compressors
                     classification                  

  ASTM D5464         Helium purity test              Getter skid
                                                     validation
  -----------------------------------------------------------------------

  : []{#_Toc212194973 .anchor}Table 16 External Helium User
  Quantification

5.  []{#_Toc200492639 .anchor}Proof‑Test & Control‑Phase Requirements

-   Proof‑test intervals: PSVs/BDs ≤ 5 years; SIL sensors ≤ 3 years;
    logic proof ≤ 4 years.

-   RCM linkage: Tests scheduled in RCM manual per ISO 55000 /
    ISO 14224.

503. The Contractor shall provide to SCK CEN the applied codes, rules
     and standard for the design, manufacturing, and testing of the
     QPLANT.

<!-- -->
