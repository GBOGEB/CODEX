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
