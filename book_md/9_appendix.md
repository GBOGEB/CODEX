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
