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
