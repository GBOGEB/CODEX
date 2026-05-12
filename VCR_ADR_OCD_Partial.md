# ADR & OCD Partial Extract (VCR Focus)

Sources: 06_arch/ADR/ADR.md (ADR-001) and 07_ops/OCD/OCD.md.

## 1. ADR-001 Highlights
| Topic | VCR-Relevant Extract |
| --- | --- |
| ADR-001 Context | Addendum II demands Table 6 leakage limits, helium recovery to WCS.LP, analyzer coverage in compressor/cold-box rooms, and SBS dot notation for warm lines. |
| ADR-001 Decision highlights | Adopt /FS joints on warm service interfaces, enforce female infrastructure vs male modules, implement DBB purge to <=0.05% residual air, install tamper seals, and fix BD/PSV populations with 200 g/s @1.3 bar(a) routed to WCS.LP. |
| ADR-001 Consequences | Predictable maintenance surfaces, minimized helium loss, traceable gasket use, and relief sizing aligned with API 520/521 and ISO 21013-1/2. |
| ADR-001 Risks & mitigations | Air ingress mitigated via DBB purge + analyzer verification; PSV sizing misalignment mitigated via certified calcs; gasket reuse mitigated via tamper workflow. |

## 2. OCD Operational Threads
| Scenario | VCR Tie-in |
| --- | --- |
| Warm start-up | Pressurize QINFRA.U/W/S, validate analyzers GAP.WCS/GAP.QRB, confirm PSV/BD readiness. |
| Maintenance outage | Execute DBB purge, replace gasket, perform leak test, log tamper data before returning to service. |
| Emergency depressurization/LOOP | Follow Addendum event tree so S-line directs 200 g/s @300 K to WCS.LP while CIS records recovery volumes. |

## 3. Role & Requirement Alignment
| User Story | Need | Requirement Link |
| --- | --- | --- |
| US-OPS-01 | Need standard purge workflow to keep helium purity >=99.999%. | RTM.005 |
| US-MAINT-02 | Need tamper seals and logs proving new gasket installation. | RTM.002 & RTM.008 |
| US-RELIAB-03 | Need analyzer + helium loss metrics to keep KPI <=1 Nm3/day. | RTM.004 |
| US-SAFETY-04 | Need PSV/BD population and sizing data for S-line certification. | RTM.006 & RTM.007 |
| US-CONTROL-05 | Need fail-open pilots so loss of air never blocks manual isolation. | RTM.003b |

## 4. Notes
- ADR-001 Accepted status (v1.3.0) confirms /FS orientation, purge strategy, tamper control, and relief sizing baseline.
- OCD scenarios emphasize when DBB purge, analyzer validation, and S-line PSV performance must be proven in operations.
- Keep this extract synced with CIS prompts so that only VCR-relevant context is carried into training decks.
