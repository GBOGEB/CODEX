    1.  []{#_Toc200491815 .anchor}QPLANT Design & Construction
        Requirements

*In the offer, the Applicant shall describe and justify the system
architecture and configuration and provide the key specifications of the
main components.*

1.  []{#_Toc212194830 .anchor}Units

<!-- -->

34. All pressure values shall be stated as absolute values in bar(a) or
    mbar(a)

35. All other units shall follow the International System of Units (SI),
    with exception of flow in g/s (not kg/s)

    1.  []{#_Toc212194831 .anchor}3D Model

36. The Contractor shall deliver a detailed 3D CAD model of the QPLANT
    and associated components to ensure interoperability, detailed
    design accuracy, and lifecycle integration:

37. The Contractor shall submit a preliminary 3D model in the Concept
    Design phase.

    a.  The file format shall be STEP AP242 format

    b.  The Level of Detail (LOD) shall be at least LOD 200.

    c.  The model shall include a first indication of the location of
        all external interfaces (to SCK CEN support systems and
        infrastructure and QLM)

38. The Contractor shall submit an updated 3D model in the Final Design
    phase.

    a.  The file format shall be STEP AP242 format.

    b.  The 3D model shall include metadata such as component IDs,
        geometric data, material properties, kinematic information,
        assembly information.

    c.  The Level of Detail (LOD) shall be 400 (final installation-ready
        models).

    d.  The models shall include the terminal points to the SCK CEN
        provided site infrastructure and support systems (water cooling,
        MIT, ....).

39. The Contractor shall submit an as built 3D model before the SAT.

    a.  The Level of Detail (LOD) shall be LOD 500 (operational/as built
        model)

        In the offer, the Applicant shall:

-   Present the tools that he shall implement to allow SCK CEN to review
    the models (SCK CEN internally uses BIMS 360 and PTC CREO).

-   Provide a preliminary model of the QPLANT with at least LOD 100 in
    STEP AP242 format.

    1.  []{#_Toc212194832 .anchor}Energy-efficiency

40. The QPLANT shall have an invCOP ≤ 380 W/W at the Nominal Design
    Point.

41. Any deviation greater than 5% from the claimed inverse COP at final
    acceptance shall trigger contractual review, including performance
    non-conformity, penalties, or corrective actions.

    In the offer the Applicant shall state and substantiate the invCOP
    for all operational scenarios, both for initial (24 QCELLs) and
    nominal design (30 QCELLs) configurations. Lower invCOP values are
    considered an advantage.

42. The Contractor shall validate compliance of the QPLANT to the invCOP
    that the Contractor committed to in their offer at each contractual
    stage and report it in every design reviews The Contractor shall
    apply mutually agreed calorimetric, flow‑based, or standardized test
    methods (e.g., ISO 5167, EN 13445).

    In the offer, the Applicant shall

-   Include the electrical power measurement method they will apply
    within the QPLANT, specifying the level of integration (e.g., total
    plant consumption including auxiliaries, compressors, control
    systems) and the measurement uncertainty.

-   Specify the corresponding reciprocal measurement methodology
    expected to be applied by SCK CEN, to validate claimed energy
    figures.

    1.  []{#_Toc200491995 .anchor}General Electrical Requirements

43. All electrical components (including cables, cabinets, cable trays,
    and associated systems) shall comply with the applicable
    international electrical standards, including but not limited to IEC
    61508 and IEC 61511 for lifecycle functional safety aspects, and
    \[AD 6\].

44. The selection of cable sheathing materials shall explicitly consider
    and be validated against the environmental conditions to which they
    will be exposed, including moisture, oil, cable trenches, heat and
    freezing temperatures, and electromagnetic interference (EMI)
    effects.

45. Each electrical and instrumentation cabinet shall provide at least
    25% of its internal volume as free space to accommodate future
    installation of equipment, cabling, or modifications without
    necessitating structural change.

46. The Contractor shall install harmonic filtering devices on all major
    variable frequency drives (VFDs) (e.g., LP and HP compressors), in
    accordance with \[AD 6\] and the requirements of IEC 61800-3 for
    industrial electromagnetic environments.

    The Contractor shall ensure that emission and immunity limits are
    met through appropriate use of input line filters, output dv/dt
    filters (where applicable), and proper shielding, grounding, and
    cable routing practices.

47. The Contractor shall ensure that all VFD-driven motors operate
    within the allowable continuous frequency range defined by IEC 60034
    (Rotating Electrical Machines). Nominal VFD operation shall not
    exceed 60 Hz, unless the Contractor provides substantiated evidence
    demonstrating that:

-   The selected motor and compressor system are rated for sustained
    operation above 60 Hz.

-   The expected Mean Time Between Failures (MTBF) at the proposed
    operating frequency is documented and acceptable.

-   All required mitigations are in place (e.g., output filtering,
    derating, bearing protection, insulation class suitability).

    1.  []{#_Toc212194834 .anchor}Design, Materials

        1.  Material Requirements

48. All materials shall be delivered with traceable certificates.

    1.  Cleaning and surface treatment

49. All welding and brazing surfaces shall be cleaned before assembly,
    using proper solvents and water to remove any trace of acid flux,
    organic depositions and any other dirt and dust.

50. All metallic surfaces in contact with He shall be cleaned, pickled,
    and passivated. Prior to helium leak testing all involved components
    in contact with He shall once again be cleaning (degreasing,
    cleaning, and drying).

    1.  Bellows

51. Bellows to compensate thermal contraction shall be avoided through
    proper piping design. If unavoidable, the Contractor shal0l seek
    SCK CEN approval for the location and type of bellows.

    *In the offer, the Applicant shall include a preliminary list of
    unavoidable bellows (if any).*

    1.  Joints and seals

52. Dismountable joints in the QRB below room temperature are not
    recommended and shall be subject to approval by SCK CEN. At ambient
    temperature, metal and Viton O-rings are allowed.

    1.  Valve requirements

53. The cryogenic valves inside the QRB shall be of the extended-spindle
    type, sealing by metallic bellows.

54. All helium shut-off valves (independent of helium temperature) shall
    comply with the following requirements:

    a.  Valve Type Selection

-   Ball valves shall be employed for nominal sizes up to and including
    DN100, unless otherwise justified by process or safety requirements.

-   Butterfly valves shall be employed for nominal sizes above DN100,
    except where specific process conditions (such as full tightness at
    cryogenic temperature or throttling requirements) necessitate
    alternative selection.

    a.  Qualification and Documentation

-   The Contractor shall submit documentation of type testing or
    qualification records demonstrating suitability for helium and
    cryogenic operation in accordance with EN 1626 and EN 12516-1/2 as
    part of the Conceptual Design file in LCP1.

    a.  Installation Requirements

-   Shut-off valves shall be welded to the pipework and preferably to
    the top plates of the QRB.

55. Every control valves shall be equipped with:

    a.  electro-pneumatic positioners

    b.  a digital position-feedback. This signals shall be continuously
        monitored by the QPLANT:CIS.

56. Manual on/off valves that are safety-relevant or operationally
    critical (as identified in the approved reliability and safety
    analyses) shall be equipped with two independent end-switches
    confirming their mechanical position (open/closed) during operation.
    The Contractor shall submit the list of such valves for SCK CEN
    approval during the detailed-design phase.

    1.  Helium guard

57. Every component operating below atmospheric pressure shall be
    protected from air ingress by a helium guard filled with helium with
    a pressure higher than 1.05 Bar(a).

58. Each helium guard segment shall equipped with a manual isolation
    valve to help locate leaks.

59. The helium guard pressure shall be remotely monitored by a pressure
    transmitter which is connected to the QPLANT:CIS.

60. All static seals, which are not welded and operating between
    atmospheric air and sub-atmospheric helium, shall be doubled. The
    space between the seals shall have a connection to the helium guard
    system.

    1.  Insulation vacuum system of the QRB

61. The QRB shall be equipped with a dedicated vacuum pumping system.

62. The pump down of the QRB from atmospheric pressure to less than
    10^-5^ mbar shall take less than one week.

63. The QRB vacuum shall be protected by a fast-acting isolation valve
    between the turbo pump and associated roughing pump.

64. A dedicated flange shall be provided between the Turbo- and
    associated roughing pump for connection of a leak detector.

65. The pump down of the vacuum system shall be fully automated.

66. All valve actuators and vacuum gauges shall fully exposed to MCS.

67. Pending completion of a risk assessment for asphyxiation hazards, if
    operation of the roughing pump presents an asphyxiation risk, the
    exhaust shall be routed outside the building via a dedicated pipe.
    This requirement shall be confirmed and finalized no later than the
    Conceptual Design phase.

    1.  Instrumentation

68. The Contractor shall furnish and install all instrumentation
    required to:

-   enable automatic control of all QPLANT operational scenarios.

-   maintain safe operating conditions; and

-   verify compliance with the specified performance criteria during
    acceptance testing.

    The Contractor shall demonstrate, by reference to internationally
    recognised calibration certificates or equivalent traceable
    documentation, that every measuring instrument supplied is suitable
    for its intended purpose.

69. The Contractor shall define the instrumentation layout and
    measurement ranges and submit the documentation to SCK CEN for
    review and approval at the Detailed-Design stage.

70. The complete, as-built wiring diagram of the instrumentation and
    control circuits shall be included in the Deliverables package.

71. The Contractor shall submit a complete set of documentation for each
    instrumentation element including but not limited to calibration
    curves, power rating, location, and protection set points (where
    applicable).

    1.  Heaters

72. Each electrical heater shall incorporate a temperature control
    ensuring the specified maximum sheath or process temperature is not
    exceeded.

73. Heating elements needed for normal control or operation shall
    either (a) be replaceable without breaking the insulation vacuum,
    or (b) be implemented redundantly.

74. Real-time heater power measurements shall be transmitted to the
    QPLANT:CIS for trending and alarm purposes.

75. All heater circuits shall successfully pass a dielectric test in
    accordance with applicable IEC/EN standards:

    a.  Test Stages

    b.  A dielectric test shall be performed after each major
        installation phase.

    c.  A final dielectric test shall be performed at hand-over.

    d.  Acceptance Criteria

    e.  No breakdown of insulation or abnormal leakage current shall
        occur under the specified test voltage and duration.

        1.  Temperature measurements

76. Temperature measurements (including the whole thermometry chain)
    shall meet the requirements listed in Table 5.

+------------------------------------+----------+----------+----------+
| Nominal Temperature                | > \< 30  | > 30 K   | > \> 120 |
|                                    | > K      | > to 120 | > K      |
|                                    |          | > K      |          |
+------------------------------------+----------+----------+----------+
| Accuracy required for standard     | > ≤ +/-  | > ≤ +/-  | ≤ +/- 1  |
| measurements                       | > 100 mK | > 500 mK | K        |
+------------------------------------+----------+----------+----------+
| Accuracy required for high         | > ≤ +/-  | > ≤ +/-  | not      |
| precision measurements             | > 50 mK  | > 300 mK | ap       |
|                                    |          |          | plicable |
+------------------------------------+----------+----------+----------+
| Long term drift for the whole      | > ≤ +/-  | > ≤ +/-  | ≤ +/-    |
| scale                              | > 10 mK  | > 50 mK\ | 100 mK\  |
|                                    | > per    | > per    | per year |
|                                    | > year   | > year   |          |
+------------------------------------+----------+----------+----------+

: []{#_Ref211437030 .anchor}Figure 6 Operational scenarios and
transitions for the Cryogenic System. Blue boxes indicate steady states
while light blue boxes indicate transients

77. For each temperature measurement, the Contractor shall submit a
    proposal of classification (standard or high precision as defined in
    Table 5) for review and approval by SCK CEN.

78. The cabling between each temperature sensing element and its
    associated signal conditioning device shall be designed and
    installed to ensure accurate, stable, and noise-immune signal
    transmission under all specified operating and environmental
    conditions.

-   The Contractor shall employ shielded, twisted-pair conductors or
    functionally equivalent solutions to minimise electromagnetic
    interference (EMI), preserve signal resolution, and enable
    compensation of lead resistance when required by the selected
    measurement method (e.g. 3-wire or 4-wire RTDs).

-   The Contractor's selected cabling solution shall be justified by
    reference to recognised standards or design practices, such as IEC
    60751, IEC 60359, ISA RP12.6, or other EMI mitigation guidelines
    accepted in industrial instrumentation. Temperature elements outside
    cold boxes shall be mounted directly in the fluid stream, using a
    protection tube welded on the pipe.

    1.  Pressure measurements (incl. vacuum gauges)

79. Each pressure transmitter shall be installed with at least:

-   one isolation valve to allow safe removal, calibration, or
    replacement without depressurizing the connected volume or
    interrupting vacuum operation

-   one dedicated connection for calibration or venting, also fitted
    with an isolation valve.

80. Each differential pressure transmitter shall additionally be
    equipped with a bypass valve and calibration valve.

81. The measurement ranges of all pressure instruments shall be defined
    by the Contractor and submitted as part of the Detailed Design File.
    Special attention shall be given to the Very Low Pressure (VLP)
    lines.

82. All pressure transmitters shall withstand, without de-calibration or
    damage, any pressure from vacuum up to the Operating Pressure
    defined by the relevant safety valve setting.

83. Accuracy of measurement shall comply with:

-   Long-term drift of pressure instruments shall not exceed ±0.5 % of
    the maximum span per year.

-   The accuracy for absolute pressure measurement shall be better than
    ±0.5 % of the calibrated span.

-   The accuracy for differential pressure measurement shall be better
    than ±0.25 % of the calibrated span.

-   Vacuum pressure measurement shall cover the range from 10³ to 10^-7^
    mbar

84. Vacuum gauges shall be capable of withstanding gas inrush without
    loss of calibration or mechanical damage.

    1.  Liquid level measurements

85. The Contractor shall measure the liquid-helium level in the QRB
    using either differential-pressure (qualified for cryogenic service)
    or superconducting level sensors.

86. The design, placement and operation of liquid-level sensors shall
    ensure that their readings are not influenced by:

-   bubbles generated by electrical heaters; or

-   flow turbulence or other hydraulic disturbances inside the vessel.

87. Liquid-level readings shall be displayed to operators as a
    percentage of the nominal working volume.

    The indicated value (including repeatability, hysteresis, and
    calibration drift) shall be accurate to:

-   ± 2 percentage points of full scale for liquid helium; and

-   ± 5 percentage points of full scale for all other cryogenic fluids.

    1.  Helium flow rate measurements

88. The accuracy of helium flow rate measurements at cryogenic
    temperature shall be better than 5% of the full range.

89. For helium flow rate measurements at room temperature the accuracy
    required shall be better than 2% of the calibrated span.

    1.  Helium Impurity measurements

        1.  Pick-ups and sampling

90. The location of sampling points shall be agreed with SCK CEN.

91. Two dedicated gas analyser shall be installed - one in the
    compressor room and the second one in the cold box room.

92. These sampling lines shall be provided with at least a pressure
    regulator, a proper removable filter element and a manual process
    isolation valve. All capillaries used for permanent monitoring shall
    end at the gas analysis.

93. Temporary sampling points shall be equipped with at least a manual
    process isolation valve and a plug.

94. Each gas analyser shall be equipped with a dedicated calibration
    line.

95. The analysed gas samples shall be sent back to the Low Pressure Line
    of the WCS (WCS-LP)

    1.  Gas analysis requirements

96. The Contractor shall implement continuous measurement of moisture
    and nitrogen content in the helium gas stream with the following
    performance:

-   measurement range of 0--100 ppm by volume for both moisture and
    nitrogen.

-   measurement accuracy better than or equal to ±1 ppm by volume across
    the entire range.

-   Long-term drift shall not exceed ±1 ppm by volume per year.

97. The Contractor shall implement a residual hydrocarbons measurement
    in the compressor room,

98. The gas analyser shall trigger alarms on the QPLANT:CIS in the event
    of any anomaly or deviation from specified thresholds.

    1.  []{#_Toc212194835 .anchor}Welding

99. The Contractor shall comply with the following requirements:

-   All welds shall be completed by welders who are certified in
    accordance with EN ISO 9606-1 and/or EN ISO 14732 (latest edition)
    or equivalent.

-   All operating modes for each type of welding shall be qualified in
    accordance with EN ISO 15614-1, or equivalent.

-   The staff carrying out the non-destructive testing shall be
    qualified in accordance with ISO 9712, level 2, industrial sectors.

-   The welding procedures shall comply to EN 15614-1(/A1, and /A2)

100. All permanent junctions shall be welded. Brazing is permitted only
     in exceptional cases and subject to prior approval by SCK CEN.

101. All junctions separating helium and water circuits shall be welded
     with the weld located on the water side.

     1.  Weld inspections

102. The Contractor shall inspect all welds in compliance with the
     applicable standards. To this end, the Contractor shall:

-   Perform radiographic inspections for bulk defects in accordance with
    EN 17636 and EN 25817 (where applicable).

-   Perform visual inspections.

-   Perform endoscopic (visual) inspections on all hidden welds,
    including but not limited to butt welds, inner welds, and welds in
    cryogenic piping.

103. The weld examinations shall include, at minimum:

-   100% of the longitudinal welds.

-   100% of the T-junctions.

-   25% of the circular welds (per welder, evenly distributed over the
    circular welds performed by that welder).

    The Contractor shall:

-   Indicate in the Manufacturing File which circular welds are selected
    for inspection.

-   Provide the results of the welding inspections to SCK CEN within one
    week after completion.

104. The Contractor shall provide associated valid certificates of the
     qualified personnel for any on-site welding

105. Certified personnel shall conduct the weld inspections, pressure,
     and leaks tests.

106. For tests of weld that are performed on-site,

-   radiography with degree of inspection as required by the applicable
    codes.

    1.  []{#_Toc212194836 .anchor}Machine Protection

107. The QPLANT shall protect itself against/minimize damage as far as
     reasonably possible. The Contractor shall perform a risk analysis
     (e.g. HAZOP, FMECA, or equivalent methodology) and implement all
     required mitigation measures. This shall include but not limited
     to:

     a.  QPLANT external interfaces

         i.  Loss of utility (e.g. electricity, water, compressed air,
             ...)

         ii. Faulty/missing interface to the MCS

         iii. Operation of the users outside the nominal interface
              parameters

     b.  Operator error

     c.  Any QPLANT internal failure e.g. loss of vacuum, QPLANT trip

108. The recovery header (QRB.S) shall be protected against over
     pressures by safety devices and non-return valves.

     1.  []{#_Toc200491892 .anchor}Purging

109. The Contractor shall install all the necessary equipment and
     connections required for the remote purging (venting, pumping, and
     filling) and conditioning of the QPLANT.[]{#_Toc200491898 .anchor}

     1.  Helium Inventory management

110. The QPLANT shall minimize the loss of helium in all operation
     conditions (including failure modes).

111. In normal operation, the QPLANT shall loose at maximum 1Nm^3^ of He
     per day.

112. The Contractor shall implement a helium leak detection and
     monitoring system in accordance with EN 13185:2001, Clause 6.2
     (Leak Detection Methodology) or equivalent, including routine leak
     testing and automated isolation mechanisms.

113. The leak rates (including all interconnecting piping, joints and
     components operating at Operating Pressure and ambient temperature)
     shall not exceed the values defined in Table 6. The system shall be
     qualified for leak-tightness under operational and standby
     conditions.

  -----------------------------------------------------------------------
  **Type of Leak**                                       **Maximal leak
                                                         rates**
  ------------------------------------------------------ ----------------
  Per helium circuits to vacuum                          1×10⁻⁸ mbar·L/s

  Per helium or helium-oil circuits to the water         1×10⁻⁸ mbar·L/s
  circuits                                               

  Per LN2 circuit to helium circuits                     1×10⁻⁸ mbar·L/s

  Per helium guard to sub-atmospheric circuits           1×10⁻⁵ mbar·L/s

  Per from helium and oil circuits to atmosphere         1×10⁻⁵ mbar·L/s

  Combined leakage from all heat exchangers of the cold  1×10⁻⁵ mbar·L/s
  boxes to vacuum vessel                                 

  Combined leakage from all helium circuits to vacuum    1×10⁻⁵ mbar·L/s
  vessels                                                

  Leak rate through a valve seat                         1×10⁻⁴ mbar·L/s

  Leak rate from a valve to atmosphere                   1×10⁻⁵ mbar·L/s

  Leak rate from a valve to vacuum                       1×10⁻⁸ mbar·L/s
  -----------------------------------------------------------------------

  : []{#_Toc200491806 .anchor}Table 3 Heat Loads Summary from QCELLs and
  Cryogenic Distribution

In the offer, the Applicant shall explicitly quantify and elaborate:

-   Expected global local leak rates, including diffusive losses
    expressed as % loss per year. Estimated number and types of valves
    and fittings contributing to leak paths.

-   Type of helium leak detection methods, pressure hold test
    procedures, vacuum decay, or rise time methodologies, and long-term
    monitoring techniques. Acceptance criteria for each method and the
    calibration procedure for leak detection equipment.

-   Post-installation and operational phase monitoring strategy, if
    applicable, including thresholds and frequency

-   Expected losses of helium during conventional pump, purge, and
    conditioning (QPLANT only) and user estimation based on internal
    volume (total pipe length and 90 l per cavity)

114. The Contractor shall calculate the total helium inventory required
     for the Cryogenic System, including QPLANT and all helium users
     listed in Table 7.[]{#_Ref185003225 .anchor}

Table 7 Helium Inventory

+-----------------+------------------------------------+--------------+
| **Component**   | **Helium inventory data**          | **Helium     |
|                 |                                    | Mass (kg)**  |
+=================+====================================+==============+
| Cryomodules     | QM (\~ 90 litres of helium per     | 440          |
| (QM) including  | cryomodules)                       |              |
| QVE.            |                                    |              |
|                 | +QVE \~ 200 litres                 |              |
+-----------------+------------------------------------+--------------+
| Cryogenic       | > VLP return \~ 2 kg               | 30           |
| distribution:   | >                                  |              |
|                 | > SHe supply \~ 15 kg              |              |
| QVB and QLM for | >                                  |              |
| 2K operation    | > TS supply-return \~ 12 kg        |              |
|                 | >                                  |              |
|                 | > Warm He lines \~ 1 kg            |              |
+-----------------+------------------------------------+--------------+
| QPLANT          | To be determined by the Contractor | TBD by       |
|                 | of the QPLANT                      | Contractor   |
+-----------------+------------------------------------+--------------+
| Gaseous warm    | Remaining inventory during         | TBD by       |
| storage         | operation.                         | Contractor   |
|                 |                                    |              |
|                 | To be determined by the Contractor |              |
|                 | of the QPLANT                      |              |
+-----------------+------------------------------------+--------------+

: []{#_Ref192161189 .anchor}Table 4 Fluid Conditions at the Refrigerator
Cold Box Interfaces for Different Operating Scenarios

1.  Abnormal conditions

<!-- -->

115. In case of an abnormal event, no more than 1% of inventory shall be
     lost. To this end, the Contractor shall implement a comprehensive
     helium recovery strategy covering all credible initiation events,
     including but not limited to LOOP, Loss of Vacuum or Instrument
     Air, Cooling Circuit Trip, Turbine Trip, QRB Trip, HP Compressor
     Trip, and PVPS Trip. For each scenario, the Contractor shall
     identify at least:

-   The required recovery mechanisms (e.g., buffer storage, valve
    isolation, overpressure protection),

-   The stepwise action plan to resume normal helium circulation once
    the initiated event is resolved.

    The strategy shall be supported by engineering justifications and
    include timelines, buffer sizing assumptions, and any control system
    responses.

116. In case of a LOOP event, the following shall apply concerning the
     Instrument Air Supply:

     a.  SCK CEN will continue to supply the Instrument Air for initial
         valve actuation (Fail-Closed or Fail-Open). However, this does
         not constitute a continuous supply obligation during LOOP.

     b.  The QPLANT shall contain a pneumatic backup system to allow
         helium recovery operations during a LOOP event. It shall have a
         minimum autonomy of 6 hours under full helium recovery load
         conditions

         The pneumatic backup system be commissioned and functionally
         tested during the SAT under simulated LOOP conditions to verify
         switching, autonomy, and integration with the helium recovery
         sequence.

         1.  Helium recovery

117. The Contractor shall implement a comprehensive helium recovery
     strategy able to cope with the following He flow from the users:

-   200 g/s (300 K, \~1.2 bar) for the enveloping LOOP event mass flow

    In the offer the Applicant shall present a high-level description of
    the helium recovery strategy including but not limited to a Bill of
    Materials (BoM) of all recovery components, including low-pressure
    gas balloon storage and/or high-pressure compressor-driven recovery
    options and/or dedicated purification system.

    In the offer, the applicant shall indicate what Structures Systems
    and Components (SSC), or other design provisions required to
    contain/minimize all helium losses to no more than 1% of total
    inventory.

118. The QPLANT shall have an input to the QRB‑S where the QCELL safety
     valves shall discharge to via the QINFRA-S line.

     1.  []{#_Toc200491990 .anchor}Warm Compressor Station

         1.  WCS General Requirements

119. The Warm Compressor Station (WCS) shall facilitate helium
     compression across at least three pressure levels:

-   VLP (Very Low Pressure)

-   LP (Low Pressure)

-   HP (High Pressure)

120. The WCS shall be connected to the warm gas helium storage (WHS).

     1.  WCS Valve Requirements

121. A minimum of one bypass valve shall be installed between each pair
     of pressure headers (VLP ↔ LP and LP ↔ HP). Each bypass valve shall
     be sized to pass ≥ 100 % of the maximum steady-state mass-flow rate
     of the associated compressor train under the worst-case
     differential-pressure condition.

122. A control valve shall be installed in the connection from the
     helium-gas storage to the LP suction header for loading.

123. A control valve shall be installed in the connection from the HP
     discharge header to the helium-gas storage for unloading. This
     valve shall be installed downstream of the fine dust filter after
     the oil charcoal adsorber.

124. All helium connections between the WCS and the QRB shall be routed
     through control valves located inside the WCS building to limit
     pressure-transient rates to values approved by SCK CEN.

125. Suction and discharge lines of every compressor stage shall be
     fitted with non-return valves that automatically close when the
     compressor stops.

     1.  Noise level

126. The sound-pressure level of each compressor shall not exceed 80 dB
     at 1 m during any steady-state operating mode. Noise tests shall be
     performed for each compressor and its electric-motor drive in
     accordance with ISO 2151 (or an equivalent international standard)
     after FAT and after SAT, and reports shall be submitted to SCK CEN.
     The results shall be documented in reports which shall be submitted
     to via VLAREM dossier

     *In the offer, the Applicant shall state guaranteed per-unit and
     complete-skid noise levels at 1 m, describe the envisaged
     noise-mitigation elements (e.g., acoustic enclosures,
     intake/exhaust silencers, isolation mounts), and identify the
     configuration to be used for FAT/SAT noise tests.*

     1.  Vibration level

127. The maximum vibration levels of the compressors and other rotating
     machines shall comply to ISO 2372 (or its successor ISO 20816).
     During the design phase, the Contractor shall submit a
     vibration-analysis report and calculation dossier for SCK CEN
     approval. During SAT, the Contractor shall measure the vibration
     using calibrated instruments and test methods in accordance with
     ISO 2954.

     1.  Compressors requirements

128. There shall be at least three (3) compressors per compressor stage.

129. All compressors of one compression stage shall identical.**Error!
     Not a valid bookmark self-reference.**. The coupling shall comply
     with API 671 / ISO 10441 (or equivalent).

![](media/image11.emf){width="4.30625in" height="1.7166666666666666in"}

130. Each compressor skid shall include an oil-retention reservoir sized
     to contain the full oil inventory of the skid in the event of pipe
     rupture.

131. Each compressor shall have an internal slide‑valve control
     providing stable turndown to ≤ 30% of rated mass flow (nameplate
     flow at rated conditions) without surge or recycle over the
     specified operating pressure range.

132. Each compressor motor shall be equipped with a variable‑frequency
     drive (VFD) rated for full‑load current.

133. The VFD speed control shall provide primary capacity turndown; the
     internal slide valve shall provide trim control and anti‑surge
     stabilization across the operating range. The control strategy
     shall minimize power consumption in all load conditions.

     *In the offer, the Applicant shall state the number of LP
     compressors and HP compressors and confirm the long term
     sustainable operating frequency.*

     1.  Coolers

134. On the gas side, each cooler shall include purge valves suitable
     for nitrogen blow-through or helium rinse.

135. On the water side, valves to drain the water and to purge the air
     shall be installed.

136. A manual or thermostatic control valve shall be installed at the
     outlet of each cooler to regulate the water flow.

137. A manual water shut off valve shall be installed at the inlet of
     each cooler.

     1.  Oil

138. The Contractor shall supply all required compressor oil for the
     first filling. The particle size shall not exceeding 25 µm and the
     water content 1 ppm v/v.

139. In the operation and maintenance manual, the Contractor shall
     include:

     a.  detailed procedures for oil preparation, dehydration, and
         filtration.

     b.  the sampling frequency for the routine oil-analysis

     c.  specifications and acceptance limits for particle count, water
         content and acid number.

         1.  Oil circulating system

             1.  Oil-pump units

140. Each compressor shall be fitted with a dedicated, automatically
     controlled auxiliary oil pump unit that maintains the minimum
     bearing-lubrication pressure during start-up, shutdown, and
     coast-down.

141. Each auxiliary oil-pump unit shall be equipped with suction and
     discharge pressure transmitters and a flow switch which interlocks
     the compressor protection system.

     1.  Oil-retention vessel

142. Each oil-retention vessel shall be fitted with an electric heater
     to pre-heat the oil prior to compressor start-up.

143. Each oil-retention vessel shall include a differential-pressure
     indicator across the internal separator to allow fouling
     monitoring.

     1.  Oil filters

144. The inlet of each compressor oil-pump shall be protected by duplex
     (change-over) filters rated 25 µm absolute, mounted in parallel.

145. A fine oil filter shall be installed at the injection points of
     compressor bearings and shaft seals.

146. Manual shut-off valves shall be installed upstream and downstream
     of every oil filter.

147. A differential-pressure gauge shall be provided across each oil
     filter to give a visual indication of filter blockage.

     1.  Oil Purge and fill up requirements

148. Each compressor shall be equipped with manual isolation valves in
     all connecting piping to permit full circuit isolation for
     maintenance.

149. The Contractor shall design the purge system and slope all relevant
     piping at a minimum gradient of 1 % toward designated oil traps to
     prevent migration of oil into oil-free regions.

     1.  Oil Removal System (ORS)

         1.  Coalescers

150. Downstream of the HP primary oil removal system, at least three
     coalescing filters shall be installed in series, with dimensions
     such that sufficiently low gas velocity is achieved through the
     filter elements for efficient coalescing.

151. The Coalescer shall be designed with a 20% gas velocity margin.

152. The coalescer arrangement and its seal construction shall be
     capable of withstanding compressor vibration.

153. All coalescers shall be equipped with a standpipe on which magnetic
     level indicator is positioned. The level shall be monitored locally
     and remotely.

154. The oil collected from the first two coalescers is to be
     re-injected to the suction side of the LP/HP compressors. The
     automatic flush of oil from the coalescer to the compressor suction
     shall be carried out using a motorized valve controlled by the
     level indicator mentioned above.

155. The last coalescer operates as guard unit. Any sign of oil
     collected therein shall lead to a shutdown of the compressor
     station.

156. The coalescers shall reduce the oil content of the stream to less
     than 40 ppb.

     1.  Charcoal adsorber

157. The charcoal adsorber shall be designed with a 20% gas velocity
     margin.

158. Only cleaned and dried charcoal in the form of smooth pellets shall
     be used as adsorbent filling. No filling consisting of irregularly
     broken particles shall be used. The filling of the bed shall be
     regular and no preferred paths for the helium may exist.

159. The Charcoal adsorber shall reduce the oil content of the stream to
     less than 10 ppb.

160. The Contractor shall demonstrate (based on design and previous
     experiences) that any movement of the adsorbent and the carry-over
     of dust particles is avoided. E.g. the flow direction of the gas
     through the charcoal bed shall be from top to bottom.

161. The Contractor shall supply any equipment necessary to fill the
     adsorber without degrading the adsorbent.

162. The Contractor shall supply the heating unit necessary for drying
     the charcoal.

     1.  Helium dryer

163. The dryer shall remove water in the helium to less than 1 ppm.

164. The dryer shall generate a total pressure drop of less than 0.5
     bar.

165. The adsorbent material shall be a molecular sieve of alkali
     alumina-silicate (Zeolite) or equivalent.

166. The helium dryer shall be dimensioned for the full helium mass flow
     (HP total mass flow) contaminated with up to 50 ppm by volume of
     water for a duration of 12 hours before regeneration.

167. The regeneration shall be performed by circulation of warm and dry
     nitrogen gas.

168. The regeneration time shall not exceed 12 hours.

169. The helium dryer unit shall include inlet and outlet valves and a
     by-pass circuit.

     1.  Gas Filters

170. The Contractor shall install at least the following gas filters:

-   At the suction side of each compressor a wire mesh filter of 100 µm
    of retention ability.

-   Downstream of the charcoal adsorber, an adapted wire mesh filter to
    stop particles of charcoal adsorbent shall be installed.

-   At the dryer outlet, a wire mesh filter of 30 µm shall be installed
    to trap particles of dryer adsorbent.

171. Each gas filter shall be equipped with manual shut-off valves on
     both sides of it to minimize contact with air.

     1.  Measuring points

172. At least the measuring points defined in Table 8 shall implemented
     and be remotely read out by the QPLANT:CIS.

+-----------------------------+----------------------------------------+
| **Parameter**               | **Measurement Location(s)**            |
+=============================+========================================+
| Helium Mass Flow Rate       | -WCS.VLP                               |
|                             |                                        |
|                             | -WCS.LP                                |
|                             |                                        |
|                             | -WCS.HP                                |
+-----------------------------+----------------------------------------+
| Helium Temperatures         | -WCS.VLP                               |
|                             |                                        |
|                             | -WCS.LP                                |
|                             |                                        |
|                             | -WCS.HP                                |
+-----------------------------+----------------------------------------+
| Helium Mass flow rate       | -WCS.VLP                               |
|                             |                                        |
|                             | -WCS.LP                                |
|                             |                                        |
|                             | -WCS.HP                                |
+-----------------------------+----------------------------------------+
| Helium Pressure             | \- Suction of each compressor          |
|                             | (including VLP)\                       |
|                             | - After each oil-retention vessel\     |
|                             | - After the charcoal adsorber and the  |
|                             | dryer                                  |
|                             |                                        |
|                             | \- Each warm storage vessel            |
+-----------------------------+----------------------------------------+
| Differential Pressure       | \- Across each oil filter\             |
|                             | - Across the charcoal adsorber and the |
|                             | dryer                                  |
+-----------------------------+----------------------------------------+
| Moisture                    | \- After the charcoal adsorber\        |
|                             | - Upstream and downstream of the       |
|                             | dryer\                                 |
|                             | - At 2/3 height of the dryer bed       |
+-----------------------------+----------------------------------------+
| Nitrogen Content (for Air   | \- After the charcoal adsorber\        |
| Detection)                  | - After the dryer                      |
+-----------------------------+----------------------------------------+
| Oil Level (Analogue and     | \- In each oil retention vessel        |
| Switches)                   | (analogue and switch)                  |
|                             |                                        |
|                             | \- In the third coalescer (switch)     |
+-----------------------------+----------------------------------------+
| Water flow rate             | \- At the outlet of the coolers        |
+-----------------------------+----------------------------------------+
| Water pressure              | \- At the inlet of the coolers         |
+-----------------------------+----------------------------------------+
| Motor temperature           | \- Each motor                          |
+-----------------------------+----------------------------------------+
| Vibration                   | \- Each Compressor                     |
+-----------------------------+----------------------------------------+
| Operation-hour counters     | \- Each Compressor, oil pumps, other   |
|                             | pumps                                  |
+-----------------------------+----------------------------------------+
| Oil level                   | \- Oil retention vessels and third     |
|                             | coalescer                              |
+-----------------------------+----------------------------------------+
| Oil injection pressure      | \- Each compressor skid                |
+-----------------------------+----------------------------------------+
| Rotational speed            | \- Compressors                         |
+-----------------------------+----------------------------------------+
| Current and voltage         | \- Each motor and compressor           |
+-----------------------------+----------------------------------------+

: []{#_Ref185259881 .anchor}Table 5 Temperature measurement precision

1.  []{#_Toc212194840 .anchor}Refrigeration Cold Box

The Refrigeration Cold Box (QRB) comprises internal and external
components and produces the refrigeration power necessary to achieve the
needs of the cryogenic users. The QRB is coupled to the WCS and
distributes the cryogenic flows to the Cryogenic Distribution System
(QDIST).

1.  General Requirements

    In the offer, the applicant shall provide a preliminary 3D MODEL
    including the terminal points for the QRB-A/B/E/D lines.

<!-- -->

173. The QRB shall be a horizontal cold box to fit with the building
     constraints (see \[AD 2\]).

174. The QRB shall comprise the following internal components:

-   Heat exchangers

-   Turbines

-   Cold Compressors

-   Piping

-   80 K dual bed adsorber

-   20 K single bed adsorber

-   Helium baths at 4.5 K and 2 K

-   Filters

-   Heaters

-   Cryogenic valves

-   Instrumentation

175. The QRB shall comprise the following external components:

-   Vacuum pumping system.

-   Warm panel with warm valves and instrumentation.

-   Piping and valves for purging and conditioning all the circuits.

-   Electrical cabinets.

-   Safety valves.

-   Helium guard circuits.

-   Compressed air distribution.

-   Coolers for turbines.

-   A platform for easy access to all the components located at the
    upper level.

-   Connection port to transfer liquid helium from QRB to external dewar
    or vice versa.

176. The Contractor may employ liquid-nitrogen pre-cooling between 300 K
     and 80 K. If liquid-nitrogen pre-cooling is adopted, the Contractor
     shall supply, integrate, and warrant all associated equipment,
     controls, and interfaces.

     In the offer, the Applicant shall submit a quantified
     techno-economic justification demonstrating overall benefit of the
     liquid-nitrogen pre-cooling. The justification shall, as a minimum,
     include:

-   Capital-cost comparison (EUR).

-   Operating-cost comparison (EUR per year), including liquid-nitrogen
    consumption expressed in kWhₑ

-   Impact on delivery logistics and supply reliability.

177. At least one manual shut-off valve shall be installed on each
     process line connected to the WCS, upstream of the first cryogenic
     isolation device.

     1.  Main components

         1.  Vacuum vessel(s)

178. The vacuum vessel(s) shall be designed for full internal vacuum (0
     bara) and for an external overpressure of minimum 1.5 bar(g) unless
     otherwise justified by the safety study.

179. The design of the passage of every line (cold or warm) connected to
     the QRB shall avoid any condensation or frost formation at the
     interfaces during any operation scenario or any transition between
     operation scenarios.

180. The ports carrying cold valves, turbines, transfer lines
     connections and instrumentation feedthrough shall be fabricated
     from stainless steel. The vacuum vessel(s) may be fabricated from
     mild steel.

181. The design of the pumping ports shall prevent the intake of any
     loose sheets of superinsulation into the vacuum pumps.

182. The QRB shall be equipped with a vacuum barrier at the Cryogenic
     Distribution System interface.

     1.  Helium Heat exchangers

183. Aluminium plate fin heat exchangers shall be vacuum brazed.
     Stainless steel heat exchangers shall be of all-welded
     construction.

184. For all heat exchangers, the type and origin of materials and
     transition pieces (Aluminium-Stainless Steel) shall be provided.

185. All heat exchangers operating below 20 K shall be arranged
     vertically with the warm end at the top.

186. Any heat exchanger between 300 K and 80 K shall facilitate warm up
     and regeneration for frozen water removal in the HP side.

187. The differential pressure between inlet and outlet of any heat
     exchanger shall be measured to monitor the pressure drop evolution
     during operation.

188. In case of 80 K nitrogen pre-cooling, a separated heat exchanger
     between nitrogen and HP helium flow shall be installed to avoid
     solidification of nitrogen in case of return of cold helium flow in
     the LP stream.

     1.  Turbines

189. Turbines with gas lubricated or magnetic bearings shall be
     deployed.

190. The power extracted by the turbines shall be transferred to water
     cooled heat exchangers. Acceptable materials for the water channels
     are stainless steel and copper compatible with the water quality as
     described in 3.7.3.2. The water side shall give easy access for
     cleaning.

191. To allow the easy exchange of turbine cartridges, the system shall
     include all the elements needed to isolate, warm up, purge and cool
     down each turbine individually. This exchange shall be possible in
     situ without warming up heat exchanger blocks.

192. A replacement of one turbine cartridge shall not exceed 3 hours.

     Separate vacuum barrier

     1.  Cold Compressors

Cold compressors may either be in the QRB or located in a dedicated Cold
Box with separate vacuum

193. The compressors shall be centrifugal with active magnetic bearings.

194. The Contactor shall provide the pressure fields showing the
     pressure ratio as a function of the reduced flow for different
     reduced iso-speeds. The stall and choke lines shall be indicated.

195. The mass flow rate of helium shall be easily adjustable via
     rotation speed regulation using Variable Frequency Drive.

196. The rotational speed of the cold compressor shall include at least
     10% speed margin with respect to the maximum value encountered in
     the different operation scenarios.

197. The rotational speed of each cold compressor should allow to be
     lowered down to 30 % of the nominal speed while remaining in the
     operational window.

198. The Contractor shall submit detailed cool-down and start-up
     procedures for each cold compressor as part of deliverable DD #7
     (Operating Manual). The procedures shall be approved by SCK CEN
     before FAT.

199. The cold compressors shall allow inspection, maintenance, and
     exchange. The intervention time including the warm-up and cold
     compressor exchange shall be less than 4 hours.

     1.  Helium phase separators

200. Two helium phase separators shall be installed in the QRB: one at 2
     K pumped by the cold compressors and one at 4.5 K.

201. The helium phase separators shall be sized for all operating
     scenarios.

202. The helium phase separators shall be equipped with electrical
     heaters to adjust the level of liquid helium, to empty from liquid
     helium and to simulate the user heat load during stand-alone
     commissioning and acceptance testing of the QPLANT.

203. A diffuser shall be installed at the inlet of the helium phase
     separators.

     1.  Adsorbers

204. To remove air impurities, two 80 K adsorbers shall be installed
     with an operating temperature below 85 K.

205. The two 80 K adsorbers shall be parallel switchable.

206. Each of the 80K adsorbers shall be sized to purify the full HP
     compressors flow contaminated up to 50 ppm by volume of air.

207. The Contractor shall choose the adsorption/regeneration time of the
     80K adsorbers to guarantee continuous operation.

208. The system shall perform the switching, regeneration, and cool-down
     of the 80 K adsorbers fully automatically. A by-pass between the
     outlet of the switchable 80K adsorbers and the LP line of the QRB
     shall be installed which could be used for helium purification.

209. To remove the remaining impurities of neon and hydrogen, one 20 K
     adsorber operating shall be installed with an operating temperature
     below 25 K.

210. This 20 K adsorber shall be sized to retain impurities of the full
     helium flow contaminated up to 1 ppm by volume of hydrogen and neon
     each, for a duration of at least 200 hours.

211. The system shall perform the regeneration of the 20 K adsorber
     fully automatically.

212. The regeneration and re-cooling of the contaminated 29K adsorber
     shall take less than 12 hours.

213. All adsorbers (80K and 20K) shall be equipped with a full mass flow
     by-pass.

214. The design of the adsorbers shall allow easy access for the
     periodic change of the adsorbent.

215. The design of the adsorbers shall avoid any movement of the
     adsorbent and any emission of dust. The adsorbent material shall be
     chemically and mechanically stable under any operating conditions.

216. All adsorbers shall be equipped with gas analysis ports (§
     3.5.11.3).

     1.  Filters

217. Downstream of each adsorber, a 10 µm wire mesh filter shall be
     installed.

218. Filters of 10 µm retention ability shall be installed at the inlet
     of turbines.

219. The Contractor shall decide the number and positions of any
     additional filters required.

220. All filters shall be accessible from the outside of the vacuum
     vessel for changing, cleaning and purging.

221. All filters shall be designed to prevent dust collected can falling
     into the connected piping during replacement.

     1.  Heaters

222. The Contractor shall install heaters wherever necessary to permit a
     full warm-up of all the circuits, including cryogenic distribution
     and the cryomodules as described in 3.2.3.2. Heaters shall also be
     used to demonstrate the QPLANT performance during the Acceptance
     Tests.

223. The Contractor shall specify the installed heating capacity (kW)
     and physical location of every heater.

224. Heaters and associated electrical wiring shall be designed to
     minimize the heat loads to cold surfaces using necessary
     thermalization and optimized wiring diameters.

     1.  Measuring Points

225. At least the measuring points defined in Table 9 shall implemented
     and be remotely read out by the QPLANT:CIS. They shall be logged at
     a rate ≤ 1 Hz.

[]{#_Ref184110805 .anchor}Table 9 Measuring Points for QRB

+-------------------------+--------------------------------------------+
| **Parameter**           | **Measurement Location(s)**                |
+=========================+============================================+
| Helium mass flow rate   | \- Inlet HP stream of the QRB- Supply SHe  |
|                         | from QRB to LINAC\                         |
|                         | - Coupler mass flow return                 |
+-------------------------+--------------------------------------------+
| Temperatures            | \- Inlets and outlets of the QRB\          |
|                         | - Inlet and outlet of each turbine         |
|                         |                                            |
|                         | \- HP outlet downstream 300 K--80 K        |
|                         | precooling\                                |
|                         | - In each adsorber bed- Liquid helium      |
|                         | baths                                      |
+-------------------------+--------------------------------------------+
| Pressure                | \- Inlets and outlets of the QRB\          |
|                         | - Inlet and outlet of each turbine\        |
|                         | - Outlet of each cold compressor\          |
|                         | - In each adsorber bed\                    |
|                         | - Helium guard circuits (if any)\          |
|                         | - Liquid helium baths- Water cooling       |
|                         | circuit                                    |
+-------------------------+--------------------------------------------+
| Differential pressure   | \- Across each filter or set of parallel   |
|                         | filters\                                   |
|                         | - HP line (300 K--80 K) first heat         |
|                         | exchanger\                                 |
|                         | - Across each adsorber bed (or as pressure |
|                         | at inlet and outlet)                       |
+-------------------------+--------------------------------------------+
| Level measurements      | \- In liquid helium phase separate (2K and |
|                         | 4K)\                                       |
|                         | - In the liquid nitrogen bath (if          |
|                         | applicable)                                |
+-------------------------+--------------------------------------------+
| Moisture                | \- At the inlet of the QRB (HP flow)       |
+-------------------------+--------------------------------------------+
| Nitrogen content for    | \- At 2/3 of the 80 K adsorber beds        |
| air detection           |                                            |
+-------------------------+--------------------------------------------+
| Rotational Speed        | \- Rotational speed of each turbine        |
+-------------------------+--------------------------------------------+
| Vacuum Pressure         | \- QRB vacuum vessel                       |
+-------------------------+--------------------------------------------+
| Electrical Power        | \- Electrical power of installed heaters   |
|                         |                                            |
|                         | \- Electrical Power to Cold Compressors    |
+-------------------------+--------------------------------------------+

: []{#_Ref184046879 .anchor}Table 6 He Leakage requirements (excluding
via permeation and diffusivity)

1.  []{#_Toc212194841 .anchor}Warm Storage Helium

    1.  Overview of System

The Warm Storage Helium (WSH) is a system that provides storage,
buffering, and management of warm helium gas within the QPLANT cryogenic
process. It acts as an intermediate reservoir between the Warm
Compressor Station (WCS), the helium recovery system, and purification
units ensuring stable operation during start-up, shutdown, transient
modes and maintenance. The WSH allows for pressure balancing, helium
inventory control, and gas recovery under all operating conditions,
thereby maintaining system integrity and operational efficiency (see
Figure 8).

![](media/image12.emf){width="3.7297287839020123in"
height="3.4013221784776904in"}

The Warm Storage Helium (WSH) consists of:

-   Helium storage vessels (Contingent Part 2)

-   Associated infrastructure (support structures, cat ladders, ....),
    Contingent Part 2.

-   Interconnecting piping between these vessels and the WCS (WCS.LP,
    WCS.HP)

-   Interconnecting piping to dedicated recovery system and/or
    purification system (if applicable)

-   Associated instrumentation, valves, and control equipment.

-   Make-up line to external gaseous helium delivery

    1.  Scope and Contingency Definition

This Contingent Part 2 covers the supply and installation of the helium
storage vessels and their associated infrastructure on the SCK CEN site.
The Fixed scope of the Contract covers all the remaining
parts/activities.

2.  General WSH requirements

<!-- -->

226. The WSH shall be dimensioned to store the full helium inventory
     plus 20 % margin.

227. The WSH shall be divided into a minimum of three (3) helium storage
     vessels to ensure operational flexibility, maintainability, and
     robustness during cyclic operation or partial unavailability of
     vessels.

228. The set pressure (PS) of the WSH relief devices shall be ≥ the
     maximum operating pressure of the HP header and ≤ the MAWP of the
     WSH vessels.

229. The helium storage vessels shall be installed outdoors and oriented
     vertically to minimise footprint in accordance with \[AD 2\]. The
     final layout, volumes, and positioning shall be proposed by the
     Contractor and validated by SCK CEN during the conceptual design
     phase.

230. Each helium storage vessel shall include at least one inspection
     manhole to permit internal access for periodic inspection.

231. The Contractor shall prepare a technical specification for the
     helium storage vessels as per \[AD 14\] covering surface cleaning,
     corrosion protection, inner-surface treatment (e.g., Rustol/Owatrol
     or equivalent), outer-surface coating,

232. Each vessel shall be fitted with valves and ports required for
     purging, conditioning, and gas analysis.

233. The storage vessels shall be interconnected by valves and connected
     to both the LP and HP sides of the WCS via automatic valves to
     regulate process pressures.

234. A gas-management warm panel for controlling the helium storage
     vessel valves shall be integrated into the main control panel of
     the WCS. This panel shall allow local operation of valve switching,
     isolation, and vessel selection functions associated with the
     helium storage system.

235. At least the measuring points defined in Table 10 shall implemented
     and be remotely read out by the QPLANT:CIS. Each vessel shall also
     be equipped with a local pressure indicator

+------------------------+---------------------------------------------+
| **Parameter**          | **Measurement Location(s)**                 |
+========================+=============================================+
| Temperatures           | Temperature of at least one storage vessel  |
+------------------------+---------------------------------------------+
| Pressure               | Helium pressure in each installed helium    |
|                        | storage vessel                              |
|                        |                                             |
|                        | Helium pressure in the common manifolds     |
+------------------------+---------------------------------------------+
| Impurity measurements  | Pick-ups and capillaries shall be provided  |
|                        | for measuring moisture and nitrogen         |
|                        | contents in each vessel                     |
+------------------------+---------------------------------------------+
| Local indicative       | Helium pressure indicator for each          |
| measuring points       | installed vessel                            |
+------------------------+---------------------------------------------+

1.  Scope boundary between Fixed and Contingent part

<!-- -->

236. Even if this contingent part is not exercised, the Contractor shall
     execute:

-   Preparation of functional and technical specifications for the
    storage vessels (e.g.: volume, flanges, instrumentation ports,
    dimensions, surface treatment, ...).

-   Physical and functional integration of the helium storage vessels
    within WSH

-   Definition of instrumentation and remote read-out points

-   Supply and Installation of all instrumentation on the vessel

-   Piping, valves, and valve logic between the helium storage vessels
    (and any other WSH interface points) and the WCS

-   Overall system and control integration within the WCS control logic

-   Provision of all physical connections to the vessel interfaces,
    irrespective of the contingent assignment.

237. If Contingent Part 2 is exercised, the Contractor shall also:

-   be fully responsible for the design and mechanical verification of
    the helium storage vessels.

-   submit the mechanical support design data and vessel interface loads
    as part of the detailed design deliverables.
