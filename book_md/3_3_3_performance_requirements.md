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
