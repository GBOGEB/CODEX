# ADR-001: /FS Orientation, Purge Control, and Safety Populations

**Context.** Addendum II requires Grade 5.0 helium purity, Table 6 leakage limits, DN150 S-line tie-in to WCS.LP, analyzer coverage (compressor room and cold-box room), and documented reliability for removable modules. Warm spines stay welded; serviceable points need repeatable integrity.

**Decision.**
- Adopt metal gasket face-seal (/FS, VCR-compatible) joints for all serviceable warm modules; maintain welded primaries.  
- Enforce orientation policy: panel female, module male.  
- Implement DBB + eductor purge achieving ≤0.05 % residual air prior to opening.  
- Apply tamper-evident ties with scan-based remake counting.  
- Fix BD/PSV populations (BD 60 QCELL + 5 QPLANT; PSV 180 QCELL + 30 QPLANT) and setpoints (2.0/18/16/3.5/4.0/1.3/0.95 bar(a); S-line 1.3 bar(a) with ≥200 g/s to WCS.LP).

**Status.** Accepted into baseline 1.3.0 (MASTER patch §1–§10).

**Consequences.**
- P&IDs must show /FS annotation and dot notation (QRB.A/B/D/E; QINFRA.U/W/S; WCS.HP/LP/VLP; WCS.R optional).  
- Maintenance workflows must replace gaskets at every remake and update CIS via tamper seal scans.  
- QA must witness DBB purge cycles and helium leak tests.  
- PSV/BD sizing dossiers required before FAT.

**SBS mapping.**
- QRB.A/B (process return, storage headers) → welded spines, /FS at warm panels and analyzer take-offs.  
- QRB.D/E (thermal shield loops) → welded circuits; /FS on warm service and instrumentation blocks.  
- QINFRA.U/W/S (utility, warm, safety headers) → welded mains, /FS at purge/analyzer blocks and safety instrumentation.  
- WCS.HP/LP/VLP (+WCS.R) → compressor station headers; /FS at analyzer panels, measurement spools, and service tees.  
- Storages & recovery vessels → /FS on analysis pick-offs only.

**Risks.**
- Air ingress during service if purge not completed → mitigated by DBB procedure and analyzer validation.  
- Overpressure of S-line → mitigated by PSV sizing ≥200 g/s to WCS.LP, vacuum breaker at 0.95 bar(a).  
- Tamper control bypass → mitigated by serialized seals and CIS audit trail.  
- Common-mode valve failure → fail-open solenoid pilots, redundant analyzers, and periodic KPI review (DMAIC control).

**Follow-up.** Track KPIs (He loss/day, leak per joint, purge residual, PSV dossier status) quarterly; update RTM if Addendum revisions arrive.
