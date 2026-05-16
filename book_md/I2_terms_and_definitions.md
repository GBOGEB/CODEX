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
