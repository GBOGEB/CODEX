SCK CEN Ref.:

Addendum II - Cryoplant Technical Requirements

Technical Specifications and Project Requirement

Tender reference: 2024-106-IVE

© SCK CEN - Stichting van Openbaar Nut -- Fondation d\'Utilité Publique
‐ Foundation of Public Utility\
**Registered Office:** Avenue Herrmann Debroux 40 -- BE‐1160 BRUSSEL\
**Research Centres:**

Boeretang 200 - 2400 MOL -- Belgium

Chemin du Cyclotron 6 - 1348 Ottignies-Louvain-la-Neuve -- Belgium

[www.sckcen.be](http://www.sckcen.be)

Copyright Rules

All property rights and copyright are reserved to SCK CEN. In case of a
contractual arrangement with SCK CEN, the use of this information by a
Third Party, or for any purpose other than for which it is intended
based on the contract, is not authorized. With respect to any
unauthorized use, SCK CEN makes no representation or warranty, expressed
or implied, and assumes no liability as to the completeness, accuracy or
usefulness of the information contained in this document, or that its
use may not infringe privately owned rights.

![](media/image1.png){width="6.600745844269467in"
height="1.4260870516185478in"}

# Table of Contents {#table-of-contents .TOC-Heading}

[I.1 Abbreviations [5](#abbreviations)](#abbreviations)

[I.2 Terms and Definitions
[6](#terms-and-definitions)](#terms-and-definitions)

[I.3 Table of Figures [9](#table-of-figures)](#table-of-figures)

[I.4 Table of Tables [10](#table-of-tables)](#table-of-tables)

[1 Introduction [12](#_Toc200491758)](#_Toc200491758)

[1.1 The LINAC [12](#_Toc188541027)](#_Toc188541027)

[1.2 Cryogenic System [12](#_Toc188541028)](#_Toc188541028)

[1.3 Cryogenic Users [13](#_Toc200491761)](#_Toc200491761)

[1.4 Overview of the He lines [14](#_Toc212194815)](#_Toc212194815)

[1.5 Introduction to QPLANT Control & Interlock System, CIS services and
infrastructure. [16](#_Toc200491763)](#_Toc200491763)

[2 Nature of the Procurement [17](#_Toc200491764)](#_Toc200491764)

[2.1 Scope of Work by the Contractor
[17](#_Toc200491765)](#_Toc200491765)

[2.2 Scope of Supply by the Contractor
[17](#_Toc200491766)](#_Toc200491766)

[3 Technical Requirements [18](#_Toc200491767)](#_Toc200491767)

[3.1 Introduction [18](#_Toc212194821)](#_Toc212194821)

[3.2 Nominal Operational Scenarios [19](#_Toc192335394)](#_Toc192335394)

[3.2.1 Lifetime and annual maintenance schedule
[19](#_Toc192496488)](#_Toc192496488)

[3.2.2 Steady state operational scenarios
[19](#_Toc200491776)](#_Toc200491776)

[3.2.3 Transient operational scenarios
[19](#_Ref192411691)](#_Ref192411691)

[3.2.4 Other operational scenarios [21](#_Toc200491791)](#_Toc200491791)

[3.3 Performance Requirements [22](#_Toc202536091)](#_Toc202536091)

[3.4 Reliability Requirements [23](#_Toc202536092)](#_Toc202536092)

[3.5 QPLANT Design & Construction Requirements
[23](#_Toc200491815)](#_Toc200491815)

[3.5.1 Units [23](#_Toc212194830)](#_Toc212194830)

[3.5.2 3D Model [24](#_Toc212194831)](#_Toc212194831)

[3.5.3 Energy-efficiency [24](#_Toc212194832)](#_Toc212194832)

[3.5.4 General Electrical Requirements
[24](#_Toc200491995)](#_Toc200491995)

[3.5.5 Design, Materials [25](#_Toc212194834)](#_Toc212194834)

[3.5.6 Welding [29](#_Toc212194835)](#_Toc212194835)

[3.5.7 Machine Protection [30](#_Toc212194836)](#_Toc212194836)

[3.5.8 Purging [30](#_Toc200491892)](#_Toc200491892)

[3.5.9 Helium Inventory management [30](#_Toc200491898)](#_Toc200491898)

[3.5.10 Warm Compressor Station [32](#_Toc200491990)](#_Toc200491990)

[3.5.11 Refrigeration Cold Box [36](#_Toc212194840)](#_Toc212194840)

[3.5.12 Warm Storage Helium [40](#_Toc212194841)](#_Toc212194841)

[3.6 QPLANT Control System [42](#_Toc212194842)](#_Toc212194842)

[3.6.1 Overview [42](#_Toc200492240)](#_Toc200492240)

[3.6.2 Reference Architecture [42](#_Toc200492241)](#_Toc200492241)

[3.6.3 Architecture, Autonomy, and Scope
[43](#_Toc212194845)](#_Toc212194845)

[3.6.4 Test System for Functional Verification
[44](#_Toc202536179)](#_Toc202536179)

[3.6.5 Digital Process Model [44](#_Toc202536180)](#_Toc202536180)

[3.6.6 Cryogenic System Control and MCS Integration
[44](#_Toc202536182)](#_Toc202536182)

[3.6.7 General Software and Hardware Requirements
[44](#_Toc200492260)](#_Toc200492260)

[3.6.8 Software development [45](#_Toc200492268)](#_Toc200492268)

[3.6.9 Software Change Management [46](#_Toc200492279)](#_Toc200492279)

[3.6.10 Human Machine Interface (HMI)
[47](#_Toc200492292)](#_Toc200492292)

[3.6.11 Migration to Newer Hardware
[48](#_Toc212194853)](#_Toc212194853)

[3.6.12 Network [49](#_Toc200492316)](#_Toc200492316)

[3.7 Interfaces [51](#_Ref190799769)](#_Ref190799769)

[3.7.1 Process Line interface [52](#_Toc212194856)](#_Toc212194856)

[3.7.2 Interfaces with the site [55](#_Ref190781343)](#_Ref190781343)

[Figure 2 [55](#_Toc212194858)](#_Toc212194858)

[3.7.3 Interface with support systems (utilities)
[56](#_Toc212194859)](#_Toc212194859)

[3.7.4 Interfaces with the Vacuum System
[59](#_Toc200492407)](#_Toc200492407)

[3.7.5 Interface with LHe (ad-hoc) user and associated helium recovery
[59](#_Toc200492411)](#_Toc200492411)

[3.7.6 Liquid Nitrogen (LN2) [61](#_Toc200492412)](#_Toc200492412)

[3.7.7 Interfaces with (external) Control System
[61](#_Toc212194863)](#_Toc212194863)

[3.8 Factory Testing [62](#_Toc200492436)](#_Toc200492436)

[3.8.1 Welding, pressure, and leak tests
[62](#_Toc200492437)](#_Toc200492437)

[3.8.2 Tests of components [62](#_Toc192183302)](#_Toc192183302)

[3.8.3 Electrical, wiring and control system tests
[62](#_Toc200492447)](#_Toc200492447)

[3.8.4 Transport and Storage [63](#_Toc200492460)](#_Toc200492460)

[3.9 Inspection and Installation [63](#_Toc200492466)](#_Toc200492466)

[3.9.1 Incoming inspection at SCK CEN site
[64](#_Toc200492472)](#_Toc200492472)

[3.9.2 Test after Mechanical assembly completion
[64](#_Toc200492479)](#_Toc200492479)

[3.10 Commissioning [64](#_Toc200492489)](#_Toc200492489)

[3.10.1 Tests to be done during Standalone Commissioning
[65](#_Toc200492490)](#_Toc200492490)

[3.11 Site Acceptance testing [65](#_Toc200492507)](#_Toc200492507)

[3.11.1 General [65](#_Toc192762740)](#_Toc192762740)

[3.11.2 WCS functional tests [65](#_Toc200492517)](#_Toc200492517)

[3.11.3 WCS capacity tests [66](#_Toc200492524)](#_Toc200492524)

[3.11.4 QPLANT functional tests [66](#_Toc200492535)](#_Toc200492535)

[3.11.5 QPLANT capacity tests [67](#_Toc200492547)](#_Toc200492547)

[3.11.6 Thermal Shield stand-by [67](#_Toc200492561)](#_Toc200492561)

[3.11.7 Cold stand-by [67](#_Toc200492567)](#_Toc200492567)

[3.11.8 2 K Operation [68](#_Toc200492574)](#_Toc200492574)

[3.11.9 QPLANT transition tests [68](#_Toc200492581)](#_Toc200492581)

[3.12 Spare Parts [68](#_Ref190800689)](#_Ref190800689)

[3.13 After-sales Services [69](#_Ref201310545)](#_Ref201310545)

[3.13.1 Level Agreement (Option 3) [69](#_Toc202536241)](#_Toc202536241)

[3.13.2 Lifetime After-sales Services (applicable when Option 3 is
exercised) [69](#_Toc202536242)](#_Toc202536242)

[3.14 Documentation [70](#_Toc200492592)](#_Toc200492592)

[4 Reliability Centred Maintenance & Lifecycle Cost Management
[73](#_Toc196376043)](#_Toc196376043)

[5 Safety, Codes and Standards [74](#_Toc200492611)](#_Toc200492611)

[5.1 Safety [74](#_Toc200492612)](#_Toc200492612)

[5.1.1 Hazard definitions and typical mitigation devices
[74](#_Toc212194892)](#_Toc212194892)

[5.1.2 ODH Monitoring Architecture and Responsibilities
[74](#_Toc212194893)](#_Toc212194893)

[5.2 Codes and Standards [76](#_Toc200492614)](#_Toc200492614)

[5.2.1 Electromagnetic interference
[77](#_Toc212194895)](#_Toc212194895)

[5.2.2 Pressure Equipment & Safety [77](#_Toc212194896)](#_Toc212194896)

[5.2.3 Functional Safety & Control [77](#_Toc200492636)](#_Toc200492636)

[5.2.4 Asset & Maintenance Management
[78](#_Toc200492637)](#_Toc200492637)

[5.2.5 Cleanliness & Purity [78](#_Toc200492638)](#_Toc200492638)

[5.2.6 Proof‑Test & Control‑Phase Requirements
[78](#_Toc200492639)](#_Toc200492639)

[6 Schedule [79](#_Toc200492642)](#_Toc200492642)

[6.1 Contractual Phases [79](#_Toc191379864)](#_Toc191379864)

[6.2 Preliminary Schedule [80](#_Ref192661306)](#_Ref192661306)

[6.3 Hold and Witness Points [81](#_Toc192762835)](#_Toc192762835)

[7 Contract Performance [82](#_Toc200492646)](#_Toc200492646)

[7.1 General Organization [82](#_Toc191379878)](#_Toc191379878)

[7.2 Communication [82](#_Toc200492648)](#_Toc200492648)

[7.3 Contract Management [82](#_Toc200492649)](#_Toc200492649)

[7.3.1 Progress Dashboard [82](#_Toc200492650)](#_Toc200492650)

[7.3.2 Meetings [83](#_Toc200492651)](#_Toc200492651)

[7.4 Risk Assessment and Risk Management Plan
[84](#_Toc200492655)](#_Toc200492655)

[7.5 Factory Access [84](#_Toc200492656)](#_Toc200492656)

[8 Quality Assurance and Control [85](#_Ref190802856)](#_Ref190802856)

[8.1 Quality Assurance [85](#_Toc200492658)](#_Toc200492658)

[8.1.1 General requirements [85](#_Toc200492659)](#_Toc200492659)

[8.1.2 Quality Management System [85](#_Toc200492660)](#_Toc200492660)

[8.1.3 Quality Assurance Program [85](#_Toc200492661)](#_Toc200492661)

[8.1.4 Qualification of personnel [85](#_Toc200492662)](#_Toc200492662)

[8.1.5 Document Retention and Submission Requirements
[85](#_Toc202536276)](#_Toc202536276)

[8.1.6 OEM Documentation [86](#_Toc212194920)](#_Toc212194920)

[8.1.7 Change Management [86](#_Toc200492678)](#_Toc200492678)

[8.1.8 Non-Conformity Management [87](#_Ref190802525)](#_Ref190802525)

[8.1.9 Audits [88](#_Toc160432906)](#_Toc160432906)

[8.2 Quality Control [88](#_Toc200492681)](#_Toc200492681)

[8.2.1 General requirements [88](#_Toc200492682)](#_Toc200492682)

[8.2.2 Manufacturing and Inspection Plan
[89](#_Toc200492683)](#_Toc200492683)

[8.2.3 Declaration of conformity with all requirements
[89](#_Toc192782715)](#_Toc192782715)

[8.3 Acceptance Tests [89](#_Toc200492685)](#_Toc200492685)

[8.3.1 General Requirements [89](#_Toc192762987)](#_Toc192762987)

[8.3.2 Factory Acceptance Test (FAT)
[90](#_Ref195080116)](#_Ref195080116)

[8.3.3 Site Acceptance Tests [90](#_Toc200492688)](#_Toc200492688)

[8.3.4 Acceptance and Warranty [90](#_Toc192765565)](#_Toc192765565)

[8.4 Final acceptance [91](#_Toc202536294)](#_Toc202536294)

[9 Appendix [92](#_Toc200492694)](#_Toc200492694)

[9.1 Cooling Power for Cool-down [92](#_Ref190769672)](#_Ref190769672)

[9.1.1 Simplified cooling model [92](#_Toc212194936)](#_Toc212194936)

[9.1.2 System Mass Summary [92](#_Toc212194937)](#_Toc212194937)

[9.1.3 Static heat load as a function of temperature
[93](#_Toc212194938)](#_Toc212194938)

[9.1.4 Enthalpy data of metal at various temperatures
[93](#_Toc212194939)](#_Toc212194939)

[9.2 Control Systems [94](#_Toc212194940)](#_Toc212194940)

[9.2.1 Instructions for GQRC [94](#_Toc212194941)](#_Toc212194941)

[9.2.2 Control Architecture details
[95](#_Ref212036407)](#_Ref212036407)

[10 Applicable Documents [98](#_Toc212194943)](#_Toc212194943)

## Abbreviations

  --------------------------------------------------------------------------
  ACC NF       Accelerator Nuclear Facilities (buildings and utilities)
  ------------ -------------------------------------------------------------
  AD           Applicable Documents

  AH           Atmospheric Heat exchanger

  BSL          Baseline

  CAV          Cavity

  CCB          Cryogenic Compressor Building

  CEA          French Alternative Energies and Atomic Energy Commission

  CIS          Control and Interlock system

  COTS         Commercial Off-The-Shelf, see also OEM

  CSS          Cryogenic Supply System (QPLANT+QINFRA+QDIST)

  CV           Control Valve

  DD           Documentation Deliverables

  DIS          Device Interlock System (part of MIS)

  DSBT         Low Temperature Systems Department

  EH           Electrical Heater

  FAT          Factory Acceptance Test

  FMECA        Failure mode, effects, and criticality analysis

  FT           Fault Tolerance

  GHe          Gaseous Helium

  HAZOP        HAZard and OPerability

  He           Helium

  HMI          Human Machine Interface

  HP           High Pressure (typically 15 bar for WCS-HP)

  HVAC         Heating, Ventilation and Air Conditioning

  HV           Hand Valve

  HX           Heat Exchanger

  KOM          Kick-Off Meeting

  LHe          Liquid Helium

  LINAC        Linear Accelerator

  LN~2~        Liquid Nitrogen

  LP           Low Pressure (Typically 1050 mbar)

  LRU          Line Replaceable Unit (used with RCM and MTBF data)

  LTU          LINAC Tunnel

  LWC          Low Pressure Warm Compressor

  MCS          Control System

  MIP          Manufacturing and Inspection Plan

  MIS          Interlocking System

  MIT          IT System

  MTBF         Mean Time Between Failure

  MTBM         Mean Time Between Maintenance

  MTTR         Mean Time To Repair

  MYRRHA       Multi-purpose hYbrid Research Reactor for High-tech
               Applications

  OEM          Original Equipment Manufacturer. (e.g. Kaeser)

  ORS          Oil removal system

  PEPS         Personal Protection System

  PFD          Process Flow Diagram

  PID          Piping and Instrumentation Diagram

  PLC          Programmable Logic Controller

  QCELL        Cryogenic Cell = QVB+QM

  QLM          Main Cryogenic Distribution Line

  QM           Cryomodule

  QPLANT       QPLANT

  QPLANT:CIS   QPLANT Control and Interlock System

  QRB          QPLANT Refrigeration Cold Box

  QSYS         Cryogenic System

  QSYS:CS      Cryogenic Control System

  QVB          Cryogenic Valve Box

  QVE          End-box

  RAMI         Reliability, Availability, Maintainability, Inspectability.

  RF           Radio Frequency

  SAT          Site Acceptance Test

  SC           Superconducting

  SHe          Supercritical Helium

  SSC          Structures Systems and Components

  ST           Storage

  SV           Safety Valve

  TRO          Technical Responsible Officer

  TRM          Technical Review Meeting

  TS           Thermal Shields

  Tu           Turbo Expander

  UPS          Uninterruptible Power Supply

  VLP          Very Low Pressure (Typically 27-31 mbar for QRB-B and
               \~400-450 mbar for WCS-VLP)

  WCS          Warm Compressor Station

  WSH          Warm Storage Helium
  --------------------------------------------------------------------------

  : []{#_Toc212194944 .anchor}Figure 1 Overall layout of the Cryogenic
  System

## Terms and Definitions

+------------+---------------------------------------------------------+
| Conceptual | A preliminary engineering framework that defines the    |
| Process    | cryogenic helium refrigeration architecture, supporting |
| Proposal   | a range of operational and functional requirements. The |
|            | Conceptual Process Proposal serves as the foundation    |
|            | for subsequent design stages by detailing the system    |
|            | architecture, proposed configurations, and functional   |
|            | decompositions necessary to meet the overarching System |
|            | Requirements. It ensures integration of key subsystems  |
|            | and process units while maintaining compliance with     |
|            | operational constraints, safety margins, and            |
|            | performance criteria. It is reviewed and validated as a |
|            | baseline for the Detailed Design phases                 |
+============+=========================================================+
| CoreShare  | SCK CEN's document management system                    |
+------------+---------------------------------------------------------+
| (Inverse)  | COP: A dimensionless indicator of the energy efficiency |
| C          | of refrigeration, representing the ratio of useful      |
| oefficient | thermal energy delivered to the electrical energy       |
| of         | consumed. In cryogenic applications,                    |
| P          |                                                         |
| erformance | COP refers specifically to the amount of cooling power  |
|            | generated at cryogenic temperatures per unit of         |
|            | electrical input.                                       |
|            |                                                         |
|            | Defined as:                                             |
|            |                                                         |
|            | COP_cryogenic = Q_cooling / P_input                     |
|            |                                                         |
|            | where:                                                  |
|            |                                                         |
|            | Q_cooling = Net cooling power at cryogenic temperature  |
|            | \[W\]                                                   |
|            |                                                         |
|            | P_input = Total input power.                            |
|            |                                                         |
|            | Inverse Coefficient of Performance (invCOP):            |
|            |                                                         |
|            | A measure of specific power consumption in              |
|            | refrigeration systems, defined as the amount of input   |
|            | electrical energy required to produce one unit of       |
|            | cooling at the specified cryogenic temperature.         |
|            |                                                         |
|            | Commonly expressed in W/W (e.g., W per W of cooling at  |
|            | 4.5 K). Lower values indicate higher efficiency.        |
|            |                                                         |
|            | Defined as:                                             |
|            |                                                         |
|            | invCOP_cryogenic = P_input / Q_cooling = 1 /            |
|            | COP_cryogenic                                           |
+------------+---------------------------------------------------------+
| Design     | +----------------------------------------------------+  |
| Stage(s) / | | A self-contained phase within the engineering      |  |
| Project    | | design process, each focusing on a distinct level  |  |
| Execution  | | of technical maturity and output deliverables.     |  |
| Stages     | | Design Stages are sequenced to transform user      |  |
|            | | requirements into realizable system configurations |  |
|            | | through increasing levels of fidelity and          |  |
|            | | validation.\                                       |  |
|            | | \                                                  |  |
|            | | Conceptual Design Phase: A phase in the design     |  |
|            | | process that involves evaluating multiple concepts |  |
|            | | to determine their ability to fulfil the defined   |  |
|            | | fit-for-purpose requirements. It includes the      |  |
|            | | identification and justification of a reference    |  |
|            | | concept deemed the most suitable and feasible      |  |
|            | | within the specified constraints. The Conceptual   |  |
|            | | Design provides a general understanding of the     |  |
|            | | system\'s intended purpose, overall structure,     |  |
|            | | operating principles, physical dimensions, and key |  |
|            | | technical specifications. Once reviewed and        |  |
|            | | approved, the Conceptual Design serves as the      |  |
|            | | foundation for the development of the Detailed     |  |
|            | | Design.                                            |  |
|            | |                                                    |  |
|            | | Detailed Design Phase: This stage develops the     |  |
|            | | finalized and exhaustive Design Documentation      |  |
|            | | required for fabrication, inspection, testing,     |  |
|            | | installation, commissioning, operation,            |  |
|            | | maintenance, refurbishment, and decommissioning of |  |
|            | | the System. Documentation must meet quality,       |  |
|            | | regulatory, and lifecycle expectations.            |  |
|            | +====================================================+  |
|            | +----------------------------------------------------+  |
|            |                                                         |
|            | : []{#_Ref195702885 .anchor}Figure 3 Simplified         |
|            | interface diagram of the QPLANT depicting a single      |
|            | representative 'QCELL' (inside grey dotted line) as a   |
|            | proxy for all heat load sources. Temperatures shown are |
|            | indicative of the 2 K operating scenario.               |
+------------+---------------------------------------------------------+
| Digital    | The software model (transient or steady-state)          |
| Process    | representing cryogenic behavior; may form part of or    |
| Model      | interface with the Test System.                         |
+------------+---------------------------------------------------------+
| Digital    | A full-scope, continuously synchronized digital         |
| Twin       | representation of the QPLANT; not mandatory.            |
+------------+---------------------------------------------------------+
| Functional | A structured, traceable document defining functional    |
| Test Plan  | verification for each System Under Test (SUT) and its   |
| (FTP)      | Control and Interlock System (SUT:CIS). It shall        |
|            | specify test cases, inputs, interfaces, control         |
|            | sequences, monitoring logic, and acceptance criteria to |
|            | demonstrate compliance with the stated requirements     |
+------------+---------------------------------------------------------+
| Hold Point | A mandatory verification point beyond which work cannot |
|            | continue without approval by SCK CEN. The work can only |
|            | continue provided that SCK CEN has been able to verify  |
|            | the quality of the work completed so far and has        |
|            | confirmed its approval of such work in writing.         |
+------------+---------------------------------------------------------+
| Lifecycle  | The cost optimization approach used during the          |
| Cost       | post-commissioning phase to manage preventive           |
| Management | maintenance, replacement strategy, and reliability      |
|            | targets. It is supported by failure forecasting,        |
|            | risk-based planning, and system performance modelling   |
|            | to maintain or reduce lifetime cost without             |
|            | compromising function.                                  |
+------------+---------------------------------------------------------+
| LOOP event | Loss Of Offsite Power is event characterized by the     |
|            | loss of external electrical supply to the QPLANT.       |
+------------+---------------------------------------------------------+
| Maximum    | It is defined in PED (2014/68/EU) as the maximum        |
| Allowable  | pressure for which equipment is designed.               |
| Pressure   |                                                         |
+------------+---------------------------------------------------------+
| Noise      | Noise Measurement (general). Unless stated otherwise,   |
| M          | all sound levels are A-weighted and expressed in dB(A), |
| easurement | measured at 1 m from the equipment envelope at          |
|            | approximately 1.5 m microphone height, under free-field |
|            | over a reflecting plane conditions, using a Class 1     |
|            | sound level meter (IEC 61672). Background noise shall   |
|            | be at least 10 dB below measured levels or corrected    |
|            | per the test standard. "Compressor (unit)" means an     |
|            | individual compressor with its motor/drive. "Complete   |
|            | skid" means the full assembly with all compressors and  |
|            | drives operating.                                       |
+------------+---------------------------------------------------------+
| Operating  | Expected maximum pressure (including safety relief from |
| Pressure   | passive or active systems) in any operational scenario, |
|            | including startup, shutdown, or transient conditions.   |
+------------+---------------------------------------------------------+
| R          | A systematic and structured process to determine the    |
| eliability | most effective maintenance approach for an asset or     |
| Centred    | system. RCM seeks to ensure that systems continue to do |
| M          | what their users require in their current operating     |
| aintenance | context. It involves identifying failure modes,         |
|            | assessing their consequences, and selecting             |
|            | initiative-taking maintenance tasks to mitigate risk    |
|            | while optimizing cost, safety, and system availability. |
+------------+---------------------------------------------------------+
| Risk       | A formal tool used to systematically document, track,   |
| Register   | and manage risks throughout a project, with the primary |
|            | purposes of risk identification, assessment, treatment, |
|            | monitoring, and communication.                          |
+------------+---------------------------------------------------------+
| Set        | Defined in API 520 as the pressure at which safety      |
| Pressure   | valves are set to open (typically ≥10 % above Operating |
|            | Pressure).                                              |
+------------+---------------------------------------------------------+
| Shut-off   | A shut-off valve is a valve that is automatically       |
| Valve      | actuated (e.g., electrically, pneumatically, or         |
|            | hydraulically) and triggered by a process or safety     |
|            | interlock event. It is intended to isolate helium flow  |
|            | in response to defined conditions such as emergency     |
|            | shutdown, overpressure, or equipment trip. It differs   |
|            | from a manual isolation valve, which is operated only   |
|            | by human intervention. Shut-off valves are designed to  |
|            | fail-safe and to maintain full functionality across     |
|            | repeated cycles between ambient and cryogenic           |
|            | conditions.                                             |
+------------+---------------------------------------------------------+
| System     | The actual system being verified (e.g. QPLANT or        |
| Under Test | QPLANT:CIS)                                             |
| (SUT)      |                                                         |
+------------+---------------------------------------------------------+
| Test       | The digital and/or physical platform used to validate   |
| System     | the SUT during commissioning; it replicates control     |
|            | logic, I/O response, and process dynamics and may       |
|            | include a digital process model (transient simulation   |
|            | or digital twin).                                       |
+------------+---------------------------------------------------------+
| Terminal   | A physical interface with SCK CEN infrastructure,       |
| Point      | specifically ACC NF.                                    |
+------------+---------------------------------------------------------+
| Validation | Ensures that the right product is built, confirming     |
|            | that the system meets the needs and expectations of the |
|            | end-users or stakeholders.                              |
|            |                                                         |
|            | Occur after verification processes, typically at the    |
|            | end of a development phase or project. Validation       |
|            | involves evaluating the final product to ensure it      |
|            | meets the needs of the intended end-user or customer.   |
+------------+---------------------------------------------------------+
| Ve         | Confirms that the product is built correctly according  |
| rification | to the specified requirements, ensuring compliance with |
|            | regulations and specifications.                         |
|            |                                                         |
|            | Conducted throughout the development lifecycle,         |
|            | including during production or development phases.      |
|            | These activities involve reviews, inspections, and      |
|            | testing to ensure compliance with specifications.       |
+------------+---------------------------------------------------------+
| Warm       | Composed of LP to HP and VLP to LP compressors, the Oil |
| Compressor | Removal System, the gas management panel, and the       |
| Station    | necessary electrical cabinets.                          |
+------------+---------------------------------------------------------+
| Witness    | A point in the process where SCK CEN will verify the    |
| Point      | quality of the work completed. However, the work may    |
|            | continue meanwhile.                                     |
+------------+---------------------------------------------------------+

: []{#_Ref190681166 .anchor}Figure 2 View of the buildings related to
the QPLANT.

## Table of Figures

Figure 1 Overall layout of the Cryogenic System [12](#_Toc212194944)

Figure 2 View of the buildings related to the QPLANT.
[13](#_Ref190681166)

Figure 3 Simplified interface diagram of the QPLANT depicting a single
representative 'QCELL' (inside grey dotted line) as a proxy for all heat
load sources. Temperatures shown are indicative of the 2 K operating
scenario. [14](#_Ref195702885)

Figure 4 QPLANT's simplified Process Flow Diagram [15](#_Ref209530150)

Figure 5 QPLANT - Control and Interlock related systems
[16](#_Ref200099216)

Figure 6 Operational scenarios and transitions for the Cryogenic System.
Blue boxes indicate steady states while light blue boxes indicate
transients [20](#_Ref211437030)

Figure 7 Direct Drive [33](#_Toc212194950)

Figure 8 WSH with Contingent Part 2 (area covered in purple dotted line)
[40](#_Ref212186204)

Figure 9 Reference Architecture of the Cryogenic Control System
[43](#_Ref210826960)

Figure 10 Software Change Management [46](#_Ref211261592)

Figure 11 MIT Reference Architecture [49](#_Ref211429607)

Figure 12 Preliminary arrangement of the pipes in the QLM - see Table 12
for details [53](#_Ref184114765)

Figure 13 Routing of QRB.EUR (External User Recovery)
[60](#_Toc212194956)

Figure 14 Simplified cooling model [92](#_Toc190680905)



1.  []{#_Toc200491758 .anchor}Introduction

"Phase 1 -- Implementation" of the MYRRHA program focuses on the design,
construction, and commissioning of a 4 mA 100 MeV super-conducting CW
proton Linear Accelerator (LINAC), a Proton Target Facility (PTF) and a
Full Power Facility (FPF). (Phase 2 of the MYRRHA program will be the
extension to 600 MeV). Further information about MYRRHA Phase I is
provided in reference \[AD3\].

1.  []{#_Toc188541027 .anchor}The LINAC

The \~160 m long LINAC consists of a normal conducting injector followed
by a superconducting section. The latter section accelerates protons
from 17 to 100 MeV using 352.2 MHz single-spoke cavities operating at 2
K. Each Cavity (CAV) is submerged in saturated superfluid helium (He II)
within Helium Tanks (HT), organized into pairs inside a Cryomodule (QM).
Each QM is connected to a dedicated Cryogenic Valve Box (QVB). The
combination of one QM and one QVB is called a Cryo-Cell (QCELL). The
full LINAC configuration will comprise sixty CAVs in thirty QMs. Initial
deployment includes twenty-four QMs: the remaining six to be added
later.

2.  []{#_Toc188541028 .anchor}Cryogenic System

The Cryoplant (QPLANT), a subsystem of the Cryogenic System (**Error!
Reference source not found.**), is designed to provide refrigeration to
QMs via the Cryogenic Distribution System (QDIST).

![](media/image3.emf){width="6.763888888888889in"
height="4.129166666666666in"}

QDIST comprises the QLM, the string of QVBs, and the QVE. The QLM houses
the main headers distributing cold helium at multiple temperature
levels. Each QCELL regulates its helium mass flow by tapping from and
returning to the distribution headers. Excess flow is bypassed through
the QVE.

The QPLANT is distributed over different areas as shown in Figure 2:

-   Compressor Room: Location of the Warm Compression Station (WCS)

-   Storage Area (outside): Location of the helium storage vessels and
    (if needed) liquid nitrogen storage vessels.

-   Cold Box Room: Location of the QRB with the associated warm panel.

-   Connecting rooms: The Warm lines from the WCS to the QRB cross
    multiple other rooms.

    ![](media/image4.png){width="6.496062992125984in"
    height="2.6023622047244093in"}

    1.  []{#_Toc200491761 .anchor}Cryogenic Users

The Cryogenic Users (QCELL), as illustrated in Figure 3, interface with
the QPLANT through a common set of designated helium process lines: A,
B, D, E, and W. The W-line is a warm (300 K) helium return line from the
QCELL.

The Thermal Shield (TS) cooling presents a static heat load, regardless
of the operational scenarios (2 K or otherwise). The TS system utilizes
high-pressure helium with a supply temperature of \~40 K and return
temperature of \~60 K, forming a closed, passive thermal circuit that
ensures radiation shielding and temperature stabilization

Each QCELL includes a 600 W heater in its 2 K tank. These heaters
support warm-up operations by evaporating residual liquid helium
(isothermal phase) and increasing the enthalpy of the cold mass
(reheating structural material)

![](media/image6.svg){width="4.795602580927384in" height="2.4375in"}

2.  []{#_Toc212194815 .anchor}Overview of the He lines

The QPLANT includes a WCS connected to helium storage vessels, a Cold
Box for refrigeration processes, and process equipment for drying, oil
removal, gas management, and purification. An indicative Process Flow
Diagram of the QPLANT is shown in Figure 4 with Table 1 providing
descriptive details of the main interfacing and transport lines.

  ----------------------------------------------------------------------------------
  **Family**     **Constituents**   **Functional role**     **Participation in
                                                            cryogenic cycle**
  -------------- ------------------ ----------------------- ------------------------
  **Cryogenic    QRB.A, QRB.B,      Deliver 4.5 K SHE,      Yes -- core
  distribution   QRB.D, QRB.E       return 2 K vapor, and   refrigeration circuits.
  lines**                           supply/return 40/60 K   Coldbox room transfer
                                    thermal-shield flow     from QLM to QRB

  **Warm line    QINFRA.U,          Utility GHe (U), warm   Partial -- only W
  interfaces**   QINFRA.W, QINFRA.S coupler return (W),     carries a steady
                                    safety/vent path (S)    liquefaction load; U and
                                                            S are utility /
                                                            contingency

  **Internal     WCS.HP,\           HP feed to QRB, LP      Internal only,
  plant          WCS.LP,\           return, VLP suction;    nevertheless routed
  headers**      WCS.VLP            traverse multiple rooms through civil interfaces
                                    and floor levels        and therefore listed for
                                                            coordination
  ----------------------------------------------------------------------------------

  : []{#_Ref211431913 .anchor}Table 1 Main interfacing and helium
  transport lines

QINFRA.W is the only warm return in normal operation and represents the
liquefaction load for the QPLANT. This represents \~ 4 % of the Helium
supplied by the QPLANT to the QCELL via the A-Line in nominal operation.

QINFRA.U is an ad-hoc utility supply and does not participate in the
closed helium cycle under normal conditions.\
\
QINFRA.S is a safety line used during abnormal or emergency events to
protect system integrity (e.g., cold-box overpressure). It routes the
discharged gas to the LP suction interface of the HP compression stage,
from which it is reintegrated into the WCS.HP header, preserving helium
inventory, and ensuring pressure relief.

![](media/image7.emf){width="9.565844269466316in"
height="6.831999125109362in"}

3.  []{#_Toc200491763 .anchor}Introduction to QPLANT Control & Interlock
    System, CIS services and infrastructure.

The QPLANT Control & Interlock System (QPLANT:CIS) shall manage all
internal process operations and local safety functions of the QPLANT. It
comprises the WCS-room PLC, the QRB-room PLC, and a Test and Development
Station that physically and functionally mirrors the QPLANT:CIS hardware

The MINERVA Control and Interlock System (CIS) consists of the following
two parts:

-   MINERVA Control System (MCS) for the control and monitoring of all
    accelerator components (including QCELL) and interfaces with
    QPLANT:CIS.

-   MINERVA Interlock System (MIS) executes machine and personal
    protection interlocks and is split into two parts:

    -   DIS for machine protection: It is e.g., used to communicate any
        machine protection relevant interlock from/to the QPLANT to/from
        QPLANT external systems, e.g., loss of cooling water flow of the
        SCK CEN infrastructure, loss of insulation vacuum of the QMs.

    -   PEPS for personal protection: It is e.g., used to communicate
        any personal protection relevant interlock from/to the QPLANT
        to/from QPLANT external systems e.g., oxygen deficiency

The MINERVA IT Infrastructure (MIT) provides the supporting IT
infrastructure for the entire facility. For the QPLANT, this includes
providing essential functionalities to its Control and Interlock System
(QPALNT:CIS), such as user authentication, the standard network
backbone, and SCADA data storage, ...)

![](media/image8.png){width="6.730583989501312in"
height="4.791666666666667in"}

2.  []{#_Toc200491764 .anchor}Nature of the Procurement

    1.  []{#_Toc200491765 .anchor}Scope of Work by the Contractor

The Contract scope covers all services required to design, build, and
commission a fully functional QPLANT in compliance with the requirements
stated in this document. The scope of work includes, but is not limited
to, the following activities:

-   Design & engineering (including QPLANT internal process integration)

-   Manufacturing, procurement, and supply of all components

-   Transportation, delivery, and on-site installation

-   Stand-alone commissioning and testing, including QPLANT:CIS

-   Quality assurance and quality control activities

-   Support service (based on time and material)

    N.B.: Integrated commissioning activities that involve end-user
    participation (e.g. CIS interfacing or operational acceptance
    testing by SCK CEN personnel) are outside the Contractor's scope.

    1.  []{#_Toc200491766 .anchor}Scope of Supply by the Contractor

**Fixed Scope**

1.  One (1) fully functional Cryoplant

    a.  including e.g.

        i.  Warm Compression Station (WCS)

        ii. Refrigeration Cold Box (QRB)

        iii. Internal piping and vacuum systems

        iv. Control and interlock system (QPLANT:CIS)

    b.  excluding

        i.  Helium gas storage vessels of the Warm Storage Helium (WSH)

2.  Helium inventory for commissioning and acceptance testing

3.  Full documentation package

**Contingent parts**

1.  Set of strategic spare parts for the first 5 years

2.  Helium gas storage vessels of the Warm Storage Helium (WSH)

3.  Yearly Service Level Agreement (SLA)

N.B.: There is no order/preference assumed for the contingent parts.

    1.  []{#_Toc212194821 .anchor}Introduction

        The Contractor shall be fully responsible for ensuring that the
        Deliverables and Services provided fully meet the specified
        requirements for the Contract. Therefore, the Applicant shall
        duly analyse the SCK CEN's Tender Documents and evaluate whether
        sufficient information is presented to allow the Applicant to
        put forward a proposal that ensures the delivery of the procured
        items meets the specified requirements. If certain information
        is found to be lacking, the Applicant shall request this
        information from SCK CEN without undue delay (according to §1.6
        of the Main Tender Document).

        In accordance with §1.7 of the Main Tender Document, the
        Contractor may no longer rely on information lacking after
        submission of its offer. If the Contractor identifies a lack of
        information during the performance of the Contract, this shall
        not give rise to any basis for a Variation.

        In the offer, the Applicant shall explicitly list all additional
        requirements (beyond those specified by SCK CEN) which have been
        defined by the Applicant, and which are assumed to be necessary
        for fulfilling the intended function, performance, or
        integration of the proposed solution. All such assumptions and
        requirements shall be clearly identified, justified, and
        documented as part of the offer. These additional requirements
        may be used as a basis for the system design and/or
        verification.

        The technical requirements imposed by SCK CEN (including, but
        not limited to norms and other standards, processes, and their
        parameters) applicable to the development, performance, and
        quality (inspections, tests, etc.) of the procured items are
        specified in the present document and all other documents
        referred to herein. In principle, these requirements are
        mandatory, unless adjusted in accordance with the principles set
        forth in the subsequent paragraphs.

        In the offer, the Applicant shall clearly state any deviation if
        certain technical requirements are not met (e.g. if a requested
        norm, standard, or preferred process parameter is not
        implemented), The Applicant shall provide a clear description
        and justification for the proposed alternative.

        In the offer, the Applicant may suggest modifications to the
        technical requirements imposed by this document, where such
        modifications improve cost, reliability, safety, ease of use, or
        any other functional aspect of the QPLANT. Each modification
        shall be supported by an assessment of its advantages and
        drawbacks.

        In the offer, the Applicant shall:

-   Submit a single offer, inclusive of all proposed modifications,
    representing the most optimal solution. Multiple alternative offers
    shall not be permitted.

-   Include an overview of the main Contract activities. For each
    activity, the Applicant shall detail how requirements will be met,
    the selected processes and techniques that shall be implemented.

-   Provide at least the details as requested in the present document.
    If no detail level is defined in this document, the Applicant is to
    choose, based on its experience, the appropriate (level of)
    detail(s) to be provided in relation to the criticality and/or
    complexity of the activity.

    During negotiations, deviations and modifications shall be discussed
    between SCK CEN and the Applicant. SCK CEN reserves the right to
    refuse any deviation or modification at its sole discretion and
    without justification. Only deviations and modifications with prior
    written approval from SCK CEN may be implemented.

    1.  []{#_Toc192335394 .anchor}Nominal Operational Scenarios

        1.  []{#_Toc192496488 .anchor}Lifetime and annual maintenance
            schedule

1.  The QPLANT shall be capable to operate uninterrupted in 2K mode for
    at least 90 consecutive days

2.  The maintenance schedule shall adhere to the following constraints:

-   ≥ 6 months: ≤ 10 days in 2K standby

-   ≥ 1 year: ≤ 20 days in 4.5K standby

-   ≥ 5 years: ≤ 60 days in warm stop

-   ≥ 10 years: ≤ 120 days in warm stop

3.  The QPLANT shall have a lifetime of at least 40 years

4.  The QPLANT shall support ≥ 50 warm-up/cool-down cycles (300 K ↔ 2 K)

    1.  []{#_Toc200491776 .anchor}Steady state operational scenarios

5.  The QPLANT shall support the steady state operational scenarios
    defined in Table 2.

+-----------------------------+----------------------------------------+
| **Operational scenarios**   | **Description**                        |
+=============================+========================================+
| Warm Stop                   | > QPLANT and QCELLS at ambient         |
|                             | > temperature                          |
+-----------------------------+----------------------------------------+
| Thermal Shield Standby      | > All QCELLs at thermal shield         |
|                             | > temperature                          |
+-----------------------------+----------------------------------------+
| 4.5 K Standby[^1]           | > All QCELLs around 4 K                |
+-----------------------------+----------------------------------------+
| 2 K Standby                 | > All QCELLs at 2 K (no RF-operation)  |
+-----------------------------+----------------------------------------+
| 2 K Operation               | > RF-operation allowed                 |
+-----------------------------+----------------------------------------+

: []{#_Ref209530150 .anchor}Figure 4 QPLANT's simplified Process Flow
Diagram

In the 2 K operation scenario, the cavity bath is 2 K (saturated
superfluid helium with 31 mbar), the thermal shields supplied at 40 K,
and the coupler cooled between 5 K and 300 K. Backpressure control and
heat load stability are critical for RF operation and a priority design
(for controls) priority both for QCELL and QPLANT.

In the 2 K standby scenario, the same temperature conditions as in 2 K
operation apply, except no dynamic heat load due to RF operation occurs.

1.  []{#_Ref192411691 .anchor}Transient operational scenarios

<!-- -->

6.  The QPLANT shall support the scenario transitions given in Figure 6.

7.  The QPLANT shall execute the transition using the capacity defined
    by the steady state scenarios. No additional capacity shall be added
    solely for acceleration of state transitions.

    1.  Cool-down

8.  The QPLANT shall perform the cool-down of the QPLANT simultaneously
    with the cryogenic users (QCELL and QDIST (static heat loads only).

9.  The QPLANT shall facilitate parallel cool down/warm up of all
    QCELLs. During cooldown and warm-up, cryomodules impose constraints:

-   Magnetic shields must reach T \< 70 K (part of the 50 K thermal
    mass) before cavities (part of the 2K mass) reach T \< 10 K.

-   The QCELLs will autonomously limit cooldown speed to enforce this
    requirement on the user side

10. The QPLANT shall facilitate an alternative cooldown in which only
    the thermal‑shield (TS) circuit which contains the 50 K stage cold
    masses are cooled until their average temperature reaches 50 K.
    Subsequently the headers A--B and D--E are simultaneous cooled down

![](media/image10.svg){width="7.010416666666667in"
height="4.666666666666667in"}

In their offer the Applicant shall:

-   Indicate and demonstrate the shortest achievable cooldown time from
    300 K to 2 K using Appendix 9.1 data, and the warm‑up duration for
    each transition in assuming simultaneous cooling of headers A--B and
    D--E.

-   Indicate and demonstrate the maximum refrigeration power the QPLANT
    can sustain at 250 K, 200 K, 150 K, 100 K, 50 K and 4.5 K.

    1.  Warm-Up

11. The QPLANT shall facilitate the warm-up of the cryogenic users from
    2 K to 300 K in less than 5 days.

12. The QPLANT shall support the transition shown in Cool-down

13. The QPLANT shall perform the cool-down of the QPLANT simultaneously
    with the cryogenic users (QCELL and QDIST (static heat loads only).

14. The QPLANT shall facilitate parallel cool down/warm up of all
    QCELLs. During cooldown and warm-up, cryomodules impose constraints:

-   
-   

15. Magnetic shields must reach T \< 70 K (part of the 50 K thermal
    mass) before cavities (part of the 2K mass) reach T \< 10 K.The
    QCELLs will autonomously limit cooldown speed to enforce this
    requirement on the user sideThe QPLANT shall facilitate an
    alternative cooldown in which only the thermal‑shield (TS) circuit
    which contains the 50 K stage cold masses are cooled until their
    average temperature reaches 50 K. Subsequently the headers A--B and
    D--E are simultaneous cooled down

16. ![](media/image10.svg){width="7.010416666666667in"
    height="4.666666666666667in"} for the warming-up of the cryogenic
    users, whether passively or actively (with QCELL heaters if
    available):

-   "Warm-up to 4.5 K" by stopping the VLP Compressors (WCS/PVPS) and
    the Cold (QRB/CC)

-   "LHe emptying" of the liquid helium baths by evaporation, optionally
    using electrical heaters, and stopping level controls

-   "Warm-up to TS"

-   "Warm up to T~ambient~"

    In their offer, the Applicant shall indicate and motivate the
    expected duration of each main phase of the warm-up process.

    1.  []{#_Toc200491791 .anchor}Other operational scenarios

        1.  Purging and Conditioning

17. The Contractor may implement a manual purging, manual conditioning,
    and manual initial preparation of the QPLANT.

-   If a manual approach is selected, the Contractor shall provide a
    detailed step‑by‑step procedure, including instrumentation checks,
    purge‑gas quality requirements, vent routing, and acceptance
    criteria for oxygen‑free readiness.

18. The QPLANT shall adhere to the purge‑parameter table (pressure,
    flow‑rate, duration, allowable residual O₂) provided by SCK CEN
    during contract execution.

    1.  Liquid Filling

19. The QPLANT shall facilitate an average retention rate of 0.8 g/s LHe
    per individual QCELL (24 g/s total) during the filling process.

20. During LHe filling, the QPLANT shall provide 2 900 L of LHe to the
    users.

21. The Contractor shall assume that LHe filling and emptying occurs
    when cryogenic users are at 4.5 K and header A conditions are met
    before JT expansion (as per QRB.A interface conditions during normal
    operation)

    In their offer, the Applicant shall:

-   State the expected duration of the LHe filling phase and the maximum
    LHe filling rate the QPLANT can produce.

-   State the expected duration of the LHe emptying phase and the
    maximum continuous emptying flow rate the QPLANT can accommodate
    while preserving the helium inventory.

22. The Contractor shall facilitate the following two evaporation
    possibilities:

    a.  Static heat loads only (Minimum evaporation rate).

    b.  QCELL heaters sped up.

23. The emptying phase shall be considered both as part of the full
    warm‑up sequence (2 K → 300 K) and as a stand‑alone transitional
    operation (for example: 2 K Standby → 4.5 K Standby → LHe Emptying →
    Filled LHe Emptying →4.5 K Standby → 2 K Standby) to permit short
    maintenance windows. See
    ![](media/image10.svg){width="7.010416666666667in"
    height="4.666666666666667in"} for the state‑transition diagram.

24. The helium inventory shall remain in QCELL and only be transferred
    to QINFRA storage for extended long‑term unavailability (LTU) or
    planned access. Any planned transfer of inventory shall:

    a.  Require specified monitoring and controls while inventory
        remains in QCELL (pressure/temperature telemetry, alarms,
        periodic leak checks).

    b.  Require documented isolation and valve configurations and
        confirmatory checks before any inventory transfer venting.

    <!-- -->

    1.  []{#_Toc202536091 .anchor}Performance Requirements

25. The QPLANT shall be sized for the following two Design Points:

    a.  Nominal Design Point: operational scenario "2K operation" with
        30 QCELLs.

    b.  Minimal Design Point: operational scenario "2K standby" with 24
        QCELLs.

26. The QPLANT shall be designed for the heat loads defined in Table 3.

+------------+------+------+------+-------+-------+---------+-------+
| O          | Is   |      | No   |       |       |         | Indic |
| perational | othe |      | n-Is |       |       |         | ative |
| Scenario   | rmal |      | othe |       |       |         | E     |
|            | Heat |      | rmal |       |       |         | quiv. |
|            | L    |      | Heat |       |       |         | Ref   |
|            | oads |      | Lo   |       |       |         | riger |
|            | \    |      | ads\ |       |       |         | ation |
|            | [W\] |      | \    |       |       |         | Po    |
|            |      |      | [W\] |       |       |         | wer,\ |
|            |      |      |      |       |       |         | \[**W |
|            |      |      |      |       |       |         | @     |
|            |      |      |      |       |       |         | 4.5   |
|            |      |      |      |       |       |         | K**\] |
+============+======+======+======+=======+=======+=========+=======+
|            | Bath | Bath | VLP  | SHe   | TS    | Mass    |       |
|            | at   | at   | re   | s     | (40   | Flow    |       |
|            | 2K   | 4K   | turn | upply | -60K) | (g/s)   |       |
|            | (q~C | (q~C | line | line  |       | for     |       |
|            | AV~) | AV~) |      |       | (q    | c       |       |
|            |      |      | 3    | 4.5K  | ~TS~+ | ouplers |       |
|            |      |      | .5K- | (q    | qI    | 4       |       |
|            |      |      | 3.7K | I~A~) | ~E~ + | .5-300K |       |
|            |      |      | (qI  |       | q     | (       |       |
|            |      |      | ~B~) |       | I~D~) | q~CPL~) |       |
+------------+------+------+------+-------+-------+---------+-------+
|            |      |      | Q    | QRB.A | Q     | QRB.W   |       |
|            |      |      | RB.B |       | RB.D, | (via    |       |
|            |      |      |      |       | QRB.E | QI      |       |
|            |      |      |      |       |       | NFRA.W) |       |
+------------+------+------+------+-------+-------+---------+-------+
| 2K         | 900  | 0    | 40   | 20    | 8600  | 2       | 3430  |
| Operation  |      |      |      |       |       |         |       |
| for 30QM:  |      |      |      |       |       |         |       |
|            |      |      |      |       |       |         |       |
| Nominal    |      |      |      |       |       |         |       |
| Design     |      |      |      |       |       |         |       |
| Point      |      |      |      |       |       |         |       |
+------------+------+------+------+-------+-------+---------+-------+
| 2K Standby | 340  | 0    | 30   | 10    | 5100  | 1       | 1490  |
| for 24QM:  |      |      |      |       |       |         |       |
|            |      |      |      |       |       |         |       |
| Minimal    |      |      |      |       |       |         |       |
| Design     |      |      |      |       |       |         |       |
| Point      |      |      |      |       |       |         |       |
+------------+------+------+------+-------+-------+---------+-------+
| 4.5K       | 0    | 560  | 0    | 11    | 8600  | 2       | 1640  |
| Standby    |      |      |      |       |       |         |       |
| for 30 QM  |      |      |      |       |       |         |       |
+------------+------+------+------+-------+-------+---------+-------+
| TS Standby | \~0  | \~0  | \~0  | \~0   | 8600  | \~1     | 720   |
| for 30QM   |      |      |      |       |       | (40     |       |
|            |      |      |      |       |       | k-300k) |       |
+------------+------+------+------+-------+-------+---------+-------+

: []{#_Ref200099216 .anchor}Figure 5 QPLANT - Control and Interlock
related systems

27. The QPLANT shall support the fluid conditions at the QRB interface
    for HP-A, VLP-B and CPLR-W listed in Table 4.

28. For the Thermal Shield circuits (QRB.D and QRB.E) the Contractor
    shall optimize the mass flow, temperatures, and pressures to improve
    the overall efficiency or capital investment. The respective values
    listed in in Table 4 are the only indicative values.

    In the offer, the Applicant shall indicate the temperatures, and
    pressures of the Thermal Shield circuits.

  ------------------------------------------------------------------------
  Interface QRB High       Very Low    Coupler     TS Supply   TS Return
                Pressure   Pressure    Return      -- QRB.D    -- QRB.E
                (HP) --    (VLP) --    (CPLR) --               
                QRB.A      QRB.B       QRB.W                   
  ------------- ---------- ----------- ----------- ----------- -----------
  Operating                                                    
  Scenario: 2 K                                                
  Operation                                                    

  Pressure      ≥ 3.0      ≤ 0.026     \~ 1.1      \~ 14.0     \~ 13.0
  (bar)                                                        

  Temperature   ≤ 4.5      ≥ 3.5       300         ≤ 40        ≤ 60
  (K)                                                          

  Mass Flow     ≥ 47       ≥ 45        ≥ 2         81          81
  Rate (g/s)                                                   

  Operating                                                    
  Scenario: 2 K                                                
  Standby                                                      

  Pressure      ≥ 3.0      ≤ 0.029     \~ 1.1      \~ 14.0     \~ 13.0 
  (bar)                                                        

  Temperature   ≤ 4.5      ≥ 4.2       300         ≤ 40        ≤ 60
  (K)                                                          

  Mass Flow     18         17          1           48          48
  Rate (g/s)                                                   
  ------------------------------------------------------------------------

  : []{#_Ref192158138 .anchor}Table 2 Operational Scenarios

1.  []{#_Toc202536092 .anchor}Reliability Requirements

<!-- -->

29. The QPLANT shall apply proven processes and be based on industrially
    proven technologies.

30. For failures resulting in an unplanned transition out of the "2K
    operation" scenario, the MTBF shall be higher than 5 years.

31. For failures resulting in an unplanned transition to the "4.5K
    standby" scenario, the MTBF shall be higher than 10 years.

32. For failures resulting in an unplanned warm up of the linac to \>
    4.5K, the MTBF shall be higher than 15 years.

    In the offer, the Applicant shall provide a substantiated
    justification for the MTBF of the QPLANT, including but not limited
    to:

-   Applied redundancy (e.g., N+1, 2oo3)

-   MTBF values for each critical component, with supporting data

-   Summary RAMI considerations and lifecycle-impacting design choice

-   Outline of RCM strategy supporting availability objectives

-   Key failure modes and corresponding mitigation measures (FO, FC, NO,
    NC for critical isolation or segmentation valves shall be provided
    for the LOOP and at least one other scenario (main interfacing
    valves of QRB and WCS)

33. The Contractor shall submit the detailed MTBF calculation
    demonstrating the compliance of the detailed design with the MTBF
    requirements to SCK CEN for review and subsequent approval at the
    latest by the end of the Phase 1. The Contractor shall substantiate
    the MTBF values by manufacturer data (OEM or COTS), field
    performance records, or predictive reliability models. The level of
    detail shall be proportionate to the component's criticality in the
    overall system reliability and availability architecture. The
    Contractor shall also provide a component-level (LRU) replacement
    schedule for the expected lifetime duration of at least 40 years,
    including MTBF data, estimated downtime impact, and cost per
    intervention.

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

    1.  []{#_Toc212194842 .anchor}QPLANT Control System

        1.  []{#_Toc200492240 .anchor}Overview

The QPLANT Control System (QPLANT:CIS) is the dedicated system for the
local control of the QPLANT, ensuring all on-site cryogenic processes
operate safely and efficiently. To function within the wider facility,
the QPLANT:CIS integrates with the MCS, the MIT platform, and the MIS.

The integration with the MCS is designed to:

-   Exchange all necessary data between the QPLANT:CIS and the QCELLs.

-   Provide operators with a single, unified interface to seamlessly
    monitor and control the QPLANT alongside other primary systems.

The integration with the MIT platform is designed to:

-   Connect to centralized networking

-   Utilize centralized infrastructure like data storage, backups, and
    user authentication.

Within the overall safety framework, the QPLANT:CIS has a clearly
defined role:

-   It manages the dedicated local protection of the QPLANT, executing
    immediate safety functions such as automated shutdowns in response
    to internal faults.

-   It defers to the MIS for all global safety functions, particularly
    when the QPLANT interacts with other facility systems

    1.  []{#_Toc200492241 .anchor}Reference Architecture

Figure 9 illustrates the reference architecture of the complete
cryogenic control system, identifying the QPLANT:CIS as a key
sub-system.

![](media/image13.jpeg){width="6.65748031496063in"
height="6.106299212598425in"}

Refer to §9.2.2 for detailed signal and interface mapping shown in
Figure 9

2.  []{#_Toc212194845 .anchor}Architecture, Autonomy, and Scope

<!-- -->

238. The QPLANT:CIS shall include all components identified in green
     within Figure 9 (Reference Architecture). The QPLANT:CIS shall
     include any additional systems or subsystems required to meet
     overall cryogenic system performance, functional, and safety
     objectives.

239. The QPLANT:CIS shall use a commercially available, industrial-grade
     control platform with documented lifecycle support and vendor
     independence. It shall meet applicable safety, performance, and
     reliability standards and shall comply with all relevant regulatory
     frameworks.

240. The QPLANT:CIS shall enable autonomous operation of the QPLANT
     across all defined operational scenarios and transitions, without
     requiring operator intervention.

241. The QPLANT:CIS shall support real-time monitoring of instrument
     health (e.g.: drift, dropout, deviation from expected range) with
     alarms and diagnostic flags for early fault detection.

     1.  []{#_Toc202536179 .anchor}Test System for Functional
         Verification

242. The Contractor shall deliver a dedicated, fit-for-purpose Test
     System for functional testing, validation, and commissioning of the
     System Under Test (SUT), specifically the QPLANT and its QPLANT:CIS

243. The Test System shall emulate key operational states including
     normal start-up, shutdown, transients, degraded modes, and fallback
     conditions.

244. The Test System shall enable alarm logic verification, interlock
     testing, and diagnostic evaluation without reliance on the live
     operational system.

     In the Offer, the Applicant shall:

-   Describe proposed SUT/Test System architecture.

    1.  []{#_Toc202536180 .anchor}Digital Process Model

A complete digital process model (transient simulation or digital twin)
is not mandatory. However, if the Contractor proposes one, the following
requirements shall apply:

245. Any proposed model shall use certified, validated, or
     standards-compliant toolsets (e.g., Simulink®, SimCryogenics, or
     validated statistical/ML models).

246. The model shall support operator training, failure simulation,
     diagnostics, and maintenance planning.

247. The model shall enable future integration into the control system
     to support virtual sensors, inference algorithms, and predictive
     diagnostics.

     In the Offer, the Applicant shall:

-   State if they will provide a digital process model and motivate it
    the decision by a cost-benefit analysis.

-   If it is not provided, the Applicant shall describe alternative
    approach for commissioning, fault simulation, diagnostics, training.

-   Provide supporting documentation for training and validation
    strategy.

    1.  []{#_Toc202536182 .anchor}Cryogenic System Control and MCS
        Integration

248. The QPLANT:CIS shall regulate the mass flow rate and supply
     temperature at the QPLANT--QCELL interface (via QINFRA to QRB in
     the coldbox room), such that the temperature change rate - during
     cool-down and warm-up - of each QCELL remains within predefined and
     controlled limits. The temperature change rate is defined as the
     maximum allowable rate of change of the internal QCELL temperature,
     expressed in K/h (e.g., 4 K/h).

249. The QPLANT:CIS shall allow the adjustment of these limits depending
     on the thermal inertia of each QCELL and the operational mode to
     form part of process design and general control methodologies

250. The QPLANT:CIS shall support bidirectional communication with the
     Concentrator PLC (refer to Figure 9 and items 20 and 33),
     exchanging real-time operational and control signals at an update
     rate of 1 Hz. This will be used by the Concentrator PLC,
     implemented within MCS, to actively control and enforce this
     temperature change rate by issuing setpoints and operational
     constraints to the QPLANT.

251. The QPLANT:CIS shall route all control commands, system status
     updates, and alerts related to cryogenic operation via MIT to
     ensure centralized visibility and unified supervision across QPLANT
     and QCELL domains.

252. The QPLANT:CIS shall enable autonomous operation (without operator
     intervention) of the QPLANT across all specified scenarios and
     transitions between them.

     1.  []{#_Toc200492260 .anchor}General Software and Hardware
         Requirements

253. The Contractor shall follow the applicable sections from the
     General Software and Hardware Requirements for Contractors (GSHRC)
     containing quality and other requirements related to software,
     firmware, and interoperability

254. When the MCS is unavailable or a communication loss occurs, the
     QPLANT:CIS shall continue to operate as long as the systems safety
     as well as personnel safety are guaranteed.

255. All the control parameters relevant for User Integration and
     monitoring (e.g.: setpoints and thresholds), including calibration
     data shall be available to the remote-control interface with MCS.

256. Interlock thresholds shall not be writable through the
     remote-control interface.

257. The QPLANT:CIS should allow every actuator to be controlled
     manually in the event of a malfunction (for example a motor can
     have an auto, manual override to fixed values).

258. The QPLANT:CIS shall allow every sensor value to be set by the
     operator (mode maintenance) to be interpreted by the QPLANT:CIS as
     it is the real value coming from the sensor.

259. Records of all measured values, valve positions, operator actions,
     logbook and alarms shall be accessible in QPLANT:CIS.

     1.  []{#_Toc200492268 .anchor}Software development

260. As part Control System Dossier, the following controls related
     information shall be provided to SCK CEN:

-   The detailed documentation of the software architecture, covering
    all modules, functional blocks, and components, along with their
    inputs and outputs.

-   lists of alarms, protection functions, instruments, events, and
    parameters.

    In the offer, the Applicant shall provide sufficient detail deemed
    representative of the anticipated software development scope and
    fixed-price offer, including assumptions, planned methodologies, and
    architectural breakdown.

261. All PLCs shall be programmed in full compliance with the IEC
     61131-3 standard.

The use of Instruction List (IL) is highly discouraged. Higher-level
languages like Structured Text (ST) are highly recommended for better
clarity, maintainability, and portability of PLC programs. Therefore,
users and developers are strongly advised to avoid new implementations
in IL and to migrate any existing IL-based code to ST or other
recommended IEC 61131-3 languages whenever possible.

In the offer, the Applicant shall:

-   Declare the programming languages to be used per functional block.

-   Justify any deviation from ST, including retained IL-based
    implementations.

-   Demonstrate software structuring practices that favour
    maintainability, reuse, and modular design.

    Proposals will be evaluated with preference given to Applicants
    demonstrating disciplined use of structured IEC 61131-3 languages
    and long-term maintainability strategies.

262. When the Software Component includes human readable information
     (for example, but not limited to: HMI, logging, source code), it
     shall be in English.

263. The Contractor shall develop a functional analysis and a detailed
     description of all control scenarios including interfaces. The
     detailed description shall also include program sequence plan
     (functions and procedures used in the program).

     In the offer, the applicant shall provide a detailed preliminary
     functional analysis and indicative control sequence plan,
     representative of the anticipated implementation. This shall
     include key functions, procedural steps, and interface interactions
     necessary to support evaluation of scope, architecture complexity,
     and design maturity.

-   The submission shall reflect a fixed-price offer and anticipated
    development consistent with the proposed control strategy.

<!-- -->

-   For each software module, functional block, component, or data
    block, the Contractor shall provide a detailed description of the
    logical conditions and input states that govern the activation,
    value assignment, or change of each output parameter.

264. Versioning info through MCS interface: Each Software Component and
     Hardware Node shall include a unique version identifier that
     uniquely represents the build date and Git commit hash,
     automatically generated during the build process to ensure
     traceability; this identifier shall be retrievable in a consistent
     and read-only manner through the MCS control and monitoring
     interface.

     1.  []{#_Toc200492279 .anchor}Software Change Management

Prior to deployment in the production environment, software updates
shall be rigorously tested in a staging environment. This minimizes
risks of integration issues with MCS, MIT, MIS, or any interfacing
systems and downtime of the QPLANT.

> ![](media/image14.png){width="3.886111111111111in"
> height="3.395521653543307in"}

265. The Contractor shall use a dedicated test environment that
     replicates the production system\'s configuration, functionality,
     and critical interfaces for software changes. This environment may
     be virtual, physical or a combination.

266. The test environment shall mirror the production system to a level
     that allows reliable validation of all changes under simulated
     real-world conditions, including performance, response time and
     stress scenarios.

267. All changes shall undergo rigorous functional, integration, and
     regression testing in the staging environment before deployment to
     the production system.

268. No changes shall be implemented on the production system without
     prior approval based on documented test results and validation in
     the test environment.

269. The Contractor shall provide a pre-tested rollback plan to ensure
     the system can be restored promptly to its previous state in case
     of issues.

270. All changes shall be tracked in a version control system with an
     audit trail, providing clear documentation of modifications and
     approvals.

271. Changes shall be designed and tested to ensure minimal impact on
     system availability during deployment, including options for
     hot-swapping or scheduled maintenance windows.

272. The Contractor shall guarantee that all testing activities in the
     staging environment remain completely isolated from production
     operations to prevent any unintended disruptions.

273. All regulatory requirements applicable to the delivery of the plant
     shall also be adhered to for any changes made after delivery,
     ensuring compliance with safety, environmental, and industry
     standards.

274. The contracting authority reserves the right to audit the testing
     process, staging environment, and changes at any time to ensure
     adherence to requirements.

275. The Contractor shall collaborate with stakeholders to evaluate and
     improve the testing and change management process based on
     operational feedback and lessons learned.

276. The Change management should be in place after Factory Acceptance
     Test and used for changes needed to integrate the consumers.

     1.  []{#_Toc200492292 .anchor}Human Machine Interface (HMI)

277. The Contractor shall deliver local operator stations to provide
     local data collection and reporting for the QPLANT system to
     support maintenance activities. As a minimum one is expected in the
     Compressor Room and one in the Cold Box Room.

278. The Contractor shall not deliver or implement an enterprise level
     QPLANT SCADA system (multi-user or multi-server architecture) as
     part of the scope.

279. The Contractor shall deliver and implement a temporary QPLANT SCADA
     system exclusively for use during the standalone commissioning
     phase. This solution is intended solely to support initial testing,
     commissioning, and operator training, and should be decommissioned
     and replaced by the MCS solution once integration is realized. This
     temporary system shall also be used as reference design for the
     development of the MCS Navigator therefor sufficient documentation
     is required.

280. The Contractor shall provide support for integration of the
     QPLANT:CIS with the MCS Navigator. This includes, but is not
     limited to:

281. Providing support in designing the Operator Screen for the Plant.

282. Supplying necessary communication protocols (e.g., OPC UA, TCP/IP)

283. Coordinating with the project SCADA team to ensure data consistency
     (e.g., tags, alarms)

284. Sharing relevant technical documentation and engineering details to
     enable seamless integration

285. The Contractor shall ensure that the operator stations (whether HMI
     panels or dedicated Industrial touch PCs) are based on
     industrial-grade hardware specifically designed for continuous
     operation in a production environment. This includes robust
     construction, compatibility with the QPLANT's environmental
     conditions (temperature, dust, vibrations, \...), and adherence to
     relevant industrial standards.

286. The platform shall be supported with software updates, firmware
     updates, and security patches for a minimum of 20 years from the
     date of commissioning. The Contractor shall provide documentation
     or official manufacturer statements guaranteeing availability of
     updates throughout this period.

     In the offer, the Applicant shall explicitly address the
     obsolescence management strategy for the proposed PLC or control
     system platform, considering the anticipated forty (40) year
     operational lifetime of QPLANT. This shall include:

-   Manufacturer support lifecycle documentation

-   Spare part availability forecasts and migration plans

-   Platform evolution roadmap (e.g., upgrade compatibility or
    virtualization strategy)

-   Technical or commercial approach to sustaining software and hardware
    support beyond the guaranteed 20-year update period (e.g.,
    stockpiling, long-term service contracts, emulation layers).

    1.  []{#_Toc212194853 .anchor}Migration to Newer Hardware

287. The visualization (HMI) project shall be designed in such a way
     that it can be migrated to newer hardware of the same manufacturer
     if the originally delivered hardware becomes obsolete or requires
     upgrade. This includes ensuring future compatibility of project
     files and software licenses and providing guidelines for seamless
     transfer of project data and configurations.

288. The touchscreen display shall have a minimum diagonal size of 24
     inches to ensure sufficient screen space for detailed process
     graphics and user interaction.

289. The display shall support a resolution suitable for clear viewing
     of process graphics, text, and trends. A minimum resolution of
     1920×1080 (Full HD) is recommended for a 24-inch display.

290. Where the system includes a local Human Machine Interface (HMI)
     that supports local control, it shall implement a control selection
     mechanism based on a 3-state principle: Local - Free - Remote.

     Local or remote control can only be granted when the system is in
     the 'free' state. If the system is not free, the requester will be
     denied the requested control, and any write commands from that side
     will be ignored. However, reading the system state shall always be
     permitted in any state, allowing either side to retrieve
     information about the system\'s status and confirming whether a
     request was successful. Writing (changing) is only allowed when the
     request is accepted.

     This control mechanism only pertains to local versus remote control
     states. Any other state machines within the system shall remain
     active, ensuring that, for example, regulation loops continue to
     function in either state.

291. Once a system is reserved in a specific control mode, it shall
     automatically transition to the \"Free\" state if a configurable
     timeout period (maximum of 5 minutes) of non-activity expires.
     \"Releasing\" means transitioning from a specific control state to
     the \"Free\" state. Non-activity refers to the absence of local or
     remote actions.

292. The Operator Station shall be designed as a non-critical component
     of the control system. No real-time or safety-critical control
     functions shall reside in the Operator Station; it is purely for
     monitoring, visualization, and local interaction.

293. The Operator Station shall store operational data (e.g., trends,
     alarms) only for a limited amount of time, sufficient for
     short-term analysis and troubleshooting. The data stored locally
     shall not be formally backed up; once data ages out of the
     configured retention period, it may be overwritten or discarded.

294. The Operator Station shall provide capabilities for plotting curves
     and trends, enabling real-time and short-term historical
     visualization of key process variables.

295. The Operator Station shall include graphical process views,
     providing an intuitive interface for monitoring equipment states
     and process flows.

296. The Operator Station shall show and log alarms and events for
     immediate operator awareness without functionality to acknowledge
     alarm occurrences

297. Graphical process views shall be agreed with SCK CEN.

298. All the sensors and actuators shall be integrated in different
     graphical views.

299. The Operator Station (PLC with IO mirroring QPLANT:CIS (PLC in WCS
     and PLC in QRB) software shall support a default data acquisition
     period of maximum two seconds. For critical turbine data an
     acquisition rate of 100 ms is required.

300. The HMI software shall allow at least two permission levels with
     distinct functions available.

301. The QPLANT:CIS shall allow to automatically call or e-mail "on
     call" staff through MIT

302. The graphical views shall be in accordance with the Process &
     Instrumentation Diagrams to easily understand and operate the
     system.

303. The HMI software package shall be installed on two workstations
     with large screens (at least height 24 inches monitors) to
     visualize the useful information during QPLANT operation

     1.  []{#_Toc200492316 .anchor}Network

         1.  Reference Architecture

![](media/image15.png){width="4.790713035870517in"
height="2.439401793525809in"}

From Figure 11 above the hierarchy and levels are shown:

Enterprise Network: Represents the high-level IT network connecting
various business operations, services, and systems. It serves as the
foundation for communication across the organization.

Industrial Network: Focuses on the network responsible for managing
industrial operations and controls, connecting systems such as SCADA,
PLCs, and field devices. It ensures reliable data transmission for
production and automation processes.

Plant: This is the central infrastructure that interconnects different
network segments, providing high-speed data transfer and ensuring
scalability and reliability.

Zone: Acts as an intermediary between the cell and the industrial
network, handling traffic distribution and optimizing data flow.

2.  General

<!-- -->

304. The Contractor shall supply a detailed list of the network ports
     and protocols necessary for the correct functionality of their
     system and application.)

305. The Contractor shall be responsible for configuring the necessary
     network elements based on the inventory of network ports,
     protocols, internal and external applications.

306. The Contractor shall use IP address ranges for the QPLANT:CIS as
     provided by the customer. This includes equipment in Level 0 of the
     Perdue model. These ranges will be pre-assigned by MIT to ensure
     consistency with the overall network architecture and addressing
     schemes. The Contractor is responsible for implementing the
     provided IP ranges without deviation, and any additional IP
     requirements shall be communicated to and approved by MIT prior to
     implementation. Additionally, the Contractor shall document the use
     of the assigned IP ranges for each device and submit this
     documentation to MIT upon completing the configuration. MIT
     reserves the right to audit the Contractor\'s implementation to
     ensure adherence to the assigned IP ranges and network
     configuration standards.

307. Where a Software Component can be upgraded, the QPLANT:CIS shall
     support an upgrade procedure which can be automated as script(s),
     without the need for an Internet connection. A list of required
     tools must be provided.

     1.  Services

308. Where backup of a system is required, for each system following
     shall be defined DD5 ():

-   a clear list of all folders, files, databases, \... that are to be
    included in a backup

-   a document describing the backup and restore process

-   any script(s) required to perform these backups and restore actions

309. Where the system has an operating system, the System shall support
     monitoring by at least one of the protocols mentioned in the MIT
     interface catalogue chapter \"Monitoring\".

310. Where the system has no operating system and requires
     authorization, the System shall support authorization by at least
     one of the protocols mentioned in the MIT interface catalogue
     chapter \"Authorization and security\".

311. Where the System has an operating system, the System shall support
     authorization by at least one of the protocols mentioned in the MIT
     interface catalogue chapter \"Authorization and security\".

312. Where the system has no operating system and requires
     authentication, the System shall support authentication by at least
     one of the protocols mentioned in the MIT interface catalogue
     chapter \"Authentication\".

313. Where the System has an operating system which requires
     authentication, the System shall support authentication by at least
     one of the protocols mentioned in the MIT interface catalogue
     chapter \"Authentication\". Ref. SCK\\55564083

314. The System shall support network addressing service by at least one
     of the protocols mentioned in the MIT interface catalogue chapter
     \"Network addressing service\".

315. The System shall support network naming service by at least one of
     the protocols mentioned in the MIT interface catalogue chapter
     \"Network naming service\".

316. The Contractor shall implement a mechanism for automatic IP address
     assignment based on MAC addresses whenever possible, utilizing DHCP
     services to ensure efficient and consistent configuration. In
     scenarios where DHCP is not feasible, the Contractor shall
     configure static IP addresses in accordance with MIT\'s assigned IP
     ranges. All configurations shall align with MIT\'s network
     architecture standards to ensure seamless integration and avoid IP
     conflicts.

317. The Contractor shall provide a comprehensive list of all devices,
     including their respective MAC addresses, prior to configuring the
     network. This list is crucial for tracking and managing devices,
     especially when configuring static IP addresses or ensuring proper
     DHCP assignment.

318. If a device is DHCP-capable but not configured for DHCP, the
     Contractor shall provide a detailed procedure for enabling and
     configuring DHCP on the device. The procedure shall include all
     necessary steps for ensuring proper DHCP functionality, such as
     network settings, IP lease time configuration, and alignment with
     MIT's DHCP service and network standards.

     1.  Infrastructure

An aggregation network ensures high reliability and performance by
implementing redundancy to minimize downtime and enable fast recovery
during faults. Redundant connections ensure continuous backbone network
availability by enabling quick failover during link failures, minimizing
disruptions, and maintaining system stability.

319. The aggregation network shall use a redundant ring topology, with a
     dedicated redundancy manager and client switches. The network shall
     automatically reconfigure within 300 ms in case of interruptions.
     Redundant connections to the backbone shall be established using a
     master/slave configuration, ensuring failover times under 300 ms.
     All links within the aggregation network, including connections to
     the backbone and cell networks, shall support 1 Gbit/s bandwidth.
     The network design shall incorporate fault recovery mechanisms to
     reroute traffic in the event of failures, ensuring uninterrupted
     data flow.

320. The QPLANT:CIS shall establish redundant connections to the
     backbone network using standby redundancy. Each connection shall
     include a master and backup device, with failover mechanisms
     ensuring that if one de²vice or connection fails, the other takes
     over seamlessly. The failover time shall be deterministic, with a
     maximum duration of 300 ms to minimize downtime.

     1.  Security

321. The Contractor shall comply with the SCK CEN cybersecurity policy,
     ensuring alignment with the IAEA NSS17 (Nuclear Security Series),
     ISO 27001 (Information Security Management), and IEC 62443
     (Industrial Communication Networks -- Network and System Security)
     standards. This includes implementing required security controls,
     risk management processes, and incident response protocols as
     outlined by these frameworks.

322. Documentation of the system\'s security features and their
     alignment with the client\'s standards must be provided for review
     and approval before deployment.

323. The Contractor shall work with the client to verify that the system
     integrates seamlessly with the client's existing security
     infrastructure, including firewalls, VPNs, and any other relevant
     security tools.

324. The Contractor shall identify all products and digital elements
     used in the production plant, including Commercial Off-The-Shelf
     (COTS) materials and custom-built systems, that fall under the
     scope of the Cyber Resilience Act. These products must be evaluated
     for compliance with the CRA\'s cybersecurity requirements.

325. If the Contractor requires remote access to the plant, he shall
     utilize the standard solution provided by the customer. Access will
     be granted with restricted permissions to ensure that only
     necessary functions are available, safeguarding the integrity and
     security of the plant\'s systems. The Contractor is responsible for
     adhering to the defined access protocols and ensuring compliance
     with the customer\'s security policies.

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

     1.  []{#_Toc200492436 .anchor}Factory Testing

         1.  []{#_Toc200492437 .anchor}Welding, pressure, and leak tests

402. As a minimum, the following tests shall be conducted during
     construction of the components.

-   Pressure tests shall be performed in accordance with the design and
    construction code.

-   Leak test shall be performed at ambient temperature after the
    pressure tests.

-   Leak tests of specific cold components (e.g. transfer lines) shall
    be conducted after spraying liquid nitrogen on welds.

    The Contractor, based on his own experience, shall carry out
    additional tests as necessary to ensure specified performance and
    quality.

    1.  []{#_Toc192183302 .anchor}Tests of components

403. All possible functional tests at the manufacturer sites shall be
     performed to detect any faults before delivery and confirm the
     performances indicated in the technical specification. These tests
     shall include at least those mentioned in following requirements.

-   All helium compressors or pumps shall be tested individually at the
    manufacturer's premises. The measured values shall include at least
    flow rate, pressures, temperatures, helium leak, noise level and
    vibrations.

-   Compressor motors shall be tested individually at the manufacturer's
    premises. The measured values shall include at least power
    consumption, temperatures, noise level, vibrations, efficiency, \...

-   Turbines, cold compressors, and cold circulators shall be tested at
    the manufacturer's premise at design rotation speed at ambient
    temperature. Measurements shall include vibrations, rotor stability
    and noise.

-   All cryogenic helium valves shall be delivered with leak test
    certificates of the body and the seat.

-   All safety components shall be delivered with the necessary
    certificates.

    1.  []{#_Toc200492447 .anchor}Electrical, wiring and control system
        tests

404. After mechanical assembly and cabling of any sub-assembly, the
     Contractor shall execute a complete electrical and wiring test. All
     components and cabling shall conform to the international
     electrical standards (IEC). The electrical and wiring tests shall
     include at least:

-   Visual inspection of cabling.

-   Checking of conformity with the electrical wiring diagrams.

-   Checking of correct labelling.

-   Checking of the grounding of all components and measuring of
    insulation resistance for all electrical wiring and electrical
    components.

-   Performing functioning of valves with adjustment of the positioners.

-   Checking of the instrumentation cabling.

-   Checking of the electrical cabinets (instrumentation, power supply
    and control) with injection of inlet signals and detection of outlet
    signals.

405. For the WCS electrical tests, before the connection between the
     motor and the compressor, the Contractor shall:

-   Verify the direction of motor rotation.

-   Check of phase rotation direction on the electrical cubicle busbar
    before switching on 3 phases electrical motors.

406. The QPLANT:CIS operation shall be tested in simulation mode before
     shipment.

     1.  []{#_Toc200492460 .anchor}Transport and Storage

407. The Contractor is responsible for the transport and storage of all
     the QPLANT components from the manufacturing sites to the SCK CEN
     final positioning. It includes the storage, transport, loading,
     unloading and final positioning activities.

408. Prior to transportation, all process circuits of the QPLANT
     components shall be filled with inert gas at a fixed pressure and
     sealed during transport. Necessary caps, blind flanges and hand
     valves shall be considered at that stage. Pressure gauges shall be
     installed and checked at the departure from manufacturer premises
     and at the arrival on SCK CEN site. It is recommended to provide
     transportation boxes with appropriate accelerometers for the
     refrigeration cold box.

409. Appropriate packaging shall protect every item during transport
     from degrading environment, be suitable for the selected transport
     and consider temporary storage in the open air.

410. Each package shall be clearly marked with a label stating the
     Contractor's name, the destination, the name of the component and
     its identification number, the weight, and a link to the
     documentation.

411. Prior to transportation, the package units shall be visually
     inspected at the manufacturer premises and a certificate about
     proper packaging and availability of the necessary documentation
     shall be issued. Representatives of the SCK CEN shall be invited by
     the Contractor to witness the inspection.

     1.  []{#_Toc200492466 .anchor}Inspection and Installation

The Contractor shall provide all mobile vacuum pumping systems required
during installation, commissioning, and related project execution
activities. This system shall be utilised for the pumping and
conditioning of various components, including storage vessels. It is not
part of the permanent scope of supply but shall be temporarily provided
for use by the Contractor during contract execution.

412. The Contractor shall assemble and install all components (including
     all interface connections) on the SCK CEN site.

413. The Contractor and its subcontractors shall apply the local
     regulations applicable on the SCK CEN site, including safety &
     logistic rules and necessary trainings.

414. For all activities on SCK CEN site, the Contractor shall comply
     with the SCK CEN Safety and Health Plan AD2.

415. Utilities (electricity, cooling water, compressed air) except
     fluids (helium and nitrogen) will be supplied free of charge from
     start of installation to end of acceptance tests at the SCK CEN
     site. The Contractor shall provide a list of needed utilities with
     date of availability at the end of the conceptual design and
     updated at the final design

416. The existing cranes in the buildings will be made available for the
     work on site, however, the Contractor shall provide qualified
     operators.

     1.  []{#_Toc200492472 .anchor}Incoming inspection at SCK CEN site

417. Upon arrival on the SCK CEN site at Mol, at least the following
     inspections shall be performed and documented:

-   Inventory control of components.

-   Visual inspections: checking for any damage of the packages,
    examination of the surfaces and welds of the components for cracks.

-   Checking of pressure settings of all volumes after transport by the
    reading of the pressure gauges, and comparison with pressure
    measured before shipment.

-   Checking of all installed shock detectors and accelerometers.

    An incoming inspection report shall be provided by the Contractor
    and approved by SCK CEN (to be included in deliverable DD09 ) before
    starting installation.

    1.  []{#_Toc200492479 .anchor}Test after Mechanical assembly
        completion

418. The Contractor shall perform pneumatic pressure tests on all helium
     service lines to prevent corrosion or degradation of internal
     surfaces. The Contractor shall execute the test methodology in
     accordance with EN 1779, EN 12345, or equivalent industry
     standards, and shall implement safety precautions per ISO 10297

419. The Contractor shall validate the position of all interfaces during
     testing, with particular attention to the interface with the QLM.

420. The Contractor shall perform the following test and verification
     after mechanical assembly completion and document in **DD-5**.

-   Conformance of the assembly with the piping and instrumentation
    diagrams, verification of the labelling.

-   [Inspection of assembly welds shall be performed according the ASME
    standard. Moreover, all cryogenic joint welds shall be 100 %
    X-rayed.]{.mark}

-   Pressure tests of subassemblies with dry nitrogen gas. The
    Contractor shall take in charge all measures concerning safety
    precautions during these pressure tests.

-   Leak tests on subsystems (including warm lines) with recording the
    vacuum level for at least 24 h shall confirm the maximum leak rates
    specified in section

-   All electrical and wiring tests shall be performed on site after
    assembly.

-   Tests of the measuring chains and instrumentation shall be performed
    with the test of the QPLANT:CIS and the inlet/outlet signals.

-   Checking of safety components and particularly the safety valves.

421. An assembly and installation test report shall be provided by the
     Contractor and approved by SCK before starting commissioning.

     1.  []{#_Toc200492489 .anchor}Commissioning

422. The Contractor shall perform all standalone commissioning (QPLANT
     without load connected to QCELL).

423. The Contractor shall supply all helium fluid for commissioning and
     acceptance testing

     1.  []{#_Toc200492490 .anchor}Tests to be done during Standalone
         Commissioning

424. The commissioning shall start with preliminary tests to control and
     check all components at ambient temperature. The preliminary tests
     shall include at least the following tasks:

-   Controlling of the instrument circuits and settings on Human Machine
    Interface.

-   Checking of all connections.

-   Operation and checking of all utilities (cooling water, air and
    vacuum pumping circuits, electrical power supply, oil, nitrogen).

-   Conditioning of the circuits (evacuation, purging, flushing), with
    pure helium gas and calibration of the gas analysers.

425. Each individual subsystem (vacuum systems, WCS, gas storages, QRB)
     shall be commissioned during running tests:

-   Helium filling and gas management.

-   Oil removal system.

-   Individual leak test of rotating machines.

-   Validation the QPLANT:CIS operation including test of interfaces and
    test of safety functions and interlocks.

426. The contractor shall provide commissioning test reports for the
     QPLANT (and separate WCS and QRB as main subsystems). Once
     approved, the acceptance testing shall commence.

     1.  []{#_Toc200492507 .anchor}Site Acceptance testing

All tests described in 3.11 shall be conducted under Contractor
responsibility following the local site rules.

The tests on site consist of an incoming inspection after arrival on
site, inspection after positioning of the components, verification after
mechanical assembly completion, a commissioning period for the
Contractor to prepare the QPLANT for acceptance capacity tests. The
acceptance capacity tests aim at verifying the functional operation and
capacity of the WCS alone and then the functional operation and capacity
of the complete QPLANT.[]{#_Toc192762740 .anchor}

1.  General

<!-- -->

427. The Contractor shall perform acceptance capacity tests on site to
     demonstrate proper operation and verify compliance with the
     performance requirements defined in in §3.2, except for the
     cool-down and warm-up of the QCELLs, which shall be demonstrated
     once the QCELLs are connected. The Contractor shall nevertheless
     demonstrate the operation sequences for cool-down and warm-up
     during these tests.

     The Contractor shall test and validate all relevant aspects,
     including mechanical and capacity performance, safety requirements,
     and process control functionality.

428. The Contractor shall submit a draft of the test program prior to
     the start of manufacturing and implementation planning. The
     Contractor shall submit the definitive version of the acceptance
     capacity test program no later than ten (10) working days before
     the planned start of the tests.

429. The acceptance capacity tests shall be performed with the specified
     heat loads applied by heaters on the different cooling circuits to
     be representative of the operation with QPLANT connected to the
     accelerator. Dedicated test cryostat, if necessary (and to be
     provided by the Contractor), could be used. Control valves in
     relevant circuits shall also simulate appropriate pressure drops.

     1.  []{#_Toc200492517 .anchor}WCS functional tests

430. The Contractor shall perform WCS functional tests before connecting
     the WCS to the Refrigeration Cold Box. These tests shall as a
     minimum include

-   Confirmation of mechanical characteristics and component actuation
    (e.g. pneumatic valves)

-   Measuring of vibrations, noise, oil pressures and temperatures.

-   Verifying of the cooling-water system.

-   Testing of control software and interlocks during operation and
    simulated failures.

-   Measuring of main characteristics such as helium flow rates,
    pressures, temperatures.

    1.  []{#_Toc200492524 .anchor}WCS capacity tests

431. The Contractor shall perform WCS capacity tests after the
     successful completion of the functional tests. The Contractor shall
     conduct warm tests of the WCS for 48 hours in steady-state
     conditions corresponding to the maximum mass flow rate and maximum
     pressure ratio for each stage.

432. The Contractor shall continuously monitor and log the following
     parameters during the capacity tests:

-   Mass flow rates delivered by each compressor.

-   Pressures at VLP, LP, and HP levels.

-   Helium temperatures.

-   Cooling-water temperatures.

-   Hydrocarbon concentration after the oil-removal system (ORS) and the
    performance of the dryer.

-   Individual motor currents and voltages.

433. The Contractor shall estimate the uncertainties associated with all
     measurements. The Contractor shall add or subtract the estimated
     uncertainty to the measured values, depending on the direction of
     bias, before comparing the results with the acceptance criteria.

434. The Contractor shall consider the WCS capacity test successful when
     all compressors operate continuously at full charge for the entire
     48-hour test period, with acceptable cooling-water temperatures as
     defined in §3.7.3.2. The Contractor shall ensure that stability
     criteria are maintained within ± 3 % for LP and ± 2 % for HP. to.

     1.  []{#_Toc200492535 .anchor}QPLANT functional tests

435. After successful functional and capacity tests of the WCS, the
     functional tests of the QRB could start. the functional tests shall
     include at least:

-   Confirmation of mechanical characteristics.

-   Measuring of vibrations of the rotating machines.

-   Confirmation of cold absorbers operation in the QRB with a full
    regeneration cycle on each of the 80 K adsorbers and on the 20 K
    adsorber.

436. The Contractor shall verify the correct operation of the cold
     adsorbers installed in the QRB. This verification shall include a
     complete regeneration cycle performed on each of the 80 K adsorbers
     and on the 20 K adsorber. The process shall confirm proper
     adsorption functionality and regeneration effectiveness in
     accordance with the system design specifications.

437. Confirmation of control software and interlocks according to the
     functional analysis.

438. Testing of the rotating machine (cold compressors) at the design
     points (Minimal and Nominal) and at full speed.

439. Checking of the safe shut down of the QPLANT after the following
     abnormal modes simulated on the QPLANT:CIS:

     Failure of the QPLANT:CIS.

440. Loss of utilities (electrical power, cooling water, instrument air,
     vacuum loss, impurities in helium gas).\
     In case of any utility losses (electricity, compressed air, water,
     vacuum, \...), the QPLANT shall ensure the safety of the QPLANT and
     people.

441. Checking of the operation of all valves, instruments, heaters and
     rotating machines in the Refrigeration Cold Box and warm panels for
     all the defined operating modes.

     1.  []{#_Toc200492547 .anchor}QPLANT capacity tests

         The QPLANT capacity tests shall start when all the functional
         tests described above have been successfully completed and all
         specified documents have been provided.

442. The QPLANT capacity tests shall be performed for the defined steady
     state scenario (Cold stand-by; Thermal Shield stand-by; 2 K
     operation: Minimal and Nominal Design Points).

443. The capacity tests of the steady state modes will be performed
     under the environmental conditions and utilities described in §
     3.7. If conditions given are out of range during capacity tests,
     the Contractor in agreement with SCK CEN could propose a correction
     for the measurements.

444. During capacity tests, the test heaters shall operate at least the
     required values defined in the heat loads table (Table 3

445. During each capacity test, the following values shall be
     continuously monitored:

-   mass flow rates, pressures / pressure drops, temperatures at the
    supply and return lines of the QRB.

-   liquid levels of LHe thermal baths.

-   main mass flow rates, pressures, and temperatures VLP, LP HP in the
    WCS.

-   pressure in storage helium tanks.

-   cooling water temperatures and mass flow rate.

-   individual electrical motor current and voltages.

-   heat power of electrical heaters.

446. The Contractor shall estimate uncertainties on the measurements.
     The estimated uncertainty will be added or subtracted (depending on
     the measurement) to the measured values before checking the
     acceptance capacity criteria.

447. The Contractor shall perform final functional acceptance tests on
     the helium recovery system to verify flow rates, pressure
     performance, recovery time, and helium purity against the specified
     design targets.

     1.  []{#_Toc200492561 .anchor}Thermal Shield stand-by

448. The Thermal Shield stand-by capacity test shall consist of:

449. Establish the mass flow rates corresponding to Thermal Shield
     stand-by mode using the test configuration with the necessary
     by-pass valves.

450. One 24 hours Thermal Shield stand-by run without operation of the
     VLP compressors from the cold stand-by mode and followed by the
     cold stand-by mode.

451. The capacity tests of the QPLANT during Thermal Shield stand-by
     mode are deemed as passed if during the full period of the test,
     without any discontinuous operation, the achieved values verify the
     performance requirements described in **Error! Reference source not
     found.** and Table 4.

     1.  []{#_Toc200492567 .anchor}Cold stand-by

452. The cold stand-by capacity test shall consist of:

-   Filling all the liquid helium baths to their minimal operating
    levels.

-   Establish the mass flow rates corresponding to cold stand-by mode
    using the test configuration with the necessary by-pass valves.

-   Start heaters as defined in requirement RTM-0445.

-   One 48 hours cold stand-by run without any sub-atmospheric
    compressor followed by a transition to 2 K operation minimal design
    point with start of the sub-atmospheric compressors.

453. The capacity tests of the QPLANT during cold stand-by mode are
     deemed as passed if during the full period of the test, without any
     discontinuous operation, the achieved values verify the performance
     requirements described in **Error! Reference source not found.**
     and Table 4.

     1.  []{#_Toc200492574 .anchor}2 K Operation

454. The 2K operation capacity tests in stable conditions shall be
     performed for the nominal and minimal design points. It shall
     consist of:

-   Establish the mass flow rates corresponding to 2K operation (one
    test at nominal design point and one test minimal design point)
    using the test configuration with the necessary by-pass valves and
    heaters.

-   Start heaters as defined in requirement RTM-0445

-   One 48 hours 2K operation run at nominal design point and one 48
    hours 2K operation run at minimal design point, both with VLP
    compressors operating in the condition defined in **Error! Reference
    source not found.**.

-   During each test, the VLP bath pressure stability shall be better
    than +/- 0.3 mbar.

455. The 2K operation capacity tests are deemed as passed if during all
     2 K operation tests, without any discontinuous operation, the
     achieved values verify the performance requirements described in
     **Error! Reference source not found.** and Table 4.

     1.  []{#_Toc200492581 .anchor}QPLANT transition tests

The liquefaction rate plus the static heat load on the cavities is to be
tested.

456. Test of the liquefaction rate at the end of cool-down: the
     liquefaction rate shall be at least 125 Liters per hours to cope
     with the filling requirements. With a static heat load of 560 watts
     applied on helium bath (at 4.5 K), the Contractor shall demonstrate
     the liquefaction rate which shall be kept for at least half an hour
     to validate the test.

457. Test of the pumping rate of the cryomodule volumes: the Contractor
     shall demonstrate using the 2 K helium bath that the pumping of the
     2 K helium cryomodule volumes (2900 litres) from 1.3 bars to 26
     mbars could be performed in maximum 24 hours, with static heat load
     of 560 watts applied.

458. Test of stability during transitions between the nominal and the
     minimal 2 K operation design points: The test of transition between
     the 2 K operation design points shall be performed with at least
     two cycles. It shall consist of:

     Two operation cycles from minimal design point to nominal design
     point and being back to minimal design point, with operation
     stabilized for 2 hours at each level of heat loads. The transition
     duration from minimal to maximal heat load is lower than five
     seconds.

459. Establish the mass flow rates and heating power corresponding to 2
     K operation initially minimal design point then nominal design
     point using the test configuration with the necessary by-pass
     valves and heaters.

460. The VLP bath pressure shall be kept stable in a range of +/- 0.5
     mbar.

461. The stability of the operation during the transition between the
     minimal and maximal 2 K operation is to be demonstrated.

     1.  []{#_Ref190800689 .anchor}Spare Parts

-   In the offer, they need to give us the list of strategic spare parts
    needed for 5/10 years. And a price for the whole package. This is
    the contingent part

-   In the offer, they need to give us a pricelist for all spare parts
    per element. This is not contingent part. This is only to fix the
    price (+price revision formula -\> in the main tender doc? See SSA.)

462. During Contract execution, the Contractor shall expand this list
     into a detailed breakdown, including part references, failure
     assumptions, and cost drivers. A corresponding spares inventory
     shall be defined, including shelf life and storage constraints, in
     alignment with the Reliability-Centered Maintenance (RCM) Plan.

463.  The Contractor shall maintain and provide an up-to-date internal
     inventory of all components, equipment, and services delivered as
     part of the plant. This inventory must include detailed information
     on internal applications, devices, network interfaces, and
     communication protocols used within the plant. The internal
     inventory should be updated and shared with the client whenever any
     changes or updates occur in the plant.

     In their Offer, the Applicant shall provide a detailed list of all
     recommended maintenance and capital spare parts required to support
     the first five (5) years of operation. This list shall include:

-   Identification and description of each spare part.

-   Preventive maintenance and repair recommendations.

-   Unit price.

-   Delivery lead times and any associated storage or handling
    requirements.

-   The Applicant shall pay particular attention to operationally
    critical components---such as turbines, cold compressors, and warm
    compressors---with long procurement lead times. These shall be
    exhaustively identified and justified within the spare parts
    strategy.

    In its Offer, the Applicant shall provide a top-level list of all
    Components that meet either of the following criteria:

-   a mean time between failures (MTBF) of less than ten (10) years, or

-   a projected replacement rate of two (2) or more times within a forty
    (40)-year service life.

-   This list shall focus on cost-relevant or operationally critical
    items and need not include minor components where individual
    replacement costs or impacts are negligible.

    1.  []{#_Ref201310545 .anchor}After-sales Services

        1.  []{#_Toc202536241 .anchor}Level Agreement (Option 3)

            It provides one (1) year of post-commissioning operational
            support. SCK CEN may, by mutual agreement, extend the SLA
            for one (1) additional year. The SLA expressly excludes
            integrated commissioning activities that involve end-user
            participation (e.g. Control and Interlock System (CIS)
            interfacing or operational testing performed by SCK CEN
            personnel). Such activities fall outside the Contractor's
            contractual obligations. For scope details and exclusions,
            refer to Section 2.1.

        2.  []{#_Toc202536242 .anchor}Lifetime After-sales Services
            (applicable when Option 3 is exercised)

            If SCK CEN activates Option 3 at contract award, the
            Contractor shall provide after-sales services for the full
            lifetime of the QPLANT. These services shall include, as a
            minimum:

<!-- -->

-   A helpdesk offering remote technical support on Business Days from
    07:00 to 19:00 CE(S)T, accessible by telephone, Microsoft Teams, or
    equivalent tools. The Contractor shall acknowledge each defect
    notification within twenty-four (24) hours.

-   Technical field service to intervene on-site for unforeseen issues
    requiring corrective maintenance.

-   An annual maintenance programme covering predictive and preventive
    activities across all QPLANT subsystems.

-   Comprehensive fault identification, analysis, troubleshooting, and
    general technical assistance for electrical, mechanical, controls,
    software, and firmware matters.

-   Deployment only of personnel suitably qualified and experienced for
    the relevant QPLANT systems.

    Upon receipt of a support request from SCK CEN, the Contractor
    shall:

-   Complete fault identification and establish a remediation strategy,
    including preliminary cost and time estimates (step (i)):

    -   within three (3) Business Days when on-site presence is
        unnecessary

    -   within five (5) Business Days when on-site presence is required.

-   Propose a remediation plan that minimises LINAC downtime.

-   Submit a firm quotation for the solution within three (3) Business
    Days after completing step (i). The quotation shall state:

-   a technical description of the proposed solution

-   fixed price for implementation.

-   lead time for execution.

-   Provide the solution without undue delay once SCK CEN issues a
    purchase order or written approval.

    The Contractor's offer shall include:

-   A concise description of the after-sales service organisation,
    including escalation paths and staffing overview.

-   Clear procedures for requesting support, listing all contact
    channels and their availability.

-   Pricing of after-sales services, including labour hourly rates.
    Spare parts or components required for after-sales activities shall
    be remunerated at prices not exceeding those listed under § 3.8.1.11
    "Spare Parts Supply."

    1.  []{#_Toc200492592 .anchor}Documentation

464. All project-related documents, including but not limited to the CAD
     model, shall be uploaded to the SCK Coreshare platform.

465. All documents shall follow standardized file naming conventions and
     metadata formats to ensure clear identification, version control,
     and lifecycle management.

![](media/image18.png){width="7.268055555555556in"
height="1.2243055555555555in"}

The active project runs from T0 at start of L1 to L6.

466. Throughout Contract performance the Contractor shall, at a minimum,
     deliver the documentation listed in Table 18.

467. As part of #DD04, the Contractor shall provide the necessary
     technical data and design datasheets of critical components such as
     heat exchangers, piping, rotating machines, and valve information
     with sufficient detail to allow SCK CEN to model the complete
     cryogenic system including the cryogenic plant in simulations.

468. The Contractor shall deliver a maintenance manual and lifecycle
     strategy documentation, including but not limited to:

-   Spare inventory and obsolescence plans

-   PPE, alarms, and recovery training

-   Simulation-driven scenario testing

-   OPEX estimations.

-   Maintenance checks, functional testing

-   MTBF-based planning and condition diagnostics

-   Operator commissioning and technician maintenance and replacement
    involvement

-   Real-time MTBF vs prediction curve tracking

469. The process flow diagrams, process and instrumentation diagrams and
     temperature-entropy diagrams showing all the operation modes
     (including cool down) of the QPLANT shall be subject to approval by
     SCK CEN.

470. The Contractor shall, at the Preliminary Design Review (PDR), which
     is the end of the LCP1 (Concept Design), provide 3-D CAD cut-aways
     and maintenance envelopes demonstrating safe human access to all
     QRB components and instrumentation located inside the vacuum
     vessel.

[]{#_Ref192660562 .anchor}Table 18 Documentation and Deliverables

+----+-------------------------------------------+---------+----------+
| *  | **Title / Content**                       | **      | **Due    |
| *D |                                           | Phase** | Date /   |
| el |                                           |         | Mil      |
| iv |                                           |         | estone** |
| er |                                           |         |          |
| ab |                                           |         |          |
| le |                                           |         |          |
| ID |                                           |         |          |
| ** |                                           |         |          |
+====+===========================================+=========+==========+
| 1. | Project Management Plan (execution of     | Project | SIG + 1  |
|    | project) including management dashboard,  | Man     | month    |
|    | schedule, meeting processes, doc list,    | agement |          |
|    | reporting/storage                         | (L0,    |          |
|    |                                           | L1)     |          |
+----+-------------------------------------------+---------+----------+
| 2. | Quality Assurance Plan, including         | QA/QC   | SIG + 1  |
|    | compliancy matrix, test plans (incl.      | (L1)    | month    |
|    | control system), reports, functional      |         |          |
|    | safety lifecycle, certificates mgmt.,     |         |          |
|    | NCR/CR processes                          |         |          |
+----+-------------------------------------------+---------+----------+
| 3. | Conceptual Design File: description of    | Con     | SIG + 5  |
|    | Cryoplant, PFDs/P&IDs, T--s diagrams,     | ceptual | months   |
|    | process calcs, plant layout & CAD models, | Design  |          |
|    | utility requirements                      | (L1)    |          |
+----+-------------------------------------------+---------+----------+
| 4. | Detailed Design File: final P&IDs, T--s   | D       | SIG + 9  |
|    | diagrams, calculation notes, list of      | etailed | months   |
|    | components, interface list, detailed      | Design  |          |
|    | drawings, safety report, control system   | (L2)    |          |
|    | architecture, procurement specs, spares   |         |          |
|    | list                                      |         |          |
+----+-------------------------------------------+---------+----------+
| 5. | Manufacturing & Inspection Plan (MIP):    | Cons    | SIG + 12 |
|    | test program, FAT, SAT, commissioning &   | tuction | months   |
|    | acceptance tests, fabrication & welding   | (L3)    |          |
|    | reports, certificates,                    |         |          |
|    | instrumentation/electrical documentation  |         |          |
+----+-------------------------------------------+---------+----------+
| 6. | Cryoplant Control System Dossier: draft & | C       | DD05 +   |
|    | final programs, source code (Bitbucket),  | ontrols | updates  |
|    | alarms/signals list, architecture,        | (L1,    |          |
|    | software documentation, calibration certs | L2,     |          |
+----+-------------------------------------------+---------+----------+
| 7. | Packaging & Transportation Plan           | Manufa  | Before   |
|    |                                           | cturing | shipment |
|    |                                           | (L3)    |          |
+----+-------------------------------------------+---------+----------+
| 8. | Installation File: incoming inspection,   | Insta   | Prior to |
|    | installation tests, assembly reports,     | llation | commi    |
|    | certificates, Non-Conformity handling     | Phase   | ssioning |
|    |                                           | (L4     |          |
+----+-------------------------------------------+---------+----------+
| 9. | Commissioning File: commissioning         | Commis  | 10 WD    |
|    | procedures, test reports, operator        | sioning | prior to |
|    | involvement, maintenance training,        |         | commi    |
|    | functional tests                          |         | ssioning |
+----+-------------------------------------------+---------+----------+
| 10 | Acceptance Test File: FAT & SAT reports,  | Acc     | End of   |
| .  | performance verification, acceptance      | eptance | Ac       |
|    | protocols                                 |         | ceptance |
|    |                                           |         | Tests    |
+----+-------------------------------------------+---------+----------+
| 11 | Final Documentation File: operation       | Acc     | 1 month  |
| .  | manual, maintenance plan, spare parts     | eptance | after    |
|    | plan, lifecycle strategy, final reports,  | testing | Ac       |
|    | complete doc package                      |         | ceptance |
+----+-------------------------------------------+---------+----------+
| 12 | Reliability-Centred Maintenance (RCM) &   | Li      | With     |
| .  | Lifecycle Cost Management (LCM) Plans:    | fecycle | DD12     |
|    | MTBF data, spares, OPEX, preventive       | Mgmt    |          |
|    | functional test plan                      |         |          |
+----+-------------------------------------------+---------+----------+
| 13 | CAD Models & 3D integration files         | Thr     | At each  |
| .  | (Creo/STEP/BIM), uploaded to SCK          | oughout | design   |
|    | Coreshare with metadata                   |         | m        |
|    |                                           |         | ilestone |
+----+-------------------------------------------+---------+----------+
| 14 | OEM Documentation: datasheets, manuals,   | OEM     | Along    |
| .  | certificates (COTS equipment)             | phase   | supply   |
+----+-------------------------------------------+---------+----------+
| 15 | VLAREM dossier: Noise Study               | D       |          |
| .  |                                           | etailed |          |
|    |                                           | Design  |          |
+----+-------------------------------------------+---------+----------+

: []{#_Ref211261592 .anchor}Figure 10 Software Change Management

4.  []{#_Toc196376043 .anchor}Reliability Centred Maintenance &
    Lifecycle Cost Management

<!-- -->

471. The Contractor shall provide the detailed maintenance plan for all
     the QPLANT main components to meet the reliability requirements.

472. The Contractor shall provide the detailed maintenance plan for all
     the QPLANT main components to meet the reliability requirements.

473. The Contractor shall deliver a preventive Functional Test Plan as
     part of the maintenance plan.

474. The Contractor shall provide the detailed maintenance plan for all
     the QPLANT main components to meet the reliability requirements.
     The Contractor shall also deliver a Reliability-Centered
     Maintenance (RCM) Plan, defining failure modes, MTBF,
     inspection/replacement intervals, and spares recommendations for
     each system component. Specific strategies including but not
     limited to:

-   Run to failure

-   Time-based replacement

-   Condition-based maintenance

-   Functional verification (testing)

-   Preventive Functional Test Plan RCM plan

475. The Contractor shall implement a Lifecycle Cost Management (LCM)
     strategy in alignment with a fixed-price contractual framework. The
     LCM shall support informed decision-making across the full system
     lifecycle.

476. The LCM strategy shall integrate the following cost domains as per
     ISO 15288:2023:

-   Capital Expenditure (CAPEX)

-   Operational Expenditure (OPEX)

-   Maintenance forecasting and spares planning

-   Upgrade and obsolescence strategy

-   End-of-life and disposal provisions

477. The Contractor shall ensure compliance with ISO 15686-5 (Lifecycle
     Costing), IEC 60300-3-3 (Reliability-Centred Maintenance), and ISO
     55000 (Asset Management) in the definition of the RCM and LCM
     strategy.

     *In the offer, the Applicant shall i*nclude, as part of their
     Offer, a brief dossier supporting the proposed RCM and LCM
     approach. This dossier shall include:

-   *Summary of the proposed RCM strategy (e.g. run-to-failure,
    time-based, condition-based)*

-   *MTBF values for major QPLANT and QPLANT:CIS components*

-   *Spare part strategy and indicative critical inventory items*

-   *Expected OPEX contributors (e.g. electricity, labour, (liquid
    nitrogen)*

-   *High-level process-flow & safety-integrity summary (PFD/SIL)*

    *If a modelling tool (e.g. process twin or diagnostic simulation) is
    offered, outline the expected benefits, any additional
    hardware/software (BoM) and incremental cost; if no model is
    offered, provide a brief rationale and alternative diagnostic
    approach*

<!-- -->

-   *Planned maintenance & diagnostic activities for a five-year
    horizon*

-   *A clearly labelled item "RCM & LCM implementation" in the
    fixed-price breakdown. If already included in the lump sum, the
    Offer shall state "included in lump sum -- no separate charge."*

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

6.  []{#_Toc200492642 .anchor}Schedule

Contractual performance shall proceed in phases (6.1). These phases
represent the highest-level breakdown of work packages expected for the
project. A phase will be considered as completed when all associated
deliverables (Table 18) are approved by SCK CEN. In their offer, the
Applicant shall develop the phases according to its own expertise and
experience and propose a detailed work schedule. In doing so, the
Applicant shall take into consideration the preliminary schedule in
[6.2]{.smallcaps} by including the milestones and respecting the
milestone dates provided in Table 23. The Applicant may add (to a
reasonable extent) additional milestones as they think appropriate.

1.  []{#_Toc191379864 .anchor}Contractual Phases

**Phase I - Design and Development (L1 Conceptual Design and L2 Detailed
Design)**

Activities expected to be performed in this phase shall, at least,
include:

i.  Establishing the project management baseline (Management Dashboard &
    underlying processes, Quality Assurance Program and Risk Management
    Plan) for review and approval by SCK CEN.

ii. Developing the conceptual design, verifying/ validating conformance
    with technical specifications, defining specific requirements for
    buildings and utilities and preparing/ submitting the Conceptual
    Design File for review and approval by SCK CEN.

iii. Developing the detailed design, verifying/ validating conformance
     with technical specifications, defining the list of components
     (incl. procurement specifications, manufacturing drawings), setting
     final requirements for buildings and utilities, developing plans
     and procedures for the next phases (e.g. MIP, packaging and
     transportation plan, installation plan) and preparing/ submitting
     the Detailed Design File

**Phase II -- Procurement, Assembly and Manufacturing (L3)**

i.  Activities expected to be performed in this phase shall, at least,
    include:

ii. Procurement/ manufacturing of components and services necessary for
    performing the Contract, execution/ reporting of tests and
    inspections (incl. FAT), Non-Conformity handling, preparing final
    plans and procedures for Phase III and IV and preparing/ submitting
    the Procurement and Manufacturing File for review and approval by
    SCK CEN.

**Phase III -- Installation (L4)**

Activities expected to be performed in this phase shall, at least,
include:

i.  Transportation to SCK CEN (only after manufacturing QC and FAT shall
    be approved by SCK  CEN), incoming inspections of supplies,
    installation of QPLANT, execution/ reporting of assembly tests,
    Non-Conformity handling and preparing/submitting the Installation
    File for review and approval by SCK CEN.

**Phase IV -- Commissioning and Acceptance (L5-L)**

Commissioning and Acceptance testing may not necessarily follow a strict
sequential order (as a part of the system may require successful
acceptance to initiate commissioning and vice versa). The Contractor
shall develop the phase according to its own expertise and shall at
least include the following activities:

i.  Stand-alone commissioning of the QPLANT, integrated commissioning
    with controls, non-conformity handling and preparing/ submitting the
    Commissioning File for review and approval by SCK CEN.

ii. Execution/ reporting of SAT and preparing/ submitting the Acceptance
    Test File (for review and approval by SCK CEN.

iii. Project closure and submission of the Final Report for review and
     approval by SCK CEN.

     1.  []{#_Ref192661306 .anchor}Preliminary Schedule

*"ED" = Earliest Date, "LD" = Latest Possible Date, "M" = months, "wks"
= weeks, "BD" = Business Days, "CD" = Calendar Days.*

  --------------------------------------------------------------------------------------------
  **ID**             **Description**                             **Responsible**   **Dates**
  ------------------ ------------------------------------------- ----------------- -----------
  T~O~               Contract Conclusion                         SCK CEN           ED: Q2 2026

  **Phase I -Design                                                                
  and Development**                                                                

  M11                Kick-Off meeting                            SCK CEN           T~0~ +15 BD

  M12                Management Dashboard & QAP submitted for    Contractor        
                     review/approval                                               

  M13                Risk Assessment/ Management Plan submitted  Contractor        
                     for review/approval                                           

  M14                Preliminary Information on Site             SCK CEN           M11 + 1M
                     Infrastructure delivered                                      

  M15                Deliverables associated with M12 and M13    SCK CEN           
                     approved                                                      

  M16                Conceptual Design File submitted for        Contractor        
                     review/approval                                               

  M17                Detailed Design File submitted for          Contractor        
                     review/approval                                               

  M18                Detailed Design File approved               Contractor        

  **Phase II --                                                                    
  Procurement and                                                                  
  Manufacturing**                                                                  

  M21                Manufacturing started                       Contractor        

  M22                Installation Plan submitted for             Contractor        
                     review/approval                                               

  M23                Manufacturing completed                     Contractor        

  M24                FAT approved                                SCK CEN           

  **Phase III --                                                                   
  Installation**                                                                   

  **MXX Building                                                 **SCK CEN**       **XXXX**
  ready for                                                                        
  installation**                                                                   

  **Infrastructure                                               **SCK CEN**       **XXXX**
  provided by SCK                                                                  
  CEN ready**                                                                      

  M31                Incoming Inspection Report submitted for    Contractor        
                     review/approval                                               

  M32                Installation started                        Contractor        

  M33                Installation completed                      Contractor        

  M34                Installation & Assembly Test Report         Contractor        
                     submitted for review/approval                                 

  **Phase IV --                                                                    
  Commissioning and                                                                
  Acceptance**                                                                     

  M41                Commissioning Test Report submitted for     Contractor        
                     review/approval                                               

  M42                Acceptance Capacity testing started         Contractor        

  M43                SAT Report submitted for review/approval    Contractor        

  M44                Provisional Acceptance and handover         SCK CEN           T~0~ + 34 M
  --------------------------------------------------------------------------------------------

  : []{#_Toc212194956 .anchor}Figure 13 Routing of QRB.EUR (External
  User Recovery)

2.  []{#_Toc192762835 .anchor}Hold and Witness Points

    Throughout the performance of the Contract, at least the following
    review/inspection (by SCK CEN) steps shall be implemented:

<!-- -->

i.  Hold Points

-   FAT approval in view of shipments

-   Approval Incoming Inspection Report in view of start installation

-   Approval Installation and Assembly Test Report in view of start
    commissioning

-   Approval Commissioning Test Report in view of start acceptance
    capacity testing

    i.  Witness points

-   Approval of the Conceptual Design File

-   Approval of the Detailed design File

-   Approval of the Procurement and Manufacturing File

-   Approval of the Installation File

-   Approval of the Commissioning File

-   Approval of the Acceptance Test File

-   Approval of the Final Report

    Upon receiving the Contractor's finalized project schedule and
    Manufacturing and Inspection Plan, SCK CEN reserves the right to add
    or remove HP(s)/WP(s) from those currently foreseen and will duly
    notify the Contractor of such decisions.

    SCK CEN has at its disposal a maximum of 30 Calendar Days (60
    Calendar Days when involving (an) external partner(s)) to complete
    all formalities) concerning approval of a certain Hold Points.
    Nonetheless, SCK CEN shall always aim to give feedback to the
    Contractor concerning the HPs without undue delay. The envisaged
    lead time is 10 Business Days (to be determined considering SCK
    CEN's and/or its collaboration partner's days of closure)

7.  []{#_Toc200492646 .anchor}Contract Performance

    1.  []{#_Toc191379878 .anchor}General Organization

        In accordance with article 20.1 of Addendum I, the Contractor
        shall assign a member of its staff to be responsible for the
        follow-up of the Contract (further referred to as "Project
        Manager"). The Project Manager shall be responsible for
        planning, organizing, monitoring, and controlling, and directing
        the performance of the Contract, to ensure that the Contract is
        accomplished on time, within budget, and compliant to the
        requirements laid down in the Contract.

        The Contractor shall notify SCK CEN in writing in case a
        different Project Manager is appointed. Replacement of the
        Project Manager is subject to prior written approval by SCK CEN.
        In case of replacement, the substitute shall always have a level
        of education, skills, and experience equivalent to or better
        than the original resource proposed for this role.

        At the conclusion of the Contract, SCK CEN shall designate the
        Leading Officer for the Contract and inform the Contractor. The
        Contractor shall be notified of any change in writing.

        Regarding the practical follow-up of the Contract, SCK CEN
        reserves the right to have itself represented by a third party
        of its choice, acting on its behalf (further referred to as
        "Representative(s)").

        In this respect, SCK CEN grants to the Representative(s) the
        same rights as SCK CEN have accrued under the present Contract
        and the Contractor shall give effect thereto. The Contractor
        shall grant the Representatives the same access rights (physical
        access, document access, \...) as have been contractually
        instated for SCK CEN.

        Notwithstanding the foregoing, SCK CEN will remain the sole
        principal to the Contract and therefore:

    <!-- -->

    i.  any approval/acceptance/equivalent step which has been
        contractually set, shall only be approved, respectively
        accepted, if and to the extent that SCK CEN has confirmed its
        approval, respectively acceptance, of such step in writing.

    <!-- -->

    i.  any decision to deviate from the terms and conditions as have
        been contractually agreed upon, may only be implemented after
        having obtained approval thereto from SCK CEN in writing.

    <!-- -->

    2.  []{#_Toc200492648 .anchor}Communication

        All communication, including - but not limited to - tender
        documents, offers, technical documentation, any correspondence,
        and all meetings, related to the Contract, shall be in English.

        Any information that a Party considers significant enough to
        bring to the attention of the other Party, shall be deemed
        correctly communicated if exchanged in writing (e-mail suffices)
        between the two persons in charge of the general organization of
        the Contract.

        Any contract-related request -- of technical or any other nature
        -- directed by SCK CEN to the Contractor shall be adequately
        responded to within five Business Days. If such request cannot
        be answered within this lead time, e.g. due to a technical
        question requiring additional time to be answered, the
        Contractor shall at least communicate (within this lead time)
        when SCK CEN will receive the answer.

        If the Contractor anticipates any delays or difficulties in
        meeting the schedule, planned deliveries or any other milestone
        within its offer, they must promptly notify SCK CEN.

    3.  []{#_Toc200492649 .anchor}Contract Management

        1.  []{#_Toc200492650 .anchor}Progress Dashboard

            The Contractor shall implement a digital dashboard giving
            SCK CEN a snapshot up-to-date information on the status and
            progress of the Contract. The information shall be
            continuously (at least monthly) updated with the latest
            information. The Contractor shall produce and submit monthly
            progress reports to SCK CEN at least three Business Days
            prior to the monthly progress meeting. If comments or
            revisions arise during the progress meeting, the Contractor
            shall issue an updated version five business days after the
            meeting. To this end, SCK CEN shall provide access for the
            Contractor to SCK CEN's designated document management
            system.

            After consultation with the Contractor, the key indicators
            to be included, the format, and the update frequency of the
            dashboard shall be communicated by SCK CEN to the
            Contractor. Said indicators shall, as a minimum, include the
            following:

-   A concise summary of the Contract progress

-   Updated open-action-register.

-   Work completed for the last period including encountered
    difficulties and improvement proposal.

-   Work scheduled for the next period

-   Monitoring of the schedule (delays, impact on milestones, \...),
    containing:

    -   An updated schedule of the project.

    -   A physical progress curve based on significant milestones to
        show the global physical progression on the project.

-   Updated issue register, and any other points-of-attention identified
    during the performance of the Contract

-   Updated Change register

-   Updated non-conformity register

-   Updated Risk register

    In the offer, the Applicant shall include a concise description of
    the dashboard as well as the underlying management processes. This
    description must include sufficient detail to demonstrate compliance
    with the requirements.

    1.  []{#_Toc200492651 .anchor}Meetings

        Meetings will take place at either of below locations:

-   The Contractor's premises.

-   SCK CEN: Boeretang 200, 2400 Mol, Belgium or Avenue Hermann-Debroux
    40, 1160 Brussels, Belgium.

-   Any other location mutually agreed upon by the Contractor and SCK
    CEN, such as the premises of the deliverable's component
    Contractors.

-   In audio or video conferencing.

    The Contractor shall ensure that all relevant information for these
    meeting is made available to SCK CEN at least three Business Days in
    advance including, but not limited to, meeting agenda, reports, and
    presentations. The Contractor shall draft the minutes of these
    meetings and submit them to SCK CEN for review and approval within 5
    Business Days following the meeting.

Travel expenses are paid by the party who travels.

1.  Progress Meetings

    The Contractor shall organize Progress meetings between the
    Contractor and SCK CEN at least monthly.

2.  Milestone Meetings

    Milestone Meetings shall be held at least for the following
    milestones, organized at the initiative of the Contractor:

-   Kick-Off meeting (M11)

    -   This meeting is a "face-to-face" meeting to be held SCK CEN.

-   Conceptual Design Review meeting

-   Detailed Design Review meeting

-   Installation review meeting in preparation for commissioning

-   Provisional Acceptance Meeting/Contract Performance Closure meeting.

    -   This meeting is a "face-to-face" meeting to be held at SCK CEN.

        1.  Technical Review Meetings

            Technical Review Meetings (TRM's) with the necessary
            stakeholders shall be held to define the technical baseline
            and identify any evolutions between reviews.

    1.  []{#_Toc200492655 .anchor}Risk Assessment and Risk Management
        Plan

        The Applicant shall submit a preliminary Risk Assessment as part
        of their offer. It shall contain all risks with a severity that
        are bound to compromise the successful completion of the
        Contract either in terms of schedule, budget, or technical
        requirements, irrespective of probability.

        Based on the preliminary Risk Assessment, the Applicant shall
        submit a preliminary Risk Management Plan as part of their
        offer. It shall present a top‑level view of the mitigation
        strategy that the Applicant shall implement during contract
        execution, for all the risks that have been identified as
        unacceptable.

        During contract execution, the Contractor shall detail,
        complete, and continuously maintain the Risk Assessment and
        update the Risk Management Plan accordingly. The Contractor
        shall continuously monitor, identify, and document any new risks
        that might threaten the successful completion of the Contract in
        any way. The Contractor shall duly implement the mitigation
        strategy in accordance with the Risk Management Plan.

    2.  []{#_Toc200492656 .anchor}Factory Access

        During the performance of the Contract, SCK CEN shall have
        access during normal working hours to (all) the location(s)
        where (part of) the Contract is being performed (including
        Contractor's and Subcontractors\' premises). The Contractor
        shall be notified of any site visit at least five Business Days
        in advance. Any changes to the specified location(s) shall
        require prior written approval from SCK CEN.

8.  []{#_Ref190802856 .anchor}Quality Assurance and Control

    1.  []{#_Toc200492658 .anchor}Quality Assurance

        1.  []{#_Toc200492659 .anchor}General requirements

            The Contractor shall ensure status identification of each
            deliverable and all its components throughout all stages of
            manufacturing, assembly, packaging and transportation,
            installation, and commissioning to ensure that only items
            that have passed all required quality inspections and tests
            are used and/or supplied. The Contractor shall ensure
            traceability to the required level in accordance with Good
            Industry Practices.

            A review and/or approval by SCK CEN shall never entail
            (provisional) acceptance or a release of responsibility
            vis-à-vis the Contractor in any way.

        2.  []{#_Toc200492660 .anchor}Quality Management System

            Contractors who subcontract work to a Subcontractor shall
            ensure that the Subcontractor's quality management system is
            in accordance with ISO 9001, certified by a nationally
            accredited body and applicable to the scope of work defined
            in the Contract.

            In absence of an ISO 9001 certified QMS, an equivalent
            system may be accepted after written approval from SCK CEN.
            If deemed necessary, SCK CEN may request an audit as
            foreseen in section §8.1.9.

            The Contractor shall inform SCK CEN of any change in
            certification during performance of the Contact.

        3.  []{#_Toc200492661 .anchor}Quality Assurance Program

            Prior to beginning its work, the Contractor shall submit a
            detailed Quality Assurance Program, QAP, for review and
            approval by SCK CEN demonstrating compliance with the
            requirements set out in the Contract. The Contractor shall
            adhere to the QAP and shall apply the mandatory QA/QC
            measures to each deliverable. In case a deviation is
            required from one or another condition set out in this
            Contract, such request shall be clearly stated in the QAP.

    <!-- -->

    i.  Contractors who subcontract work to a Subcontractor must respond
        appropriately to ensure that the Subcontractor complies with the
        QAP.

        In the offer, the Applicant shall include a preliminary version
        of this QAP.

        1.  []{#_Toc200492662 .anchor}Qualification of personnel

            The Contractor shall ensure that all personnel involved in
            the performance of the Contract is qualified and well
            trained to deliver results complying with SCK CEN
            requirements and specifications. Special training and
            qualifications are specifically required for personnel
            responsible for:

    <!-- -->

    i.  The Contractor shall keep records of personnel qualification and
        make them available to SCK CEN free of charge upon simple
        request.

    <!-- -->

    i.  The Contractor shall ensure that all personnel who have direct
        contact with SCK CEN can understand as well as express
        themselves fluently in English, both orally and in writing.

        1.  []{#_Toc202536276 .anchor}Document Retention and Submission
            Requirements

            The Contractor shall retain all documents created under the
            Contract for a minimum period of ten (10) years, or for the
            duration required by applicable law, whichever is longer.

            The Contractor shall ensure that all documents submitted to
            SCK CEN:

    <!-- -->

    i.  are identified by a unique document code, version number, and
        document title.

    <!-- -->

    ii. include a reference to the Contract unless the document was
        created independently of the Contract.

    iii. are version-controlled and include a change log listing the
         modifications applied in each revision.

    iv. are reviewed and approved by competent and authorized personnel
        prior to submission to SCK CEN.

    v.  are submitted in digital format, compatible with commonly
        available application software for Microsoft Windows OS and
        suitable for transmission via the internet.

    <!-- -->

    i.  The Contractor should use EPLAN for all electrical and
        masterplan-related drawings to facilitate integration of the
        deliverables into SCK CEN's existing design and facility
        documentation systems. While this is not mandatory, SCK CEN
        encourages its use to enhance compatibility with internal tools
        and infrastructure.

    <!-- -->

    ii. The Contractor should ensure that the 3D models and associated
        workflows are compatible with SCK CEN's current digital
        engineering environment, which includes PTC Windchill, PTC Creo,
        and Autodesk BIM360.

        In the offer the Applicant shall (If the Contractor's standard
        toolchain or practices differ from SCK CEN's platforms):

-   propose a suitable workflow for 3D model exchange,

-   describe how the Contractor intends to use model metadata and
    attributes, and

-   explain how the Contractor will ensure integration and
    interoperability with SCK CEN's systems throughout the project
    lifecycle.

    1.  []{#_Toc212194920 .anchor}OEM Documentation

        1.  Documentation from OEMs (COTS Equipment)

            The Contractor shall store and provide to SCK CEN all
            documentation received from the Original Equipment
            Manufacturer (OEM) related to Commercial Off-The-Shelf
            (COTS) equipment and applicable use within the QPLANT

        2.  OEM Documentation Provided by SCK CEN

            If SCK CEN provides OEM documentation to the Contractor, the
            Contractor shall store and return the documentation to SCK
            CEN as received. If the original documentation is in a
            language other than English, the Contractor shall provide an
            accurate English translation alongside the original.

            The Contractor shall version-control the documents received
            from SCK CEN. When an updated version of a document is
            received, the previous version shall be removed from
            circulation as soon as reasonably possible.

            These documents shall be made accessible to the Contractor's
            employees / Subcontractors only on a need-to-know basis, for
            the purpose of the Contract, for a limited time, for as long
            as the documents are needed.

    2.  []{#_Toc200492678 .anchor}Change Management

        Proposals for change to the project, its scope of work and/or
        previously approved deliverables, either initiated by the
        Contractor or by SCK CEN, shall be analysed and documented (in a
        "Change Request") by the Contractor and submitted for approval
        to SCK CEN.

        A Change Request shall at least contain following information:

    <!-- -->

    i.  the initiator of the change

    ii. the justification for the change

    iii. the impact of the change (on product and/or (related)
         service(s),

    iv. safety,

    v.  risks,

    vi. contract price and schedule),

    vii. the description of the change and the plan of implementation.

         The Contractor shall include the Change Request template in
         annex to the QAP.

         Only Change Requests approved by SCK CEN may and shall be
         implemented.

         A Change Request having a budgetary impact on the Contractor
         shall form the basis for a Variation Order. In such event, the
         Change Request shall be considered as approved when the
         Variation Order is issued by SCK CEN.

         The Contractor shall create and maintain a Change Register,
         accessible to SCK CEN, in which all Change Requests shall be
         logged, including at least

    <!-- -->

    i.  a unique identifier, title, date of issuance,

    <!-- -->

    viii. monetary impact,

    ix. impact on the Contract schedule, and information about the
        status of (vi) the decision (potential, pending, approved,
        withdrawn, or disputed) and (vii) the implementation.

    x.  Deviations from the specifications defined in the Contract, that
        were not explicitly authorized by SCK CEN in advance in writing,
        shall be treated as Non-Conformities.

        1.  []{#_Ref190802525 .anchor}Non-Conformity Management

            A Non-Conformity is defined as any non-compliance with, or
            deviation from, any of the requirements and/or conformity
            criteria set forth in the Contract or approved Change
            Requests.

            The Contractor shall have a process in place for managing
            Non-Conformities that arise during the performance of the
            Contract, including receiving and processing notifications
            of Non-Conformities from SCK CEN and/or third parties (such
            as its Contractors or Subcontractors).

            In case of a Non-Conformity, the Contractor may not ship, or
            shall recall at its own risk and expense, the impacted
            supply. Any steps of the Contract execution, which are
            (potentially) affected by the Non‑Conformity, shall be put
            on hold.

            The Contractor shall notify SCK CEN in writing of any such
            Non-Conformities by means of a Non-Conformity Report (NCR).
            An NCR shall be submitted to SCK CEN as soon as reasonably
            possible after a Non-Conformity is identified.

            The NCR shall cover at least the following aspects:

    <!-- -->

    i.  Detailed description of the Non-Conformity.

    <!-- -->

    xi. Identification of all potentially affected deliverables.

    xii. Identified (root) cause(s) including verification thereof.

    xiii. Proposed corrective actions including their anticipated
          effectiveness.

    xiv. Proposed reoccurrence prevention plan (if applicable).

    xv. The Contractor shall include the NCR template in annex to the
        QAP.

    xvi. The NCR shall be submitted to SCK CEN for approval. SCK CEN
         shall be entitled to reject the solution(s) proposed by the
         Contractor in case SCK CEN deems the solution not useable given
         the circumstances.

         The Contractor shall perform the necessary actions to correct
         the Non-Conformity (in accordance with the SCK CEN approved
         NCR) at its own risk and expense. Said necessary actions shall
         not only concern redoing (parts of) the manufacturing and/or
         its related processes (assembly, packaging, delivery, ...) but
         shall also entail redoing all QA/QC activities associated
         therewith. Next to that, if so, requested by SCK CEN, the
         Contractor shall moreover reimburse SCK CEN for the costs
         incurred by SCK CEN to have the FAT/SAT of the impacted items
         redone.

         The Contractor shall keep SCK CEN duly informed about the
         progress of the implementation of the actions identified in the
         NCR and, if applicable, shall provide a revised schedule
         identifying the time impact of the implementation of said
         actions; the Contractor shall minimize the consequences on the
         schedule in any case.

    <!-- -->

    i.  At the specific request of SCK CEN, to avoid repetition of
        possible recurring Non-Conformities during the execution of the
        Contract, or when imposed by the Contractor\'s quality
        management system or the QAP, the Contractor shall carry out a
        root cause analysis of the Non-Conformity. Such an analysis
        shall:

        a.  be documented and submitted for approval to SCK CEN.

        b.  include the identified Non-Conformity cause(s).

        c.  propose an action plan to minimize the probability of a
            recurrence.

    <!-- -->

    ii. For actions taking more than 1 month, the Contractor shall
        provide a regular status report describing the result of
        implementation according to the due dates in the action plan.

    iii. Performing the root cause analysis and implementing any
         preventive/corrective actions arising therefrom, shall not give
         rise to any additional compensation for the Contractor.

         Any Non-Conformities identified and reported by SCK CEN to the
         Contractor, as well as any other complaints received by the
         Contractor from SCK CEN, shall be treated as Non-Conformities
         and duly documented, investigated, and resolved according to
         the stipulations under this clause.

         Neither the implementation of the procedure on Non-Conformity
         management, nor the approval by SCK CEN of a Non-Conformity
         Report, shall waive or reduce the Contractor's responsibility,
         according to the relevant stipulations of the Contract, to
         indemnify and hold SCK CEN harmless against all losses,
         damages, and costs (e.g. due to delay on the schedule) arising
         from such Non-Conformity.[]{#_Toc160432906 .anchor}

         1.  Audits

             SCK CEN shall be entitled to carry out, or to have carried
             out by a third party on its behalf (procured at SCK CEN's
             own cost), an audit of Contractor/its Subcontractor's
             premises, equipment, procedures to assess the ability of
             Contractor/Subcontractor to comply with the requirements of
             this document and the Contract. SCK CEN may request such
             audit when at least one of the following conditions is met:

    <!-- -->

    i.  to qualify a Contractor/Subcontractor which is not ISO 9001
        certified.

    <!-- -->

    ii. to address performance issues.

        SCK CEN shall inform the Contractor in advance of the audit and
        shall take all necessary steps not to unduly interfere with the
        performance of Contractor's business operations. SCK CEN shall
        provide an audit report within two weeks of completing the
        audit. The Contractor shall respond within two weeks with an
        action plan to address the identified Non-Conformities.

    <!-- -->

    1.  []{#_Toc200492681 .anchor}Quality Control

        1.  []{#_Toc200492682 .anchor}General requirements

            The Contractor shall be fully responsible for the quality of
            the deliverables, including the quality of all components,
            materials, and services procured by the Contractor.

            The Contractor shall ensure that the Contract is performed
            in accordance with all applicable regional, national, and
            international laws, regulations and industrial codes and
            standards and Good Industry Practices.

            Additionally, to ensure compliance with the requirements
            outlined in this document, the QAP shall include at least
            the qualification and validation requirements specified in
            this document.

            The Contractor shall ensure that all components, materials,
            equipment, and/or tools used at the performance of the
            Contract are appropriately designed, constructed, installed,
            calibrated, and operated. The Contractor shall develop,
            maintain, and comply with appropriate schedules for
            adjustment, cleaning, calibration, or any other required
            maintenance. The Contractor shall maintain records of these
            activities and make them available to SCK CEN upon simple
            request and without any right for further compensation or
            payment.

            All measurement and testing instrumentation used at the
            performance of the Contract shall have the appropriate
            qualifications and shall be regularly calibrated to ensure
            appropriate accuracy and precision for the measurement at
            hand. SCK CEN reserves the right to request a measurement
            system analysis and/or proof of calibration in case of any
            doubt of appropriateness.

            The Contractor shall provide all equipment necessary to
            perform and to evaluate the tests on site. Additional test
            cryostats, valves and instrumentation for acceptance tests
            shall be delivered by the Contractor. Additionally, the
            Contractor shall describe special test facilities that will
            be used during the contract.

            The inspections, measurements, and testing activities
            described in the Contract are mandatory but comprise only
            the minimum required. These activities are not intended to
            supplant any control, measurement, examination, inspection,
            or test usually performed by the Contractor to ensure the
            quality of the product. The Contractor shall perform the
            quality control according to best practices, as generally
            recognized, as well as, as assessed based on his internal
            ability and prior experience.

            In the offer, the Applicant shall outline the quality
            control process that shall be implemented during Contract
            execution.

        2.  []{#_Toc200492683 .anchor}Manufacturing and Inspection Plan

            The Contractor shall prepare a Manufacturing and Inspection
            Plan (MIP) covering all tests and inspections from start of
            manufacturing to provisional acceptance. It shall, as a
            minimum, include test and inspection plans & procedures and
            (if on-site at SCK CEN) utilities necessary for executing
            the tests. It shall indicate the Hold Points and Witness
            Points defined in the Contract as well as any other HP/WP
            defined by SCK CEN during execution of the Contract.

            The MIP shall serve to verify that all tests and inspections
            are executed as planned and in compliance with the agreed
            HP/WP.

            A preliminary version of the MIP shall be provided during
            LCP2 in **DD-5** with the updated and unalterable version
            provided at the end of LCP5

            In the offer, the Applicant shall explain the approach to
            implementing the above MIP requirements.

        3.  []{#_Toc192782715 .anchor}Declaration of conformity with all
            requirements

            Together with the delivery, the Contractor shall submit to
            SCK CEN a Declaration of Conformity certifying that all the
            requirements have been met. Such declaration shall include
            at least the following information:

            Identification of the deliverable, including the purchase
            order reference no. and Contract reference.

            A list of approved changes, waivers, or deviations from the
            specifications.

            Such declaration shall be dated and signed by a duly
            authorized representative of the Contractor responsible for
            quality assurance as shown in the approved QAP.

    2.  []{#_Toc200492685 .anchor}Acceptance Tests

        1.  []{#_Toc192762987 .anchor}General Requirements

            The acceptance tests shall be performed according to a duly
            reviewed and SCK CEN approved Acceptance Test Program
            (FAT/SAT). The test program shall be prepared and submitted
            by the Contractor to SCK CEN for review and approval at
            least 3 months prior to the date scheduled for the tests,
            unless otherwise specified.

            The Acceptance Test(s) Program(s) shall describe:

    <!-- -->

    i.  General overview: the purpose of the tests, a comprehensive list
        of the tests to be performed, the participants to be present on
        site during the test, and a description of the communication
        strategy and logistical organization for conducting the tests.

    <!-- -->

    ii. General requirements: tools, instrumentation, and computing
        devices to be used; environmental conditions that must be in
        place; required consumables and utilities (e.g.: process gas,
        electricity, cooling water); qualifications of the personnel to
        conduct the testing.

    iii. Safety requirements which must be respected during the testing.

    iv. Parameters to be measured and their measurement accuracy, noting
        the target values, range of acceptability, on which test stage
        which parameters are measured, the measurement instruments used
        to perform the measurements, the measurement method, the
        calculation formulas (if no direct measurement is possible),
        \...

    v.  Test setups and methods, including a description of each test
        setup and the method used to establish an accurate measurement.

    vi. Reporting, including a description of how the acceptance tests
        shall be documented, what the documents shall contain and to
        what organizations these documents shall be transmitted.

    vii. The Acceptance Test(s) shall be documented in FAT/SAT reports,
         clearly documenting the results of each individual test and
         whether the deliverable has passed or failed the acceptance
         test (incl. applicable Non-Conformity reports).

         1.  []{#_Ref195080116 .anchor}Factory Acceptance Test (FAT)

             The FAT program shall consider, as a minimum, the
             requirements outlined in 3.9.1.

             SCK CEN and its representatives may witness these tests at
             the Contractor and his Subcontractor\'s sites.

             SCK CEN shall approve the results before transportation.

         2.  []{#_Toc200492688 .anchor}Site Acceptance Tests

             The SAT program shall consider, as a minimum, the
             requirements outlined in 3.11**Error! Reference source not
             found.**.

             SCK CEN and its representatives shall have access to
             participate to the tests on site.

             The SAT report shall be included in **DD-10**

         3.  []{#_Toc192765565 .anchor}Acceptance and Warranty

             **Provisional Acceptance**

             A Provisional Acceptance Certificate shall be issued by SCK
             CEN for each deliverable (together with the required
             documentation), provided that no shortcomings are
             identified during the provisional acceptance.

             The provisional acceptance shall be subject to:

    <!-- -->

    i.  the successful completion of the SAT [and]{.underline}

        (*ii*) all identified Non-Conformities (e.g. documentation
        lacking) having been duly corrected by the Contractor.

        **Warranty Period**

        The Warranty Period for the CRYOPLANT shall be three (3) years
        from the date of the issuance of the Provisional Acceptance
        Certificate. In-warranty repairs and/or replacement parts shall
        be warranted for at least one (1) year after execution, or for
        the unexpired portion of the original Warranty Period of the
        CRYOPLANT, whichever is longest. Notwithstanding the foregoing,
        the Warranty Period is suspended for the duration between formal
        notice by the Contracting Authority to the Contractor on the
        defect and resolving of said defect by the Contractor.

        If the Contractor fails to fulfil its obligations under the
        warranty, so that final acceptance cannot take place at the
        scheduled time, the Warranty Period shall be automatically
        extended, without any right to compensation for the Contractor,
        until final acceptance takes place

        **Warranty Conditions**

        During the warranty period, the Contractor shall at its own risk
        and expense remedy any outstanding issues, as well as any
        shortcomings and defects that were not visible during the
        acceptance tests.

        The Contractor's methods of solving a warranty issue shall
        always need to be approved in advance by SCK CEN. SCK CEN
        reserves the right, at its sole discretion, to not allow for
        repair and to demand replacement of a defective item.

        In case the warranty work needs to be performed at SCK CEN, the
        Contractor shall consider and comply with SCK CEN's instructions
        relating to working hours, access, \..., without being entitled
        to any additional compensation.

        The Contractor's warranty obligation shall not apply:

    <!-- -->

    i.  to normal wear and tear of the QPLANT, as well as any associated
        consumables.

    <!-- -->

    viii. to defects of which the Contractor is notified after the
          Warranty period, unless SCK CEN can demonstrate that such
          defect has arisen before the end of the Warranty period in
          which case such defect shall fall under the warranty
          obligation.

    ix. to failures or defects which the Contractor can substantiate are
        due to alteration, misapplication, inappropriate use in view of
        the conditions of use as outlined by the Contractor (if any are
        provided), and/or maintenance not carried out according to the
        Contractor's nominal conditions as set forth by the Contractor,
        lack of trained maintenance personnel (other than the
        Contractor's personnel), operation above rated capacities either
        intentional or otherwise, or physical damage caused by persons
        other than the Contractor's personnel.

        During the warranty period, the Contractor shall execute repairs
        and/or replacements without undue delay at the Contractor's risk
        and expense. SCK CEN may request warranty service during
        non-normal working hours or for services excluded from the
        warranty coverage as defined herein, provided that SCK CEN shall
        pay the reasonable overtime premium portion of the non-normal
        hours worked or the normal service charge, respectively.

        In-warranty repairs and/or replacement parts shall be warranted
        for at least one year after execution, or for the unexpired
        portion of the original warranty period of the deliverable,
        whichever is longest. Notwithstanding the foregoing, the
        warranty period is suspended for the duration between formal
        notice by SCK CEN to the Contractor on the defect and resolving
        of said defect by the Contractor.

        If the Contractor fails to fulfil its obligations under the
        warranty, so that final acceptance cannot take place at the
        scheduled time, the warranty period shall be automatically
        extended, without any right to compensation and/or remuneration
        for the Contractor, until final acceptance takes place.

        The Contractor shall keep a register of all interventions that
        the Contractor performs during the warranty period which can be
        always consulted by SCK CEN. If SCK CEN can demonstrate a trend
        of failure occurring during the warranty period, which is not
        attributable to any inappropriate use of the equipment, this
        will be considered as a deficiency, and the Contractor shall be
        liable to replace at his own risk and expense the affected item

        In addition to the above rights, SCK CEN shall be entitled to
        full compensation for all damages incurred in view of these
        outstanding issues, shortcomings, and/or defects during the
        warranty period for which the Contractor is responsible.

        The warranty as described in this section shall in no way
        constitute a restriction on the applicable Belgian statutory
        regulations on hidden defects.

    <!-- -->

    3.  []{#_Toc202536294 .anchor}Final acceptance

        Initial acceptance occurs after the successful completion of the
        Warranty Period, at the written request of the Contractor, on
        the condition that all defects, attributable to the Contractor,
        regardless of whether they have been identified in the
        Provisional Acceptance Certificate or during the Warranty
        Period, have been duly resolved by the Contractor. If the
        conditions are met, a Final Acceptance Certificate will be
        issued by SCK CEN within 10 Business Days after receipt of the
        Contractor's written request in this respect.

9.  []{#_Toc200492694 .anchor}Appendix

    1.  []{#_Ref190769672 .anchor}Cooling Power for Cool-down

During a sequential cooldown of the 50 K masses when the magnetic
shields temperatures are below 70 K, the cool down of the cavities and
couplers from the Thermal Shield temperature to 4.5 K can start.

When the cavities reach the liquid helium temperature (4.5 K Static),
the liquid filling of the helium baths can start.

1.  []{#_Toc212194936 .anchor}Simplified cooling model

![](media/image20.svg){width="5.413792650918635in"
height="3.1247397200349956in"}

2.  []{#_Toc212194937 .anchor}System Mass Summary

The QPLANT cryogenic system consists of two main cooling stages: the 50K
stage and the 2K stage. The following table provides the total mass of
each stage, including all structural and functional components.

  -----------------------------------------------------------------------
  **Material**            **2 K Stage kg          **50 K Stage kg
                          (fraction)**            (fraction)**
  ----------------------- ----------------------- -----------------------
  Stainless Steel (SS)    4 868 (0.3939)          1 007 (0.0936)

  Copper (Cu)             0 (0)                   7 597 (0.7065)

  Aluminium (Al)          0 (0)                   2 149 (0.1998)

  Nickel (Ni)             2 730 (0.2210)          0 (0)

  Niobium (Nb)            2 808 (0.2273)          0 (0)

  Titanium (Ti)           1 950 (0.1578)          0 (0)

  **Stage Totals**        **12 356 kg**           **10 753 kg**
  -----------------------------------------------------------------------

  : []{#_Toc212194974 .anchor}Table 17 Project Lifecycle Phases.

Note: These masses represent the total system mass including all
materials (stainless steel, copper, aluminium, niobium, titanium, and
nickel). The mass-weighted average specific heat and enthalpy values
shall be used for cooldown calculations.

3.  []{#_Toc212194938 .anchor}Static heat load as a function of
    temperature

  ------------------------------------------------------------------------------------------------------------------------
  Heat load ID                         Type of heat load Formula
  ------------------------------------ ----------------- -----------------------------------------------------------------
  $${HL}_{cond\ 50\ K - 2\ K}$$        Static            $$- 2.4\int_{T_{1}}^{T_{2}}{\lambda_{SS304/316 - NIST}(T)dT}$$

  $${HL}_{rad\ 50\ K - 2\ K}$$         Static            $$1.49E - 05*\left( T_{1}^{4} - T_{2}^{4} \right)$$

  $${HL}_{cond\ 293.15\ K - 50\ K}$$   Static            $$- 0.87\int_{T_{1}}^{T_{2}}{\lambda_{SS304/316 - NIST}(T)dT}$$

  $${HL}_{rad\ 293.15\ K - 50\ K}$$    Static            $$4.15E - 07*\left( T_{1}^{4} - T_{2}^{4} \right)$$
  ------------------------------------------------------------------------------------------------------------------------

  : []{#_Toc201310425 .anchor}Table 19 Pressure Equipment and Safety
  Standards

4.  []{#_Toc212194939 .anchor}Enthalpy data of metal at various
    temperatures

  -----------------------------------------------------------------------
  Temperature (K)         2K Stage Enthalpy       50K Stage Enthalpy
                          (J/kg)                  (J/kg)
  ----------------------- ----------------------- -----------------------
  1                       0.0                     0.0

  2                       0.6                     0.1

  3                       1.2                     0.2

  4                       2.2                     0.4

  6                       4.9                     0.9

  8                       9.9                     2.7

  10                      16.0                    4.9

  15                      40.3                    17.6

  20                      84.2                    46.5

  25                      159.2                   107.9

  30                      280.4                   218.5

  35                      465.4                   401.0

  40                      729.3                   670.7

  50                      1534.9                  1518.9

  60                      2685.0                  2810.3

  70                      4173.2                  4547.0

  77                      5409.5                  6017.7

  80                      5982.0                  6710.4

  90                      8073.3                  9248.1

  100                     10413.9                 12096.5

  120                     15695.1                 18566.3

  140                     21679.0                 25911.4

  160                     28262.6                 33951.3

  180                     35377.0                 42530.5

  200                     42937.0                 51512.2

  220                     50797.2                 60789.0

  240                     58829.0                 70288.9

  260                     66978.2                 79970.8

  280                     75256.0                 89822.2

  300                     83753.4                 99870.3
  -----------------------------------------------------------------------

  : []{#_Toc201310426 .anchor}Table 20 Functional Safety & Control
  Standards

2.  []{#_Toc212194940 .anchor}Control Systems

    1.  []{#_Toc212194941 .anchor}Instructions for GQRC

[]{#_Ref192251100 .anchor}Table 26 Instructions for GSHRC

+--------+-------------------------------------------------------------+
| Req.   | Specific instruction                                        |
+========+=============================================================+
| G      | Applicable. Software hardware and firmware are              |
| SHRC-1 | deliverables.                                               |
+--------+-------------------------------------------------------------+
| G      | Applicable. Final Software Architecture shall be delivered  |
| SHRC-2 | as part of **DD-4**.                                        |
+--------+-------------------------------------------------------------+
| G      | Applicable. Final System Interlock Diagram shall be         |
| SHRC-3 | delivered as part of **DD-4**.                              |
+--------+-------------------------------------------------------------+
| G      | Applicable. Final Interface Design Description shall be     |
| SHRC-4 | delivered as part of **DD-4**.                              |
+--------+-------------------------------------------------------------+
| G      | Applicable. Datasheets shall be delivered as part of        |
| SHRC-5 | **DD-8**.                                                   |
+--------+-------------------------------------------------------------+
| G      | Applicable. A Release Note shall be delivered as part of    |
| SHRC-6 | **DD-10**. And after any change after acceptance.           |
+--------+-------------------------------------------------------------+
| G      | Applicable. An Installation Instructions shall be delivered |
| SHRC-7 | as part of **DD-8**.                                        |
+--------+-------------------------------------------------------------+
| G      | Applicable. A Test Plan shall be delivered as part of       |
| SHRC-8 | **DD-4**.                                                   |
+--------+-------------------------------------------------------------+
| G      | Applicable.                                                 |
| SHRC-9 |                                                             |
+--------+-------------------------------------------------------------+
| GS     | Applicable. An Interface Test Plan shall be delivered as    |
| HRC-10 | part of **DD-4** and report shall be delivered as part of   |
|        | **DD-10**.                                                  |
+--------+-------------------------------------------------------------+
| GS     | Applicable. An Interface Simulator shall be delivered as    |
| HRC-11 | part of **DD-4**.                                           |
|        |                                                             |
|        | See paragraph Software Change Management for more details.  |
+--------+-------------------------------------------------------------+
| GS     | Applicable. A Test System Description shall be delivered as |
| HRC-12 | part of **DD-4**.                                           |
+--------+-------------------------------------------------------------+
| GS     | Applicable. An Interlock Test Plan shall be delivered as    |
| HRC-13 | part of **DD-4**.                                           |
+--------+-------------------------------------------------------------+
| GS     | Applicable. An Interlock Test Report shall be delivered as  |
| HRC-14 | part of **DD-10**.                                          |
+--------+-------------------------------------------------------------+
| GS     | Not Applicable. Not a deliverable. See paragraph Software   |
| HRC-15 | Change Management for more details.                         |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Description of the used internally used test    |
| HRC-16 | system required by applicant.                               |
+--------+-------------------------------------------------------------+
| GS     | Granting a license for background materials is applicable   |
| HRC-17 | and shall be delivered as part of **DD-11**                 |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Delivery of the background materials shall be   |
| HRC-18 | done before **DD-11**                                       |
+--------+-------------------------------------------------------------+
| GS     | Updates of Background materials are applicable up to the    |
| HRC-19 | end of the Warranty period.                                 |
+--------+-------------------------------------------------------------+
| GS     | Granting a license for foreground materials is applicable   |
| HRC-20 | and shall be delivered as part of **DD-11**                 |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Delivery of the foreground materials shall be   |
| HRC-21 | done                                                        |
+--------+-------------------------------------------------------------+
| GS     | Updates of foreground materials are applicable up to the    |
| HRC-22 | end of the Warranty period.                                 |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Restrictions on use of specific open-source     |
| HRC-23 | licenses for SW/HW Materials                                |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Restrictions on open-source licenses for        |
| HRC-24 | combined work                                               |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Inventory must be provided with each Release    |
| HRC-25 | Note                                                        |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Sublicense(s) for intended use                  |
| HRC-26 |                                                             |
+--------+-------------------------------------------------------------+
| GS     | Applicable: warranty                                        |
| HRC-27 |                                                             |
+--------+-------------------------------------------------------------+
| GS     | Applicable: Escrow                                          |
| HRC-28 |                                                             |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Updates of Escrow Materials must be promptly    |
| HRC-29 | deposited if changes occur.                                 |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Upkeep of escrow is required, and fees are paid |
| HRC-30 | by SCK CEN.                                                 |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Description of secure software development must |
| HRC-31 | be provided.                                                |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Delivery of secure software is required with no |
| HRC-32 | known exploitable vulnerabilities.                          |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Default configuration must be secure.           |
| HRC-33 |                                                             |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Description of a default configuration must be  |
| HRC-34 | provided.                                                   |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Description of vulnerability management process |
| HRC-35 | must be provided.                                           |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Description of policy for Coordinated           |
| HRC-36 | Vulnerability Disclosure must be provided.                  |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Known Vulnerabilities must be listed in Release |
| HRC-37 | Notes.                                                      |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Distribution of patches/updates to mitigate     |
| HRC-38 | Vulnerabilities is required.                                |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Description of software defects process must be |
| HRC-39 | provided.                                                   |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Known software defects must be listed in        |
| HRC-40 | Release Notes.                                              |
+--------+-------------------------------------------------------------+
| GS     | Applicable. Distribution of patches/updates to address      |
| HRC-41 | software defects is required.                               |
+--------+-------------------------------------------------------------+

: []{#_Toc201310427 .anchor}Table 21 Asset & Maintenance Management

2.  []{#_Ref212036407 .anchor}Control Architecture details

The following table expands on details as per Figure 9.

  ---------------------------------------------------------------------------------
  **No.**           **Name**               **Description**
  ----------------- ---------------------- ----------------------------------------
  **11--19: Local                          
  Engineering and                          
  Control                                  
  Stations**                               

  11                Engineering Station    A dedicated workstation for running the
                                           engineering tools in commissioning
                                           stage.

  111               Engineering Tool       A dedicated engineering software for
                                           configuring, troubleshooting, or
                                           programming the QPLANT:CIS during
                                           commissioning phase.

  12                Local Operator Station A touchscreen placed near the cryogenic
                    (HMI)                  plant for direct operator interactions,
                                           real-time control, and monitoring.

  121               QPLANT HMI             Local HMI

  13                Warm Compressor        A PLC in charge of warm compressor
                    Station PLC            processes and associated subsystems in
                                           the cryogenic plant.

  131               WCS Software           The software component or logic running
                                           on the Warm Compressor Station PLC.

  14                ColdBox PLC            A PLC handling cold-related processes
                                           (cold box, vacuum insulation, other
                                           sub-circuits) in the QPLANT.

  141               CB Software            The software controlling the cold box,
                                           vacuum insulation, \...

  143               IVAC Software          The software dedicated to insulation
                                           vacuum, or auxiliary cold systems.

  15                PN-PN Coupler          A Profinet-to-Profinet coupler device
                                           bridging two separate PN networks or
                                           segments in ICS/plant architecture.

  151               Interface Definition   The definition of the interface used for
                                           controlling and monitoring the QPLANT.

  **20--29:                                
  Aggregation and                          
  System PLCs**                            

  20                Concentrator PLC       A PLC responsible for system level
                                           control, integrating the QPLANT with the
                                           MCS Navigator and aligning consumers
                                           with production plant.

  201               QCELL_BROKER Software  A software component that mediates the
                                           QCELL consumers with the QPLANT
                                           production.

  202               Plant Control and      A software component that instructs the
                    Monitoring             QPLANT operation to align with the
                                           accelerator needs.

  204               OPC-UA Server          A server implementing OPC-UA for data
                                           exchange with MCS Navigator.

  21                QVE Local Controller   A PLC for controlling and monitoring the
                                           end valvebox.

  211               QVE Control Logic      Logic for controlling the end valvebox.

  22                QCELL_Controller       A PLC for controlling and monitoring
                                           cryogenic cells.

  221               QCELL Control Logic    A software component implementing the
                                           logic for the QCELL control.

  **30--39:                                
  Networks and                             
  Communication**                          

  30                MIT Network            Networks

  31                MIS Network            A dedicated fieldbus network for safety
                                           related communication.

  32                Local Fieldbus Network A fieldbus network in scope of
                                           Contractor for interconnecting local
                                           devices (PLCs, sensors, \...)

  33                Local Fieldbus Network A fieldbus network in scope of ICS for
                                           interconnecting local devices (PLCs,
                                           sensors, \...).

  34                QPLANT Aggregation Ntw The aggregation network serves as an
                                           intermediary between the MIT backbone
                                           and the Plant.

  **40--49:                                
  Clients**                                

  41                Zero Client            MIT backbone upper-level network.

  **50--59:                                
  Interlocks and                           
  Safety**                                 

  50                MIS Interlock System   A system responsible for global personal
                                           and machine protection.

  501               Interlock Controller   A PLC controller responsible for
                                           integrating relevant QPLANT interlocks
                                           with the MIS system.

  **70--79:                                
  Deployment and                           
  Services**                               

  70                MCS Deployment Service A deployment service for QPLANT, used to
                                           distribute or update software
                                           components.

  701               Deployment Tool        Tool used for deploying new software
                                           versions to the QPLANT:CIS.

  72                MIT Services           Global IT services like NTP,
                                           Authentication, etc.

  721               NTP Service            A network time protocol service for time
                                           synchronization across ICS or QPLANT
                                           systems.

  73                MCS Services           Control System shared services like the
                                           Navigator, Archiving etc.

  731               Archiver               A data historian or archiving service
                                           used to record historical process data
                                           for the accelerator and the QPLANT.

  **80--89:                                
  Visualization and                        
  Clients**                                

  80                Zero Client            Used for visualizing MCS Navigator, the
                                           zero client displays the user interface
                                           generated by the server. All processing,
                                           data storage, and updates occur
                                           centrally.

  **90--99: Servers                        
  and Supervisory                          
  Systems**                                

  90                Server (Cluster)       Server cluster based on KVM (for
                                           Kernel-based Virtual Machine) full
                                           virtualization solution for Linux on x86
                                           hardware.

  711               Navigator              The project wide SCADA system for
                                           controlling/monitoring the accelerator
                                           and the cryogenic processes at a higher
                                           supervisory level.

  7111              QPLANT                 A control panel or interface for the
                                           QPLANT.

  7112              QCELLPanel             A control panel or interface for a
                                           cryogenic cell.
  ---------------------------------------------------------------------------------

  : []{#_Toc201310428 .anchor}Table 22 Cleanliness And Purity

10. []{#_Toc212194943 .anchor}Applicable Documents

SCK CEN is providing the required information necessary for the
performance of the Contract as outlined in this Addendum. The level of
maturity provided is that necessary for the Applicant to provide and
offer. Within Contract execution, SCK CEN may provide updated versions
of the applicable documents listed below.

+------------------------------------------------------+---------------+
| **Document name**                                    | **Reference** |
+------------------------------------------------------+---------------+
| 1.  D2.1 Preliminary Design                          | [[SCK         |
|                                                      | CEN/817770    |
|                                                      | 62]{.mark}](h |
|                                                      | ttps://ecm.sc |
|                                                      | kcen.be/OTCS/ |
|                                                      | llisapi.dll/l |
|                                                      | ink/81777062) |
+------------------------------------------------------+---------------+
| 2.  SCK CEN Auxiliary Building                       | [SCK          |
|                                                      | CEN/89        |
|                                                      | 811518](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/89811518) |
+------------------------------------------------------+---------------+
| 3.  Safety Plan (for LCP4 onwards)                   | [SCK          |
|                                                      | CE            |
|                                                      | N/56057080](h |
|                                                      | ttps://ecm.sc |
|                                                      | kcen.be/OTCS/ |
|                                                      | llisapi.dll/l |
|                                                      | ink/56057080) |
+------------------------------------------------------+---------------+
| 4.  General Specification for Steel Piping Materials | [SCK          |
|                                                      | CEN/81        |
|                                                      | 912295](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81912295) |
+------------------------------------------------------+---------------+
| 5.  General Software and Hardware Requirements for   | SCK           |
|     Contractors                                      | CEN/55310227  |
+------------------------------------------------------+---------------+
| 6.  Requirements for Electrical Equipment Included   | [SCK          |
|     in Package Plants                                | CEN/81        |
|                                                      | 913364](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81913364) |
+------------------------------------------------------+---------------+
| 7.  EMC Guidelines                                   | [SCK          |
|                                                      | CEN/81        |
|                                                      | 913579](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/overv |
|                                                      | iew/81913579) |
+------------------------------------------------------+---------------+
| 8.  SCADA HMI Guideline                              | [SCK          |
|                                                      | CEN/53        |
|                                                      | 012565](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/53012565) |
+------------------------------------------------------+---------------+
| 9.  Technical Specification for Control Valves       | [SCK          |
|                                                      | CEN/81        |
|                                                      | 912936](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81912936) |
+------------------------------------------------------+---------------+
| 10. Technical Specification for Instruments          | [SCK          |
|                                                      | CE            |
|                                                      | N/89816164](h |
|                                                      | ttps://ecm.sc |
|                                                      | kcen.be/OTCS/ |
|                                                      | llisapi.dll/l |
|                                                      | ink/89816164) |
+------------------------------------------------------+---------------+
| 11. Painting and coating specification               | [SCK          |
|                                                      | CEN/81        |
|                                                      | 913862](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81913862) |
+------------------------------------------------------+---------------+
| 12. Technical Specification for Plate Heat           | [SCK          |
|     Exchangers                                       | CEN/81        |
|                                                      | 912893](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81912893) |
+------------------------------------------------------+---------------+
| 13.  MIT Interface Catalogue                         | [SCK          |
|                                                      | CEN/81        |
|                                                      | 912045](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81912045) |
+------------------------------------------------------+---------------+
| 14. Technical Specification for Shop Fabricated      | [SCK          |
|     Tanks                                            | CEN/81        |
|                                                      | 913369](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81913369) |
+------------------------------------------------------+---------------+
| 15.  TS Of Manual and Motor Operated Metallic Valves | [SCK          |
|                                                      | CEN/81        |
|                                                      | 912050](https |
|                                                      | ://ecm.sckcen |
|                                                      | .be/OTCS/llis |
|                                                      | api.dll/Overv |
|                                                      | iew/81912050) |
+------------------------------------------------------+---------------+
| 16. MIS Slow Interlock interface                     | SCK           |
|                                                      | CEN/48282970  |
|     (applies also to non-safety digital              |               |
|     communication)                                   |               |
+------------------------------------------------------+---------------+
| 17. Analog Signals: 4-20mA (NAMUR NE43)              |               |
+------------------------------------------------------+---------------+
| 18. MCS architecture                                 | SCK           |
|                                                      | CEN/38585071  |
+------------------------------------------------------+---------------+
| 19. MIS architecture                                 | SCK           |
|                                                      | CEN/39550252  |
+------------------------------------------------------+---------------+
| 20. MIT architecture                                 | SCK           |
|                                                      | CEN/39553304  |
+------------------------------------------------------+---------------+
| 21. MCS Interface Catalogue                          | SCK           |
|                                                      | CEN/48276492  |
+------------------------------------------------------+---------------+
| 22. Slow interlock interface document                | SCK           |
|                                                      | CEN/48282970  |
+------------------------------------------------------+---------------+
| 23. MIT Interface Catalogue                          | SCK           |
|                                                      | CEN/55564083  |
+------------------------------------------------------+---------------+
| 24. MCS Secondary Interface Catalogue: Profibus DP   | SCK           |
|                                                      | CEN/48483448  |
+------------------------------------------------------+---------------+
| 25. MCS Slow Control OPC UA Interface                | SCK           |
|                                                      | CEN/56163474  |
+------------------------------------------------------+---------------+
| 26. MCS Slow Control PROFINET Interface              | SCK           |
|                                                      | CEN/55190851  |
+------------------------------------------------------+---------------+
| 27. General Software and Hardware Requirements for   | SCK           |
|     Contractors                                      | CEN/55310227  |
+------------------------------------------------------+---------------+
| ##  {#section-1 .unnumbered}                         |               |
+------------------------------------------------------+---------------+

: []{#_Ref192752742 .anchor}Table 23 Preliminary Schedule and Main
Milestones

-   [Operational and maintenance expected needs over a defined period of
    5 years including:]{.mark}

    -   [Preventive and corrective maintenance activities, software
        updates, calibration, compliance re-certifications, and energy
        efficiency optimization. Specific assumptions apply for
        forecasted OPEX:]{.mark}

i.  [Nitrogen cost: 250€/ton]{.mark}

ii. [Electricity cost: 142 €/MWh]{.mark}

iii. [Helium inventory: 250 €/kg (annual losses to be defined the
     Applicant)]{.mark}

     ter

[^1]:
